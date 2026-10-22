import json
import sys
import re
from unittest.mock import MagicMock
from openai import OpenAI
from duckduckgo_search import DDGS
from src.logger_config import logger
from src.utils import remove_chinese_chars

# Import settings from our config
from src.config import API_KEY, API_BASE, MODELS, DEFAULT_TEMPERATURE

# 1. Mock xxhash
try:
    import xxhash
except ImportError:
    mock_xxhash = MagicMock()
    mock_xxhash.xxh64_digest.return_value = b'00000000'
    sys.modules['xxhash'] = mock_xxhash

# 2. Initialize OpenAI Client
client = OpenAI(api_key=API_KEY, base_url=API_BASE)

# --- Layer 3: CRITICAL LANGUAGE MANDATE ---
LANGUAGE_MANDATE = """
[CRITICAL LANGUAGE MANDATE]:
1. Respond STRICTLY in THAI.
2. Technical terms, acronyms, or concept names MUST remain in ENGLISH if a direct Thai word is unnatural (e.g., use "Bias", "Framework", "Overfitting").
3. NEVER use Chinese characters / Hanzi (Simplified or Traditional) under any circumstances. If you are unsure of a Thai translation, fallback to ENGLISH, NEVER Chinese.
"""

# --- Helper Tools ---
def web_search_tool(query: str, max_results=3):
    """ค้นหาข้อมูลจากอินเทอร์เน็ตแบบ Real-time"""
    logger.info(f"Using Web Search Tool for: {query}")
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=max_results)]
            return "\n\n".join([f"Source: {r['title']}\nContent: {r['body']}" for r in results])
    except Exception as e:
        logger.error(f"Web Search Tool failed: {str(e)}")
        return "ไม่สามารถเข้าถึงข้อมูลจากอินเทอร์เน็ตได้ในขณะนี้"

def call_llm(system_prompt, user_prompt, model_name):
    logger.info(f"AI Call -> {model_name}")
    full_system_prompt = system_prompt + "\n" + LANGUAGE_MANDATE

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=DEFAULT_TEMPERATURE,
            response_format={"type": "text"}
        )
        output = response.choices[0].message.content

        # --- Layer 1: Output Sanitizer ---
        sanitized_output = remove_chinese_chars(output)

        # บันทึกแค่สรุปสั้นๆ (100 ตัวอักษรแรก)
        summary = sanitized_output.replace("\n", " ")[:100] + "..." if len(sanitized_output) > 100 else sanitized_output
        logger.info(f"Response: {summary}")

        return sanitized_output
    except Exception as e:
        logger.error(f"LLM Call failed for {model_name}: {str(e)}")
        raise e

# --- Research Agents ---
def western_research_agent(state):
    logger.info("Starting Western Research Agent")
    feedback = state.get("twin_feedback", "")
    query = state['user_query']
    if feedback:
        query += f" focus on solving: {feedback}"

    search_data = web_search_tool(query + " latest trends analysis")
    system = """คุณคือ "Western Research Specialist" เน้นการหาข้อมูลจากแหล่งข่าวฝั่งตะวันตก
หากมี Feedback จาก Boss ให้ปรับปรุงการค้นหาและวิเคราะห์ตามคำสั่งนั้นอย่างเคร่งครัด"""
    user = f"โจทย์: {state['user_query']}\nFeedback จาก Boss: {feedback if feedback else 'ไม่มี'}\n\nข้อมูลอินเทอร์เน็ต:\n{search_data}"
    output = call_llm(system, user, MODELS["western_research"])
    return {"western_research_output": output}

def eastern_research_agent(state):
    logger.info("Starting Eastern/China Research Agent")
    feedback = state.get("twin_feedback", "")
    query = state['user_query']
    if feedback:
        query += f" focus on solving: {feedback}"

    search_data = web_search_tool(query + " จีน วิเคราะห์ ล่าสุด")
    system = """คุณคือ "Eastern/China Research Specialist" เน้นการหาข้อมูลจากบริบทฝั่งตะวันออก (จีน)
หากมี Feedback จาก Boss ให้ปรับปรุงการค้นหาและวิเคราะห์ตามคำสั่งนั้นอย่างเคร่งครัด"""
    user = f"โจทย์: {state['user_query']}\nFeedback จาก Boss: {feedback if feedback else 'ไม่มี'}\n\nข้อมูลอินเทอร์เน็ต:\n{search_data}"
    output = call_llm(system, user, MODELS["eastern_research"])
    return {"eastern_research_output": output}

# --- Analytical Agents ---
def technical_agent(state):
    logger.info("Starting Technical Agent")
    feedback = state.get("twin_feedback", "")
    system = """คุณคือ "Technical Architect" วิเคราะห์ Tech Stack
หากมี Feedback จาก Boss ให้ปรับปรุงการออกแบบตามคำแนะนำนั้น"""
    user = f"โจทย์: {state['user_query']}\nFeedback จาก Boss: {feedback}\n\nWESTERN: {state['western_research_output']}\n\nEASTERN: {state['eastern_research_output']}"
    output = call_llm(system, user, MODELS["technical"])
    return {"technical_output": output}

def devils_advocate_agent(state):
    logger.info("Starting Devil's Advocate Agent")
    feedback = state.get("twin_feedback", "")
    system = """คุณคือ "Devil's Advocate" ค้นหาความเสี่ยงและจุดบอด
หากมี Feedback จาก Boss ให้ตรวจสอบความเสี่ยงในประเด็นที่ Boss กังวลเป็นพิเศษ"""
    user = f"โจทย์: {state['user_query']}\nFeedback จาก Boss: {feedback}\n\nWESTERN: {state['western_research_output']}\n\nEASTERN: {state['eastern_research_output']}"
    output = call_llm(system, user, MODELS["devils_advocate"])
    return {"devils_advocate_output": output}

# --- Synthesis & Decision ---
def debate_synthesizer(state):
    logger.info("Starting Debate Synthesizer")
    system = """คุณคือผู้รวบรวมข้อมูล สรุปเป็น "Global Debate Matrix Table" ภาษาไทย"""
    user = f"WESTERN: {state['western_research_output']}\n\nEASTERN: {state['eastern_research_output']}\n\nTECH: {state['technical_output']}\n\nRISKS: {state['devils_advocate_output']}"
    output = call_llm(system, user, MODELS["synthesizer"])
    return {"debate_matrix": output}

def digital_twin_agent(state):
    logger.info("Starting Digital Twin Manager Agent")
    system = f"""คุณคือ "Boss/Digital Twin" ใช้ปรัชญาและวิสัยทัศน์ของคุณตัดสินใจ
[VISION]: {state['persona_context']}

หน้าที่ของคุณ:
1. ประเมินว่าข้อมูลจากเอเจนต์ลูกน้องเพียงพอต่อการตัดสินใจตามหลักการของคุณหรือไม่
2. อธิบาย "เหตุผล" ที่คุณเลือกยอมรับ (Approve) หรือปฏิเสธ (Reject) อย่างชัดเจน

ตอบกลับเป็น JSON:
{{
  "is_satisfied": true/false,
  "rejection_reason": "สิ่งที่ต้องแก้ไข (ใส่เฉพาะกรณี false)",
  "decision_reason": "สรุปเหตุผลที่คุณตัดสินใจแบบนี้ตามหลักการของคุณ (ใส่ทั้งกรณี true/false)",
  "final_verdict": "คำสรุปสุดท้าย (ใส่เฉพาะกรณี true)"
}}"""
    user = f"GLOBAL MATRIX:\n{state['debate_matrix']}"
    output = call_llm(system, user, MODELS["digital_twin"])

    content = output.strip()
    if "```json" in content: content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content: content = content.split("```")[1].split("```")[0].strip()

    try:
        res_data = json.loads(content)
        return {
            "is_satisfied": res_data.get("is_satisfied", False),
            "twin_feedback": res_data.get("rejection_reason", ""),
            "decision_reason": res_data.get("decision_reason", "อ้างอิงตามหลักการตัดสินใจส่วนตัว"),
            "final_verdict": res_data.get("final_verdict", ""),
            "rejection_count": 1 if not res_data.get("is_satisfied", False) else 0
        }
    except:
        return {
            "is_satisfied": True,
            "twin_feedback": "",
            "decision_reason": "พิจารณาแล้วเห็นควรให้ดำเนินการ",
            "final_verdict": output,
            "rejection_count": 0
        }

def memory_processor_agent(content: str):
    logger.info("Starting Memory Processor")
    system = """[STRICT RULE]: EXTRACT ONLY DECISION PHILOSOPHY AND VISION.
คุณคือ "Mental Model Architect" สกัดหลักการคิด (ภาษาไทย)"""
    user = f"วิเคราะห์ (ห้ามภาษาจีน): \n\n{content}"
    output = call_llm(system, user, MODELS["ingestion"])

    try:
        clean_output = re.sub(r'<think>.*?</think>', '', output, flags=re.DOTALL).strip()
        start_idx = clean_output.find("[")
        end_idx = clean_output.rfind("]")
        if start_idx != -1 and end_idx != -1:
            json_str = clean_output[start_idx:end_idx+1]
            res_data = json.loads(json_str)
            if isinstance(res_data, list): return res_data
        return [content]
    except:
        return [content]

def retrieval_agent(query: str, all_chunks: list):
    logger.info("Starting Retrieval Agent")
    system = """คุณคือ "Context Retriever" เลือก Chunks ที่เกี่ยวข้องที่สุด"""
    user = f"คำถาม: {query}\n\nChunks:\n" + "\n\n".join(all_chunks)
    output = call_llm(system, user, MODELS["retrieval"])
    return output
