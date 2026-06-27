import os
from typing import List
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from graph.state import SynthesisResult, Finding, Chunk


class SynthesizerAgent:
    """Merges search chunks into structured findings with confidence scores."""
    
    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "groq")
        model = os.getenv("LLM_MODEL", "mixtral-8x7b-32768")
        
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
    
    def run(self, research_question: str, chunks: List[Chunk]) -> SynthesisResult:
        if not chunks:
            return SynthesisResult(
                key_findings=[],
                overall_confidence=0.0,
                source_diversity_score=0.0
            )
        
        # Prepare context: chunk texts with IDs
        context_parts = []
        for chunk in chunks[:20]:  # Limit context to top 20 chunks
            context_parts.append(
                f"[CHUNK_ID: {chunk.chunk_id}]\n{chunk.text[:500]}...\n"
            )
        
        context = "\n".join(context_parts)
        
        prompt = ChatPromptTemplate.from_template("""You are a research synthesis agent.

Given a research question and a set of text chunks from web sources, produce structured findings.

For each finding:
1. Write a clear, specific claim
2. List which CHUNK_IDs support this claim
3. Assign a confidence score (0.0 to 1.0) based on source agreement
4. Note any contradictions found

Also produce:
- overall_confidence: weighted average across findings
- source_diversity_score: how spread out the sources are (0.0 to 1.0, penalize single-source reliance)

{format_instructions}

Research Question: {question}

Retrieved Chunks:
{context}

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
            # Fallback: create simple findings from chunks
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