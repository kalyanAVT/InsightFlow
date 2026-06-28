from dotenv import load_dotenv
load_dotenv()

from graph.state import AgentState
from graph.pipeline import graph


def test_pipeline():
    question = "What are the latest advances in RAG systems for enterprise search in 2026?"
    
    print(f"Starting research: {question}")
    print("-" * 60)
    
    state = AgentState(research_question=question)
    result_dict = graph.invoke(state)
    
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(result_dict.get("final_report", "No report"))
    
    print("\n" + "-" * 60)
    print("PIPELINE STATS")
    print("-" * 60)
    
    plan = result_dict.get("plan")
    if plan:
        print(f"Sub-queries: {len(plan.sub_queries)}")
        for sq in plan.sub_queries:
            print(f"  - {sq.query}")
    
    search_results = result_dict.get("search_results", [])
    print(f"\nSearch results: {len(search_results)}")
    for sr in search_results:
        print(f"  - {sr.sub_query}: {len(sr.chunks)} chunks, {len(sr.sources)} sources")
    
    rag_chunks = result_dict.get("rag_chunks", [])
    print(f"\nRAG chunks from memory: {len(rag_chunks)}")
    
    synthesis = result_dict.get("synthesis")
    if synthesis:
        print(f"\nFindings: {len(synthesis.key_findings)}")
        for f in synthesis.key_findings:
            print(f"  - {f.claim[:80]}... (confidence: {f.confidence:.2f})")
    
    critique = result_dict.get("critique")
    if critique:
        print(f"\nQuality score: {critique.quality_score:.2f}")
        print(f"Proceed: {critique.proceed}")
        if critique.gap_analysis:
            print(f"Gap analysis: {critique.gap_analysis[:200]}...")
    
    print(f"\nRetry count: {result_dict.get('retry_count', 0)}")
    print(f"Declined: {result_dict.get('declined', False)}")
    if result_dict.get("declined"):
        print(f"Decline reason: {result_dict.get('decline_reason', '')}")
    
    errors = result_dict.get("errors", [])
    print(f"\nErrors: {len(errors)}")
    for err in errors:
        print(f"  - [{err.node}] {err.error_type}: {err.message}")


if __name__ == "__main__":
    test_pipeline()