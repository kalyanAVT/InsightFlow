import os
import requests
from typing import List
from bs4 import BeautifulSoup
from tavily import TavilyClient
from graph.state import SearchResult, Chunk, ChunkMetadata
from retrieval.chunking import chunk_text


class SearchAgent:
    """Searches the web using Tavily, scrapes pages, and chunks content."""
    
    def __init__(self):
        self.tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    def run(self, query: str) -> SearchResult:
        # 1. Search Tavily
        search_response = self.tavily.search(
            query=query,
            search_depth="basic",
            include_answer=False,
            max_results=3
        )
        
        results = search_response.get("results", [])
        
        all_chunks: List[Chunk] = []
        sources: List[str] = []
        
        # 2. Scrape each result and chunk
        for result in results:
            url = result.get("url")
            title = result.get("title", "Untitled")
            
            if not url:
                continue
            
            sources.append(url)
            
            # Try to fetch full page content
            content = self._fetch_page(url)
            if not content:
                # Fallback to Tavily's snippet if scraping fails
                content = result.get("content", "")
            
            # 3. Chunk the content
            chunks = chunk_text(
                text=content,
                source_url=url,
                source_title=title
            )
            all_chunks.extend(chunks)
        
        return SearchResult(
            sub_query=query,
            sources=sources,
            chunks=all_chunks
        )
    
    def _fetch_page(self, url: str) -> str:
        """Fetch and extract clean text from a URL."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0"
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator="\n", strip=True)
            
            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return "\n".join(lines)
            
        except Exception:
            return ""