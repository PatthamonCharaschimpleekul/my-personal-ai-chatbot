from typing import List, Dict, TypedDict, Annotated
import operator

class AgentState(TypedDict):
    user_query: str
    persona_context: str
    # แยก Research เป็น 2 ฝั่ง
    western_research_output: str
    eastern_research_output: str

    technical_output: str
    devils_advocate_output: str
    debate_matrix: str
    twin_feedback: str
    rejection_count: Annotated[int, operator.add]
    is_satisfied: bool
    final_verdict: str
