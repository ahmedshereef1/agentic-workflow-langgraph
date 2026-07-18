import argparse

from config.settings import settings
from src.graph.research_graph import build_research_graph, run_research_graph


def main():
    parser = argparse.ArgumentParser(
        description="Run the research workflow from the top-level entrypoint"
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
    print(result)


if __name__ == "__main__":
    main()
