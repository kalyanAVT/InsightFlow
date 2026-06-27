from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4


class SubQuery(BaseModel):
    """A single sub-query derived from the research question."""
    query: str = Field(description="The search query text")
    intent: str = Field(description="What this query is trying to find")
    priority: int = Field(default=1, description="Priority order (1 = highest)")


class ResearchPlan(BaseModel):
    """Output of the Planner Agent."""
    sub_queries: List[SubQuery] = Field(description="List of focused search queries")
    output_format: str = Field(default="report", description="Expected report structure")
    quality_threshold: float = Field(default=0.75, description="Minimum acceptable quality score")
    domain_hints: List[str] = Field(default_factory=list, description="Inferred domains")


class ChunkMetadata(BaseModel):
    """Metadata for a text chunk."""
    source_url: str
    source_title: str = ""
    page_num: int = 0
    paragraph_idx: int = 0
    char_start: int = 0
    char_end: int = 0
    retrieval_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Chunk(BaseModel):
    """A text chunk from search or memory."""
    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    text: str
    metadata: ChunkMetadata
    score: float = 0.0  # relevance score


class SearchResult(BaseModel):
    """Output of a single Search Agent."""
    sub_query: str
    sources: List[str] = Field(default_factory=list)
    chunks: List[Chunk] = Field(default_factory=list)


class Finding(BaseModel):
    """A single finding from synthesis."""
    claim: str
    supporting_chunks: List[str] = Field(default_factory=list)  # chunk_ids
    confidence: float = 0.0
    contradictions: List[str] = Field(default_factory=list)


class SynthesisResult(BaseModel):
    """Output of the Synthesizer Agent."""
    key_findings: List[Finding] = Field(default_factory=list)
    overall_confidence: float = 0.0
    source_diversity_score: float = 0.0
    coverage_assessment: Dict[str, bool] = Field(default_factory=dict)


class AgentError(BaseModel):
    """Structured error from any node."""
    error_type: str  # LLM_TIMEOUT, TOOL_FAILURE, VALIDATION_ERROR, etc.
    node: str
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    retry_scheduled: bool = False


class AgentState(BaseModel):
    """
    The full state object that flows through the LangGraph.
    Each node reads from and writes to this state.
    """
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    research_question: str = ""
    plan: Optional[ResearchPlan] = None
    search_results: List[SearchResult] = Field(default_factory=list)
    rag_chunks: List[Chunk] = Field(default_factory=list)
    synthesis: Optional[SynthesisResult] = None
    final_report: str = ""
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    declined: bool = False
    decline_reason: str = ""
    retry_count: int = 0
    timestamps: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    token_usage: Dict[str, int] = Field(default_factory=dict)
    errors: List[AgentError] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True