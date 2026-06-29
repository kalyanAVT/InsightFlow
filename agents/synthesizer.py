import os
import numpy as np
from typing import List
from dotenv import load_dotenv

load_dotenv()

from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from graph.state import SynthesisResult, Finding, Chunk


class SynthesizerAgent:
    """Merges search chunks into structured findings with confidence scores."""
    
    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "groq")
        model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        
        if provider == "groq":
            self.llm = ChatGroq(
                model=model,
                temperature=0.2,
                api_key=os.getenv("GROQ_API_KEY")
            )
        else:
            self.llm = ChatOpenAI(
                model=model,
                temperature=0.2,
                api_key=os.getenv("OPENAI_API_KEY")
            )
        
        self.parser = PydanticOutputParser(pydantic_object=SynthesisResult)
        self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    def _deduplicate_chunks(self, chunks: List[Chunk], threshold: float = 0.92) -> List[Chunk]:
        """Remove near-duplicate chunks based on cosine similarity."""
        if not chunks:
            return []
        
        texts = [c.text for c in chunks]
        embeddings = self.embedder.encode(texts)
        
        unique_chunks = [chunks[0]]
        unique_embeddings = [embeddings[0]]
        
        for i in range(1, len(chunks)):
            similarities = [
                np.dot(embeddings[i], emb) / (np.linalg.norm(embeddings[i]) * np.linalg.norm(emb))
                for emb in unique_embeddings
            ]
            
            if max(similarities) < threshold:
                unique_chunks.append(chunks[i])
                unique_embeddings.append(embeddings[i])
        
        return unique_chunks
    
    def run(self, research_question: str, chunks: List[Chunk]) -> SynthesisResult:
        if not chunks:
            return SynthesisResult(
                key_findings=[],
                overall_confidence=0.0,
                source_diversity_score=0.0
            )
        
        chunks = self._deduplicate_chunks(chunks)
        
        # LIMIT: max 15 chunks for context to avoid token overflow
        context_parts = []
        for chunk in chunks[:15]:
            context_parts.append(
                f"[CHUNK_ID: {chunk.chunk_id}]\nSource: {chunk.metadata.source_url}\n{chunk.text[:500]}...\n"
            )
        
        context = "\n".join(context_parts)
        
        prompt = ChatPromptTemplate.from_template("""You are a research synthesis agent.

Given a research question and text chunks from sources, produce structured findings.

{format_instructions}

Research Question: {question}

Retrieved Chunks:
{context}

Rules:
- Each finding must be a single, specific, verifiable claim
- Link each claim to CHUNK_IDs that support it
- Confidence: 0.0-1.0 based on source agreement (multiple sources = higher)
- Note contradictions explicitly
- overall_confidence: weighted average
- source_diversity_score: 0.0-1.0, penalize single-source reliance

Respond with ONLY the JSON. No extra text.""")
        
        chain = prompt | self.llm | self.parser
        
        try:
            result = chain.invoke({
                "question": research_question,
                "context": context,
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
        except Exception as e:
            return self._fallback_synthesis(chunks)
    
    def _fallback_synthesis(self, chunks: List[Chunk]) -> SynthesisResult:
        """Create basic findings if LLM parsing fails."""
        findings = []
        for chunk in chunks[:5]:
            findings.append(Finding(
                claim=chunk.text[:200] + "...",
                supporting_chunks=[chunk.chunk_id],
                confidence=0.5
            ))
        
        return SynthesisResult(
            key_findings=findings,
            overall_confidence=0.5,
            source_diversity_score=0.5
        )