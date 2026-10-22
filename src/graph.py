from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.config import MAX_REJECTIONS
from src.agents import (
    western_research_agent,
    eastern_research_agent,
    technical_agent,
    devils_advocate_agent,
    debate_synthesizer,
    digital_twin_agent
)

from src.logger_config import logger

def should_continue_debate(state: AgentState) -> str:
    is_satisfied = state.get("is_satisfied", False)
    rejection_count = state.get("rejection_count", 0)

    if is_satisfied:
        logger.info("Digital Twin SATISFIED. Ending workflow.")
        return "end"

    if rejection_count >= MAX_REJECTIONS:
        logger.warning(f"Max rejections ({MAX_REJECTIONS}) reached. Forcing end.")
        return "end"

    logger.info(f"Digital Twin NOT SATISFIED (Round {rejection_count}). Re-running research...")
    return "continue"

def create_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("western_research", western_research_agent)
    workflow.add_node("eastern_research", eastern_research_agent)
    workflow.add_node("technical", technical_agent)
    workflow.add_node("devils_advocate", devils_advocate_agent)
    workflow.add_node("synthesizer", debate_synthesizer)
    workflow.add_node("digital_twin", digital_twin_agent)

    # 1. Phase 1: Parallel Global Search
    workflow.set_entry_point("western_research")
    workflow.add_edge("__start__", "western_research")
    workflow.add_edge("__start__", "eastern_research")

    # 2. Phase 2: Parallel Deep Analysis (Wait for both research to finish)
    workflow.add_edge("western_research", "technical")
    workflow.add_edge("eastern_research", "technical")
    workflow.add_edge("western_research", "devils_advocate")
    workflow.add_edge("eastern_research", "devils_advocate")

    # 3. Phase 3: Synthesis
    workflow.add_edge("technical", "synthesizer")
    workflow.add_edge("devils_advocate", "synthesizer")

    # 4. Phase 4: Final Verdict
    workflow.add_edge("synthesizer", "digital_twin")

    # Conditional Loop
    workflow.add_conditional_edges(
        "digital_twin",
        should_continue_debate,
        {
            "end": END,
            "continue": "western_research"
        }
    )

    return workflow.compile()
