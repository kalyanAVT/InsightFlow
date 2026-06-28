import asyncio
import time
from fastapi import APIRouter, HTTPException
from api.schemas import ResearchRequest, ResearchResponse, ReportResponse
from graph.state import AgentState
from graph.pipeline import graph


router = APIRouter()

# In-memory store (will add Redis in Step 3)
run_store: dict[str, dict] = {}


@router.post("/research", response_model=ResearchResponse)
async def start_research(request: ResearchRequest):
    """Start a new research run."""
    run_id = str(int(time.time() * 1000))
    
    state = AgentState(
        run_id=run_id,
        research_question=request.question
    )
    
    run_store[run_id] = {"state": state, "status": "running", "events": []}
    
    asyncio.create_task(_run_pipeline(run_id, state))
    
    return ResearchResponse(
        run_id=run_id,
        status="started",
        estimated_duration_seconds=180
    )


async def _run_pipeline(run_id: str, state: AgentState):
    """Execute the LangGraph pipeline."""
    try:
        result_dict = graph.invoke(state)
        
        # Parse back to AgentState-like dict
        run_store[run_id]["result"] = result_dict
        run_store[run_id]["status"] = "completed"
        
    except Exception as e:
        run_store[run_id]["status"] = "failed"
        run_store[run_id]["error"] = str(e)


@router.get("/status/{run_id}")
async def get_status(run_id: str):
    """Check run status."""
    if run_id not in run_store:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return {
        "run_id": run_id,
        "status": run_store[run_id]["status"]
    }


@router.get("/report/{run_id}", response_model=ReportResponse)
async def get_report(run_id: str):
    """Get the final report for a run."""
    if run_id not in run_store:
        raise HTTPException(status_code=404, detail="Run not found")
    
    entry = run_store[run_id]
    result = entry.get("result", {})
    
    if not result:
        raise HTTPException(status_code=404, detail="Run not completed yet")
    
    # Count chunks
    search_results = result.get("search_results", [])
    chunks_count = sum(len(r.get("chunks", [])) for r in search_results)
    chunks_count += len(result.get("rag_chunks", []))
    
    # Collect sources
    sources = []
    seen = set()
    for result_item in search_results:
        for chunk in result_item.get("chunks", []):
            meta = chunk.get("metadata", {})
            url = meta.get("source_url", "")
            if url and url not in seen:
                seen.add(url)
                sources.append({
                    "url": url,
                    "title": meta.get("source_title", "Source")
                })
    
    # Get quality score
    critique = result.get("critique")
    quality_score = critique.get("quality_score") if critique else None
    
    # Calculate latency
    total_latency = None
    timestamps = result.get("timestamps", {})
    if timestamps:
        try:
            start = timestamps.get("planner", {}).get("start")
            end = timestamps.get("writer", {}).get("end")
            if start and end:
                from datetime import datetime
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(end)
                total_latency = int((end_dt - start_dt).total_seconds() * 1000)
        except:
            pass
    
    return ReportResponse(
        run_id=run_id,
        question=result.get("research_question", ""),
        report_markdown=result.get("final_report", "No report generated"),
        quality_score=quality_score,
        total_latency_ms=total_latency,
        chunks_retrieved=chunks_count,
        sources=sources
    )


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "0.2.0-step2",
        "features": [
            "parallel_search",
            "memory_rag",
            "hybrid_retrieval",
            "cross_encoder_rerank",
            "critic_retry_loop",
            "citation_enforcement"
        ]
    }