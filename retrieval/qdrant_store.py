import os
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


class QdrantStore:
    """
    Qdrant Cloud vector store wrapper.
    Connects to Qdrant free tier (no Docker needed).
    """
    
    def __init__(self):
        self.url = os.getenv("QDRANT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")
        
        if not self.url or not self.api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in .env")
        
        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key,
            timeout=30
        )
        
        self.collection_name = "research_chunks"
        self.vector_size = 384  # all-MiniLM-L6-v2 dimensions
    
    def ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            print(f"Created collection: {self.collection_name}")
        else:
            print(f"Collection {self.collection_name} already exists")
    
    def store_chunks(self, chunks: List, embeddings: List[List[float]], run_id: str):
        """
        Store chunks with embeddings.
        chunks: list of Chunk objects
        embeddings: list of embedding vectors
        """
        self.ensure_collection()
        
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            points.append(PointStruct(
                id=chunk.chunk_id,
                vector=embedding,
                payload={
                    "text": chunk.text,
                    "source_url": chunk.metadata.source_url,
                    "source_title": chunk.metadata.source_title,
                    "page_num": chunk.metadata.page_num,
                    "paragraph_idx": chunk.metadata.paragraph_idx,
                    "run_id": run_id,
                    "retrieval_count": 0
                }
            ))
        
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
    
    def search(self, query_embedding: List[float], limit: int = 8) -> List[dict]:
        """Search for similar chunks."""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit
            )
            return results
        except Exception as e:
            print(f"Qdrant search error: {e}")
            return []
    
    def get_collection_info(self) -> dict:
        """Get info about the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.config.params.vectors.size,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            return {"error": str(e)}


# Singleton instance
qdrant_store = QdrantStore()