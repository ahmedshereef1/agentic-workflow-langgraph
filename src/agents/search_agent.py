from loguru import logger

from langchain_community.utilities import GoogleSerperAPIWrapper

from src.models.schemas import SearchResult


class SearchAgent:
    def __init__(self, serper_api_key: str):
        self.search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)

    def execute(self, state: dict, k: int = 4) -> dict:
        query = state.get("query")
        max_results = state.get("max_results", k)

        if not query:
            return {**state, "errors": ["Search agent error: No Query Provided"]}

        try:
            self.search.k = max_results
            raw_results = self.search.results(query=query)

            # Convert raw search result to instance of the SearchResult model
            results = [
                SearchResult(
                    title=raw.get("title", ""),
                    url=raw.get("link", ""),
                    snippet=raw.get("snippet", ""),
                )
                for raw in raw_results.get("organic", [])
            ]

            logger.info(
                f"Search agent found {len(results)} results with max results: {max_results}"
            )
            logger.info(f"Search Results: {[res.model_dump() for res in results]}")

            return {**state, "search_results": [res.model_dump() for res in results]}
        except Exception as e:
            logger.exception(f"Search agent failed: {e}")
            errors = state.get("errors", [])
            errors.append(f"Search agent error: {str(e)}")

            return {
                **state,
                "errors": errors,
                "search_results": [],
            }
