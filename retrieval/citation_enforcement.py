import os
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List
from graph.state import Chunk, Finding


class CitationEnforcement:
    """
    Checks that each claim in the synthesis is actually supported by retrieved chunks.
    If max similarity < threshold, triggers decline.
    """
    
    def __init__(self):
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.threshold = float(os.getenv("CITATION_THRESHOLD", "0.50"))
    
    def check(self, findings: List[Finding], chunks: List[Chunk]) -> tuple[bool, str]:
        """
        Returns: (passed, reason)
        passed = True if all claims have sufficient evidence
        """
        if not findings or not chunks:
            return False, "No findings or no chunks available"
        
        chunk_texts = [c.text for c in chunks]
        chunk_embeddings = self.embedder.encode(chunk_texts)
        
        for finding in findings:
            claim_embedding = self.embedder.encode([finding.claim])[0]
            
            # Compute similarities to all chunks
            similarities = [
                np.dot(claim_embedding, ce) / (np.linalg.norm(claim_embedding) * np.linalg.norm(ce))
                for ce in chunk_embeddings
            ]
            
            max_sim = max(similarities) if similarities else 0.0
            
            if max_sim < self.threshold:
                return False, (
                    f"Claim '{finding.claim[:80]}...' has insufficient evidence. "
                    f"Max similarity: {max_sim:.3f}, required: {self.threshold}"
                )
        
        return True, "All claims sufficiently supported"