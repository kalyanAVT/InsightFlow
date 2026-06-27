import time
from datetime import datetime
from typing import Any
from graph.state import AgentState, AgentError
from agents.planner import PlannerAgent
from agents.searcher import SearchAgent
from agents.synthesizer import SynthesizerAgent


def planner_node(state: AgentState) -> dict[str, Any]:
    """Execute the Planner Agent."""
    start_time = time.time()
    try:
        agent = PlannerAgent()
        plan = agent.run(state.research_question)
        
        return {
            "plan": plan,
            "timestamps": {
                **state.timestamps,
                "planner": {
                    "start": datetime.utcfromtimestamp(start_time).isoformat(),
                    "end": datetime.utcnow().isoformat()
                }
            }
        }
    except Exception as e:
        return {
            "errors": [
                *state.errors,
                AgentError(
                    error_type="LLM_TIMEOUT" if "timeout" in str(e).lower() else "VALIDATION_ERROR",
                    node="planner",
                    message=str(e)
                )
            ]
        }


def search_node(state: AgentState) -> dict[str, Any]:
    """Execute a single Search Agent (Step 1: uses first sub-query only)."""
    start_time = time.time()
    
    if not state.plan or not state.plan.sub_queries:
        return {
            "errors": [
                *state.errors,
                AgentError(
                    error_type="VALIDATION_ERROR",
                    node="searcher",
                    message="No plan or sub-queries available"
                )
            ]
        }
    
    sub_query = state.plan.sub_queries[0]
    
    try:
        agent = SearchAgent()
        result = agent.run(sub_query.query)
        
        return {
            "search_results": [result],
            "timestamps": {
                **state.timestamps,
                "searcher": {
                    "start": datetime.utcfromtimestamp(start_time).isoformat(),
                    "end": datetime.utcnow().isoformat()
                }
            }
        }
    except Exception as e:
        return {
            "errors": [
                *state.errors,
                AgentError(
                    error_type="TOOL_FAILURE" if "api" in str(e).lower() else "UNEXPECTED",
                    node="searcher",
                    message=str(e)
                )
            ]
        }


def synthesizer_node(state: AgentState) -> dict[str, Any]:
    """Execute the Synthesizer Agent."""
    start_time = time.time()
    
    all_chunks = []
    for result in state.search_results:
        all_chunks.extend(result.chunks)
    
    try:
        agent = SynthesizerAgent()
        synthesis = agent.run(
            research_question=state.research_question,
            chunks=all_chunks
        )
        
        return {
            "synthesis": synthesis,
            "timestamps": {
                **state.timestamps,
                "synthesizer": {
                    "start": datetime.utcfromtimestamp(start_time).isoformat(),
                    "end": datetime.utcnow().isoformat()
                }
            }
        }
    except Exception as e:
        return {
            "errors": [
                *state.errors,
                AgentError(
                    error_type="LLM_TIMEOUT" if "timeout" in str(e).lower() else "UNEXPECTED",
                    node="synthesizer",
                    message=str(e)
                )
            ]
        }


def writer_node(state: AgentState) -> dict[str, Any]:
    """Simple writer for Step 1. Formats synthesis into Markdown."""
    if not state.synthesis:
        return {"final_report": "# Error\nNo synthesis available."}
    
    lines = [
        f"# Research: {state.research_question}",
        "",
        "## Key Findings",
        ""
    ]
    
    for i, finding in enumerate(state.synthesis.key_findings, 1):
        lines.append(f"### Finding {i}: {finding.claim}")
        lines.append(f"- Confidence: {finding.confidence:.2f}")
        if finding.supporting_chunks:
            lines.append(f"- Supported by {len(finding.supporting_chunks)} chunks")
        lines.append("")
    
    lines.extend(["## Sources", ""])
    
    seen_urls = set()
    for result in state.search_results:
        for chunk in result.chunks:
            if chunk.metadata.source_url not in seen_urls:
                seen_urls.add(chunk.metadata.source_url)
                lines.append(f"- [{chunk.metadata.source_title or 'Source'}]({chunk.metadata.source_url})")
    
    return {"final_report": "\n".join(lines)}