# app/services/search.py
import os
from typing import List, Dict, Any
from langchain.utilities import GoogleSearchAPIWrapper

class SearchService:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")

    async def search_with_google(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for content using Google Search API
        """
        search = GoogleSearchAPIWrapper(
            google_api_key=self.google_api_key,
            google_cse_id=self.google_cse_id
        )

        results = search.results(query, num_results)
        return results

    async def get_urls_from_results(self, results: List[Dict[str, Any]]) -> List[str]:
        """
        Extract URLs from search results
        """
        urls = []

        for result in results:
            if isinstance(result, dict) and "link" in result:
                urls.append(result["link"])
            elif hasattr(result, "metadata") and "source" in result.metadata:
                urls.append(result.metadata["source"])

        return urls
