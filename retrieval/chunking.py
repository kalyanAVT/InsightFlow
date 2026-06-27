import re
from typing import List
from graph.state import Chunk, ChunkMetadata


def chunk_text(
    text: str,
    source_url: str,
    source_title: str = "",
    chunk_size: int = 700,
    chunk_overlap: int = 100
) -> List[Chunk]:
    """
    Split text into chunks preserving semantic boundaries.
    Priority: paragraphs -> sentences -> words
    """
    # Split into paragraphs first
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    
    chunks: List[Chunk] = []
    current_chunk = []
    current_size = 0
    chunk_idx = 0
    
    def estimate_tokens(text: str) -> int:
        """Rough token estimate: ~4 chars per token."""
        return len(text) // 4
    
    def flush_chunk():
        nonlocal current_chunk, current_size, chunk_idx
        if not current_chunk:
            return
        
        chunk_text_str = "\n\n".join(current_chunk)
        chunks.append(Chunk(
            text=chunk_text_str,
            metadata=ChunkMetadata(
                source_url=source_url,
                source_title=source_title,
                paragraph_idx=chunk_idx
            )
        ))
        chunk_idx += 1
        
        # Keep overlap for next chunk
        overlap_text = []
        overlap_size = 0
        for para in reversed(current_chunk):
            para_tokens = estimate_tokens(para)
            if overlap_size + para_tokens <= chunk_overlap:
                overlap_text.insert(0, para)
                overlap_size += para_tokens
            else:
                break
        
        current_chunk = overlap_text
        current_size = overlap_size
    
    for para in paragraphs:
        para_tokens = estimate_tokens(para)
        
        # If single paragraph exceeds chunk size, split by sentences
        if para_tokens > chunk_size:
            sentences = re.split(r'(?<=[.!?])\s+', para)
            for sentence in sentences:
                sent_tokens = estimate_tokens(sentence)
                if current_size + sent_tokens > chunk_size and current_chunk:
                    flush_chunk()
                current_chunk.append(sentence)
                current_size += sent_tokens
        else:
            if current_size + para_tokens > chunk_size and current_chunk:
                flush_chunk()
            current_chunk.append(para)
            current_size += para_tokens
    
    # Flush remaining
    flush_chunk()
    
    return chunks