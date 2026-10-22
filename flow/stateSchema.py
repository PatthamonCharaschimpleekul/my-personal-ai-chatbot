from typing import List, Dict, TypedDict, Annotated
import operator

class AgentState(TypedDict):
    user_query: str
    persona_context: str          # Context จาก Memory DB (Chat 1)
    research_output: str          # ผลลัพธ์จาก Research Agent
    technical_output: str         # ผลลัพธ์จาก Technical Agent
    devils_advocate_output: str   # ผลลัพธ์จาก Devil's Advocate
    debate_matrix: str            # สรุปข้อดี-ข้อเสียรวม
    twin_feedback: str            # Feedback กรณี Digital Twin สั่งปฏิเสธ
    rejection_count: int          # กัน Loop บานปลาย (Max 3 รอบ)
    is_satisfied: bool            # Flag การอนุมัติ
    final_verdict: str            # คำตอบสุดท้ายส่งหา User