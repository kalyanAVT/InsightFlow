import os
import requests
from typing import List
from dotenv import load_dotenv

load_dotenv()

from bs4 import BeautifulSoup
from tavily import TavilyClient
from graph.state import SearchResult, Chunk, ChunkMetadata
from retrieval.chunking import chunk_text


class SearchAgent:
    """Searches the web using Tavily, scrapes pages, and chunks content."""
    
    def __init__(self):
        self.tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    def run(self, query: str) -> SearchResult:
        search_response = self.tavily.search(
            query=query,
            search_depth="basic",
            include_answer=False,
            max_results=3
        )
        
        results = search_response.get("results", [])
        all_chunks: List[Chunk] = []
        sources: List[str] = []
        
        for result in results:
            url = result.get("url")
            title = result.get("title", "Untitled")
            
            if not url:
                continue
            
            sources.append(url)
            content = self._fetch_page(url)
            if not content:
                content = result.get("content", "")
            
            chunks = chunk_text(
                text=content,
                source_url=url,
                source_title=title
            )
            # LIMIT: max 8 chunks per source to prevent explosion
            all_chunks.extend(chunks[:8])
        
        return SearchResult(
            sub_query=query,
            sources=sources,
            chunks=all_chunks
        )
    
    def _fetch_page(self, url: str) -> str:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            text = soup.get_text(separator="\n", strip=True)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return "\n".join(lines)
            
        except Exception:
            return ""