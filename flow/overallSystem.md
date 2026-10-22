flowchart TD
    %% System Boundary Definitions
    subgraph UI ["Frontend Interface (Streamlit / Next.js)"]
        Chat1["Chat 1: Memory & Training Collector"]
        TrainBtn["[ Button: Trigger Fine-Tune / Memory Process ]"]
        Chat2["Chat 2: Decision Console & Debate"]
    end

    subgraph Memory_Pipeline ["Data & Memory Pipeline"]
        VectorDB[("Vector DB / Mem0\n(Persona & Decision Metrics)")]
        DatasetStore[("Dataset Storage\n(JSONL for LoRA)")]
        TrainScript["Local Training Pipeline\n(Unsloth / LLaMA-Factory)"]
    end

    subgraph Multi_Agent_Engine ["LangGraph Multi-Agent Engine"]
        SubAgents["Sub-Agents Execution (Parallel)\n- Research Agent\n- Technical Agent\n- Devil's Advocate"]
        DebateSynthesizer["Debate Synthesizer\n(Builds Pros/Cons/Risks Matrix)"]
        DigitalTwin["Digital Twin Agent (Manager)\n- Evaluates against User Persona\n- Evaluates Criteria Satisfaction"]
    end

    %% Data Flow Connections
    Chat1 -->|1. User Thought / Decision Logs| VectorDB
    Chat1 -->|1. Raw Chat History| DatasetStore
    TrainBtn -->|2. Trigger Training Job| TrainScript
    DatasetStore --> TrainScript
    TrainScript -->|Updated Weights / Persona| DigitalTwin

    Chat2 -->|3. Project Query| SubAgents
    VectorDB -.->|Inject Persona & Constraints| DigitalTwin
    
    SubAgents -->|4. Agent Outputs| DebateSynthesizer
    DebateSynthesizer -->|5. Debate Matrix| DigitalTwin
    
    DigitalTwin -->|6a. Approved | Chat2
    DigitalTwin -->|6b. Rejected (Feedback Loop) | SubAgents