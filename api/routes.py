import asyncio
import time
from fastapi import APIRouter, HTTPException
from api.schemas import ResearchRequest, ResearchResponse, ReportResponse
from graph.state import AgentState
from graph.pipeline import graph


router = APIRouter()

# In-memory store for Step 1 (will move to Redis in Step 2)
run_store: dict[str, AgentState] = {}


@router.post("/research", response_model=ResearchResponse)
async def start_research(request: ResearchRequest):
    """Start a new research run."""
    run_id = str(time.time())  # Simple ID for now, use uuid7 in production
    
    # Create initial state
    state = AgentState(
        run_id=run_id,
        research_question=request.question
    )
    
    # Store initial state
    run_store[run_id] = state
    
    # Run graph in background (Step 1: simple await, no true background task yet)
    asyncio.create_task(_run_pipeline(run_id, state))
    
    return ResearchResponse(
        run_id=run_id,
        status="started",
        estimated_duration_seconds=120
    )


async def _run_pipeline(run_id: str, state: AgentState):
    """Execute the LangGraph pipeline."""
    try:
        # Run the graph
        final_state = graph.invoke(state)
        
        # Store result
        run_store[run_id] = final_state
    except Exception as e:
        # Store error state
        state.errors.append({
            "error_type": "UNEXPECTED",
            "node": "pipeline",
            "message": str(e)
        })
        run_store[run_id] = state


@router.get("/report/{run_id}", response_model=ReportResponse)
async def get_report(run_id: str):
    """Get the final report for a run."""
    if run_id not in run_store:
        raise HTTPException(status_code=404, detail="Run not found")
    
    state = run_store[run_id]
    
    # Count chunks
    chunks_count = sum(len(r.chunks) for r in state.search_results)
    
    # Collect sources
    sources = []
    seen = set()
    for result in state.search_results:
        for chunk in result.chunks:
            if chunk.metadata.source_url not in seen:
                seen.add(chunk.metadata.source_url)
                sources.append({
                    "url": chunk.metadata.source_url,
                    "title": chunk.metadata.source_title
                })
    
    # Calculate latency if timestamps exist
    total_latency = None
    if state.timestamps:
        try:
            start = state.timestamps.get("planner", {}).get("start")
            end = state.timestamps.get("writer", {}).get("end")
            if start and end:
                from datetime import datetime
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(end)
                total_latency = int((end_dt - start_dt).total_seconds() * 1000)
        except:
            pass
    
    return ReportResponse(
        run_id=run_id,
        question=state.research_question,
        report_markdown=state.final_report,
        quality_score=state.synthesis.overall_confidence if state.synthesis else None,
        total_latency_ms=total_latency,
        chunks_retrieved=chunks_count,
        sources=sources
    )


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "ok",
        "qdrant": "not_checked",  # Will add in Step 2
        "version": "0.1.0-step1"
    }