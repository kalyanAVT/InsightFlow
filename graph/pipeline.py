from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.nodes import planner_node, search_node, synthesizer_node, writer_node


def build_graph():
    """
    Build the Step 1 linear pipeline.
    Planner -> Search -> Synthesizer -> Writer -> END
    """
    # Initialize the graph with our state type
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("searcher", search_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("writer", writer_node)
    
    # Add edges (linear flow)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "searcher")
    workflow.add_edge("searcher", "synthesizer")
    workflow.add_edge("synthesizer", "writer")
    workflow.add_edge("writer", END)
    
    # Compile the graph
    return workflow.compile()


# Global instance
graph = build_graph()