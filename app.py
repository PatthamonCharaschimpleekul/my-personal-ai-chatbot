import streamlit as st
import os
import sys
import uuid
import time
from unittest.mock import MagicMock
from dotenv import load_dotenv

# 1. Initialize Logging FIRST
from src.logger_config import logger

# 2. Mock xxhash
try:
    import xxhash
except ImportError:
    mock_xxhash = MagicMock()
    mock_xxhash.xxh64_digest.return_value = b'00000000'
    sys.modules['xxhash'] = mock_xxhash

from src.graph import create_graph
from src.agents import memory_processor_agent, retrieval_agent
from src.storage import save_chat, list_chats, load_chat

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Digital Twin Multi-Agent System", layout="wide")

# --- Constants & Setup ---
DB_DIR = "persona_db"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# --- Functions ---
def add_ui_log(message, type="info"):
    if "ui_logs" not in st.session_state:
        st.session_state.ui_logs = []
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.ui_logs.append({"time": timestamp, "msg": message, "type": type})
    if type == "success": logger.success(message)
    elif type == "warning": logger.warning(message)
    elif type == "error": logger.error(message)
    else: logger.info(message)

def get_db_stats():
    if not os.path.exists(DB_DIR):
        return 0, 20, 0
    files = [f for f in os.listdir(DB_DIR) if f.endswith(".md") or f.endswith(".txt")]
    count = len(files)
    target = 20
    percentage = min(int((count / target) * 100), 100)
    return count, target, percentage

def process_and_save_to_db(content, original_filename=None):
    add_ui_log(f"Starting memory processing for: {original_filename or 'New Note'}")
    with st.spinner("🧠 Memory Architect is processing and chunking your input..."):
        try:
            chunks = memory_processor_agent(content)
            add_ui_log(f"Successfully split into {len(chunks)} chunks", type="success")
        except Exception as e:
            add_ui_log(f"Chunking failed: {str(e)}", type="error")
            chunks = [content]

    for i, chunk in enumerate(chunks):
        if original_filename:
            base_name = os.path.splitext(original_filename)[0]
            filename = f"{base_name}_chunk_{i}_{uuid.uuid4().hex[:4]}.md"
        else:
            filename = f"chunk_{uuid.uuid4().hex[:8]}.md"

        path = os.path.join(DB_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(chunk)
        add_ui_log(f"Saved chunk: {filename}")
    return len(chunks)

def delete_file(filename):
    path = os.path.join(DB_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
        add_ui_log(f"Deleted file: {filename}", type="warning")
        return True
    return False

def get_all_chunks():
    if not os.path.exists(DB_DIR):
        return []
    files = [f for f in os.listdir(DB_DIR) if f.endswith(".md") or f.endswith(".txt")]
    all_chunks = []
    for f_name in files:
        with open(os.path.join(DB_DIR, f_name), "r", encoding="utf-8") as f:
            all_chunks.append(f.read())
    return all_chunks

def clear_db():
    add_ui_log("Requesting full database clear...", type="warning")
    if os.path.exists(DB_DIR):
        for f in os.listdir(DB_DIR):
            os.remove(os.path.join(DB_DIR, f))
    add_ui_log("All database files cleared", type="success")
    return True

def start_new_chat():
    st.session_state.messages = []
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.current_chat_title = "New Chat"
    add_ui_log("Started a new chat session", type="success")

# --- Session State Initialization ---
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "ui_logs" not in st.session_state:
    st.session_state.ui_logs = []
    add_ui_log("System initialized", type="success")

# --- UI ---
st.title("🤖 Digital Twin Multi-Agent System")

with st.sidebar:
    st.header("💬 Chat History")
    if st.button("➕ New Chat", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.divider()
    chats = list_chats()
    for chat in chats:
        col_chat, col_del = st.columns([1.0, 0.001]) # เน้นพื้นที่กดชื่อแชท
        if col_chat.button(f"📄 {chat['title']}", key=f"chat_{chat['id']}", use_container_width=True):
            loaded = load_chat(chat["id"])
            if loaded:
                st.session_state.messages = loaded["messages"]
                st.session_state.current_chat_id = loaded["id"]
                st.session_state.current_chat_title = loaded["title"]
                add_ui_log(f"Loaded chat: {chat['title']}")
                st.rerun()

    st.divider()
    st.header("⚙️ System Status")
    count, target, pct = get_db_stats()
    st.write(f"**Database:** {count}/{target} chunks")
    st.progress(pct / 100)

    with st.expander("📜 System Logs"):
        for log in reversed(st.session_state.ui_logs[-15:]):
            color = "white"
            if log["type"] == "success": color = "#28a745"
            elif log["type"] == "warning": color = "#ffc107"
            elif log["type"] == "error": color = "#dc3545"
            st.markdown(f"<small style='color:{color}'>[{log['time']}] {log['msg']}</small>", unsafe_allow_html=True)

    with st.expander("🗑️ Database Management"):
        confirm_delete = st.checkbox("ยืนยันลบฐานข้อมูลทั้งหมด")
        if st.button("Clear All Database", type="primary", disabled=not confirm_delete):
            if clear_db():
                st.rerun()

# Tab management
tab1, tab2 = st.tabs(["👤 Chat 1: Memory Collector", "💬 Chat 2: Decision Console"])

# --- TAB 1: Memory Collector ---
with tab1:
    st.header("Persona & Memory Collection")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Add Memory")
        note_input = st.text_area("บันทึกความคิดหรือเกณฑ์การตัดสินใจใหม่:", height=150)
        if st.button("Save Note"):
            if note_input:
                num_chunks = process_and_save_to_db(note_input)
                st.success(f"บันทึกและแบ่งเป็น {num_chunks} chunks เรียบร้อย!")
                time.sleep(0.5)
                st.rerun()

    with col2:
        st.subheader("Upload MD Files")
        uploaded_files = st.file_uploader("เลือกไฟล์ .md หรือ .txt", accept_multiple_files=True, type=["md", "txt"])
        if uploaded_files:
            if st.button("🔥 Process Uploaded Files"):
                total_chunks = 0
                for uploaded_file in uploaded_files:
                    content = uploaded_file.read().decode("utf-8")
                    num = process_and_save_to_db(content, uploaded_file.name)
                    total_chunks += num
                st.success(f"อัปโหลดและประมวลผลเป็นทั้งหมด {total_chunks} chunks เรียบร้อย!")
                time.sleep(0.5)
                st.rerun()

    st.divider()
    st.subheader("Current Database Contents")
    files = [f for f in os.listdir(DB_DIR) if f.endswith(".md") or f.endswith(".txt")] if os.path.exists(DB_DIR) else []
    if not files:
        st.write("ยังไม่มีข้อมูลในฐานข้อมูล")
    else:
        files.sort(key=lambda x: os.path.getmtime(os.path.join(DB_DIR, x)), reverse=True)
        for f in files:
            col_file, col_del = st.columns([0.9, 0.1])
            with col_file:
                with st.expander(f):
                    with open(os.path.join(DB_DIR, f), "r", encoding="utf-8") as f_content:
                        st.text(f_content.read())
            with col_del:
                if st.button("🗑️", key=f"del_{f}"):
                    if delete_file(f):
                        st.rerun()

# --- TAB 2: Decision Console ---
with tab2:
    st.header("Decision Console")

    # ฟังก์ชันช่วยวาดแชทจาก Role
    def render_chat_message(msg):
        role = msg["role"]
        content = msg["content"]
        avatar = None
        label = None

        if role == "user":
            avatar = "user"
        elif role == "assistant":
            avatar = "assistant"
        elif role == "thought":
            # ค้นหาว่าเป็น Agent ตัวไหนจาก Content หรือ Metadata
            agent_type = msg.get("agent", "")
            if agent_type == "western": avatar, label = "🇺🇸", "Western Research"
            elif agent_type == "eastern": avatar, label = "🇨🇳", "Eastern/China Research"
            elif agent_type == "technical": avatar, label = "💻", "Technical Agent"
            elif agent_type == "devil": avatar, label = "😈", "Devil's Advocate"
            elif agent_type == "twin": avatar, label = "🤖", "Digital Twin (Decision)"

        with st.chat_message(avatar or role):
            if label: st.subheader(label)
            st.markdown(content)
            if "reason" in msg and msg["reason"]:
                st.info(f"**การวิเคราะห์ของ Boss:** {msg['reason']}")
            if "feedback" in msg and msg["feedback"]:
                st.warning(f"**สิ่งที่ต้องแก้ไข (Feedback):** {msg['feedback']}")
            if "matrix" in msg and msg["matrix"]:
                with st.expander("📊 View Debate Matrix"):
                    st.markdown(msg["matrix"])

    # วาดแชทเก่า
    for message in st.session_state.messages:
        render_chat_message(message)

    if prompt := st.chat_input("ต้องการปรึกษาเรื่องอะไรครับ?"):
        add_ui_log(f"User Query: {prompt}")
        user_msg = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_msg)
        render_chat_message(user_msg)

        with st.chat_message("assistant"):
            with st.status("Agents are thinking...", expanded=True) as status:
                all_chunks = get_all_chunks()
                if all_chunks:
                    add_ui_log("Retrieval Agent is selecting relevant chunks")
                    relevant_context = retrieval_agent(prompt, all_chunks)
                else:
                    relevant_context = "ไม่มีข้อมูลในฐานข้อมูล"

                graph = create_graph()
                inputs = {
                    "user_query": prompt,
                    "persona_context": relevant_context,
                    "rejection_count": 0,
                    "is_satisfied": False,
                    "twin_feedback": ""
                }

                final_state_full = inputs.copy()
                for output in graph.stream(inputs):
                    for key, value in output.items():
                        add_ui_log(f"Agent {key} completed step")

                        # จัดการตัวนับรอบการปฏิเสธ (เพราะใน Graph เป็นแบบสะสม)
                        if "rejection_count" in value:
                            final_state_full["rejection_count"] += value["rejection_count"]

                        # อัปเดตค่าอื่นๆ
                        for k, v in value.items():
                            if k != "rejection_count":
                                final_state_full[k] = v

                        # บันทึก Thinking ของเอเจนต์แต่ละตัวลงประวัติ
                        thought_msg = None
                        if key == "western_research":
                            thought_msg = {"role": "thought", "agent": "western", "content": value.get("western_research_output", "")}
                        elif key == "eastern_research":
                            thought_msg = {"role": "thought", "agent": "eastern", "content": value.get("eastern_research_output", "")}
                        elif key == "technical":
                            thought_msg = {"role": "thought", "agent": "technical", "content": value.get("technical_output", "")}
                        elif key == "devils_advocate":
                            thought_msg = {"role": "thought", "agent": "devil", "content": value.get("devils_advocate_output", "")}
                        elif key == "digital_twin":
                            is_sat = value.get("is_satisfied")
                            current_round = final_state_full.get("rejection_count")
                            status_text = "🎯 อนุมัติเรียบร้อย" if is_sat else f"⚠️ ปฏิเสธการตัดสินใจ (ครั้งที่ {current_round})"
                            thought_msg = {
                                "role": "thought",
                                "agent": "twin",
                                "content": status_text,
                                "reason": value.get("decision_reason", ""),
                                "feedback": value.get("twin_feedback", "")
                            }

                        if thought_msg:
                            st.session_state.messages.append(thought_msg)
                            render_chat_message(thought_msg)

                status.update(label="Analysis Complete!", state="complete", expanded=False)

            answer = final_state_full.get("final_verdict", "ขออภัย ไม่สามารถสรุปคำตอบได้")
            decision_reason = final_state_full.get("decision_reason", "")
            matrix = final_state_full.get("debate_matrix", "")

            final_msg = {
                "role": "assistant",
                "content": answer,
                "reason": decision_reason,
                "matrix": matrix
            }
            st.session_state.messages.append(final_msg)
            render_chat_message(final_msg)

            save_chat(st.session_state.current_chat_id, st.session_state.messages)
