import json

from loguru import logger

from src.graph.research_graph import build_research_graph
from config.settings import settings


def lambda_handler(event, context):
    # log environemnt variable (masked for security)
    logger.info("SERPER_API_KEY present: %s", bool(settings.SERPER_API_KEY))
    logger.info("CLAUDE_BASE_URL present: %s", bool(settings.CLAUDE_BASE_URL))
    logger.info("CLAUDE_API_KEY present: %s", bool(settings.CLAUDE_API_KEY_ANTI))

    # Extract parameters from event with default
    query = event.get("query", "What are the benefits of using AWS Cloud Services?")
    confidence_threshold = event.get(
        "confidence_threshold", settings.CONFIDENCE_THRESHOLD
    )
    max_retries = event.get("max_retries", settings.MAX_RETRIES)
    add_max_results = event.get("add_max_results", settings.ADD_MAX_RESULTS)

    # Validate parameters
    if not 0 <= confidence_threshold <= 1:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"error": "Confidence threshold must be between 0 and 1"}
            ),
        }
    if max_retries < 0:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Max retries must be non-negative number"}),
        }
    if add_max_results < 1:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"error": "Additional max results must be positive number"}
            ),
        }

    # Build the research graph
    graph = build_research_graph(
        serper_api_key=settings.SERPER_API_KEY,
        claude_api_key=settings.CLAUDE_API_KEY_ANTI,
        confidence_threshold=confidence_threshold,
        max_retries=max_retries,
        add_max_results=add_max_results,
    )

    # Run the graph
    result = graph.invoke(
        {
            "query": query,
            "search_results": [],
            "summarized_content": "",
            "fact_checked_results": {},
            "final_report": "",
            "errors": [],
            "fact_check_attempts": 0,
            "summarization_attempts": 0,
            "max_results": 4,
            "search_retries": 0,
        }
    )

    return {
        "statusCode": 200,
        "body": {
            "final_report": result.get("final_report", ""),
            "errors": result.get("errors", []),
        },
    }
