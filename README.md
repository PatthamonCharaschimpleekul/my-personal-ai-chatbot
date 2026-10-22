# My Personal AI Chatbot 🤖

A local-first, multi-agent personal AI chatbot — a small "digital twin" that
talks in my context: it ingests my notes into a persona memory, retrieves
them, and answers through a debate of specialized agents, orchestrated with
**LangGraph** and served by a **Streamlit** UI.

> 🔒 Privacy by design: chat history, the persona knowledge base, and logs
> are gitignored — they never leave my machine. Models run locally via
> [Ollama](https://ollama.com) by default.

## Architecture

```
User ⇄ Streamlit UI
        │
        ├─ Memory Architect ── chunks notes → persona_db/ (local markdown)
        ├─ Retrieval Agent  ── grounds answers in persona memory
        └─ Debate Engine (LangGraph)
             ├─ Western / Eastern research agents
             ├─ Technical agent
             ├─ Devil's advocate
             ├─ Synthesizer
             └─ Digital-Twin manager (final answer)
```

Design docs & sequence diagrams live in [`flow/`](flow/) (GitHub renders the Mermaid).

## Stack

`Python · LangGraph · LangChain · OpenAI-compatible API (Ollama) · Streamlit · Pydantic · Loguru · DuckDuckGo Search`

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in your values
ollama pull qwen2.5:7b # or any model you configure
streamlit run app.py
```

## Configuration

`.env` controls the whole thing — point every agent at any
OpenAI-compatible endpoint:

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_BASE` | `http://localhost:11434/v1` | model endpoint (Ollama) |
| `OPENAI_API_KEY` | `ollama` | any placeholder for local |
| `MODEL_INGESTION` / `MODEL_RETRIEVAL` | `qwen2.5:7b` | pipeline models |
| `MODEL_RESEARCH` / `MODEL_TECHNICAL` / `MODEL_DEVILS_ADVOCATE` / `MODEL_SYNTHESIZER` | various | debate agents |
| `MODEL_DIGITAL_TWIN` | `deepseek-r1:14b` | final synthesizing agent |
