# test_pipeline.py
import asyncio
from dotenv import load_dotenv
load_dotenv()

from graph.state import AgentState


async def test_pipeline():
    """Run a full research pipeline and print the report."""
    
    question = "What are the latest advances in RAG systems for enterprise search in 2026?"
    
    print(f"Starting research: {question}")
    print("-" * 60)
    
    # Create initial state
    state = AgentState(research_question=question)
    
    # Import here to avoid circular issues
    from graph.pipeline import graph
    
    # Run the graph - returns a dict
    result_dict = graph.invoke(state)
    
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(result_dict.get("final_report", "No report generated"))
    
    print("\n" + "-" * 60)
    errors = result_dict.get("errors", [])
    print(f"Errors: {len(errors)}")
    for err in errors:
        print(f"  - [{err.node}] {err.error_type}: {err.message}")
    
    print(f"\nTimestamps: {result_dict.get('timestamps', {})}")
    
    # Show plan if available
    plan = result_dict.get("plan")
    if plan:
        print(f"\nPlan generated: {len(plan.sub_queries)} sub-queries")
        for sq in plan.sub_queries:
            print(f"  - {sq.query}")


if __name__ == "__main__":
    asyncio.run(test_pipeline())