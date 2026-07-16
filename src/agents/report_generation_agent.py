from loguru import logger

from src.utils.chain_builder import ChainBuilder
from src.models.schemas import FinalReport, ResearchState
from src.utils.prompt_templates import PromptTemplates
from src.utils.error_handler import ErrorHandler


class ReportGenerationAgent:
    def __init__(self, llm):
        self.chain_builder = ChainBuilder(llm)

    def execute(self, state: ResearchState) -> ResearchState:
        summary = state.get("summarized_content")
        query = state["query"]

        if not summary or not query:
            return {
                **state,
                "errors": ["Report generation agent error: Missing required content"],
            }

        chain = self.chain_builder.build(
            prompt_template=PromptTemplates.report_generation_prompt(),
            input_vars=["query", "summary"],
            model=FinalReport,
        )

        try:
            final_report = chain.invoke({"query": query, "summary": summary})
            final_report = final_report.model_dump()

            logger.info("===== Final Report ======")
            logger.info(final_report["report"])
            logger.info("=========================")

            return {**state, "final_report": final_report["report"]}

        except Exception as e:
            logger.exception(f"Report generation agent failed: {e}")

            return ErrorHandler.add_error(
                state,
                f"Report generation agent error: {str(e)}",
            )
