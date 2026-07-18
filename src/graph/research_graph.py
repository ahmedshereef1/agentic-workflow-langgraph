import argparse
from loguru import logger
from langsmith import traceable

from langchain_aws import ChatBedrock
from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, StateGraph

from config.settings import settings

from src.agents.search_agent import SearchAgent
from src.agents.summarize_agent import SummarizeAgent
from src.agents.fact_check_agent import FactCheckAgent
from src.agents.report_generation_agent import ReportGenerationAgent
from src.agents.stop_workflow_agent import StopWorkflowAgent
from src.models.schemas import ResearchState


def build_research_graph(
    serper_api_key: str,
    claude_api_key: str,
    confidence_threshold: float,
    max_retries: int,
    add_max_results: int,
):
    # Initialize different models for Summarization and Fact-Checking agents
    fact_check_llm = ChatAnthropic(
        model_name=settings.CLAUDE_MODEL_ID,
        api_key=claude_api_key,
        base_url=settings.CLAUDE_BASE_URL,
    )

    summarize_llm = ChatBedrock(
        model="amazon.nova-lite-v1:0",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        temperature=0,
    )

    # Initialize agents
    search_agent = SearchAgent(serper_api_key=serper_api_key)
    summarize_agent = SummarizeAgent(summarize_llm)
    fact_check_agent = FactCheckAgent(
        llm=fact_check_llm,
        confidence_threshold=confidence_threshold,
        max_retries=max_retries,
        add_max_results=add_max_results,
    )
    report_generation_agent = ReportGenerationAgent(summarize_llm)
    stop_workflow_agent = StopWorkflowAgent()

    # Define graph state
    builder = StateGraph(ResearchState)

    # Set entry point
    builder.set_entry_point("Search")

    # Add nodes
    builder.add_node("Search", search_agent.execute)
    builder.add_node("Summarize", summarize_agent.execute)
    builder.add_node("Fact Check", fact_check_agent.execute)
    builder.add_node("Report", report_generation_agent.execute)
    builder.add_node("Stop Workflow", stop_workflow_agent.execute)

    def on_search_complete(state: ResearchState) -> str:
        return "Stop Workflow" if state.get("errors") else "Summarize"

    def on_summarization_complete(state: ResearchState) -> str:
        return "Stop Workflow" if state.get("errors") else "Fact Check"

    def on_fact_check_complete(state: ResearchState) -> str:
        fact_check_result = state.get("fact_checked_results", {})
        confidence_score = fact_check_result.get("confidence_score", 1.0)
        count = state.get("search_retries", 0)

        if state.get("errors"):
            return "Stop Workflow"

        if confidence_score < confidence_threshold:
            if count >= max_retries:
                logger.info(
                    f"Maximum retry attempts ({max_retries}) reached. Stopping workflow."
                )
                return "Stop Workflow"
            return "Search"

        return "Report"

    def on_report_complete(state: ResearchState) -> str:
        return "Stop Workflow" if state.get("errors") else END

    def on_stop_workflow(_state: ResearchState) -> str:
        return END

    builder.add_conditional_edges(
        "Search",
        on_search_complete,
        {
            "Stop Workflow": "Stop Workflow",
            "Summarize": "Summarize",
        },
    )

    builder.add_conditional_edges(
        "Summarize",
        on_summarization_complete,
        {
            "Stop Workflow": "Stop Workflow",
            "Fact Check": "Fact Check",
        },
    )

    builder.add_conditional_edges(
        "Fact Check",
        on_fact_check_complete,
        {
            "Stop Workflow": "Stop Workflow",
            "Report": "Report",
            "Search": "Search",
        },
    )

    builder.add_conditional_edges(
        "Report",
        on_report_complete,
        {
            "Stop Workflow": "Stop Workflow",
            END: END,
        },
    )

    builder.add_conditional_edges("Stop Workflow", on_stop_workflow, {END: END})

    return builder.compile()


@traceable(name="research_graph_run")
def run_research_graph(graph, query: str):
    return graph.invoke({"query": query})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run research graph with custom parameters"
    )
    parser.add_argument(
        "--query",
        type=str,
        default="What are the benefits of using AWS Cloud Services?",
        help="Research query",
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=settings.CONFIDENCE_THRESHOLD,
        help="Confidence score threshold (0-1)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=settings.MAX_RETRIES,
        help="Maximum number of retries",
    )
    parser.add_argument(
        "--add-max-results",
        type=int,
        default=settings.ADD_MAX_RESULTS,
        help="Number of additional results per retry",
    )

    args = parser.parse_args()

    graph = build_research_graph(
        serper_api_key=settings.SERPER_API_KEY,
        claude_api_key=settings.CLAUDE_API_KEY_ANTI,
        confidence_threshold=args.confidence_threshold,
        max_retries=args.max_retries,
        add_max_results=args.add_max_results,
    )

    result = run_research_graph(graph, args.query)
