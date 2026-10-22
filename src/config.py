import os
from dotenv import load_dotenv

# โหลดค่าจาก .env (ถ้ามี)
load_dotenv()

# --- API Configuration ---
API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
API_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1")

# --- Agent-Specific Models ---
MODELS = {
    # 1. Pipeline Models
    "ingestion": os.getenv("MODEL_INGESTION", "qwen2.5:7b"),
    "retrieval": os.getenv("MODEL_RETRIEVAL", "qwen2.5:7b"),

    # 2. Research Agents (Regional)
    "western_research": os.getenv("MODEL_WESTERN", "gemma2:9b"),
    "eastern_research": os.getenv("MODEL_EASTERN", "qwen2.5:14b"),

    # 3. Analytical Agents
    "technical": os.getenv("MODEL_TECHNICAL", "qwen2.5-coder:14b"),
    "devils_advocate": os.getenv("MODEL_DEVILS_ADVOCATE", "llama3.1:8b"),

    # 4. Boss & Orchestration
    "synthesizer": os.getenv("MODEL_SYNTHESIZER", "qwen2.5:14b"),
    "digital_twin": os.getenv("MODEL_DIGITAL_TWIN", "deepseek-r1:14b"),
}

# --- Shared Settings ---
DEFAULT_TEMPERATURE = 0.5 # ลดลงนิดหน่อยเพื่อความแม่นยำ
MAX_REJECTIONS = 3
