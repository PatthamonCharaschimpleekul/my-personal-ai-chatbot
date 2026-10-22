sequenceDiagram
    autonumber
    actor User
    participant UI as Frontend UI
    participant MemoryDB as Vector DB / Mem0
    participant SubAgents as Sub-Agents Pool
    participant Synthesizer as Debate Synthesizer
    participant Twin as DigitalTwin Agent (Manager)

    %% PHASE 1: Data Collection & Memory
    rect rgb(230, 240, 255)
        note over User, MemoryDB: PHASE 1: Persona & Memory Data Collection (Chat 1)
        User->>UI: Input thoughts / project criteria / decisions
        UI->>MemoryDB: Extract & store decision metrics/chunks
        User->>UI: Click [Trigger Training / Memory Sync]
        UI->>MemoryDB: Process & consolidate chunks / prep dataset
    end

    %% PHASE 2: Multi-Agent Debate & Rejection Loop
    rect rgb(255, 240, 230)
        note over User, Twin: PHASE 2: Execution & Rejection Loop (Chat 2)
        User->>UI: Submit Project Prompt
        UI->>SubAgents: Dispatch query to Sub-Agents
        
        par Parallel Execution
            SubAgents->>SubAgents: Research Agent analyzes trends & context
            SubAgents->>SubAgents: Technical Agent evaluates feasibility & code
            SubAgents->>SubAgents: Devil's Advocate identifies risks & blind spots
        end
        
        SubAgents->>Synthesizer: Send 3-way analysis outputs
        Synthesizer->>Synthesizer: Generate Structured Debate Matrix (JSON/MD)
        Synthesizer->>UI: Stream Sub-Agent Debate Progress to Accordion UI
        
        Synthesizer->>Twin: Pass Debate Matrix + Project Goal
        MemoryDB-->>Twin: Inject Retreived Persona Memory Chunks

        loop Decision Evaluation Loop (Max 3 Retries)
            Twin->>Twin: Evaluate Matrix against User Persona & First Principles
            alt Digital Twin is NOT Satisfied (Rejection)
                Twin->>SubAgents: Reject with Specific Feedback/Refinement Directive
                SubAgents->>SubAgents: Re-analyze with new constraints
                SubAgents->>Synthesizer: Resubmit refined outputs
                Synthesizer->>Twin: Pass Updated Debate Matrix
            else Digital Twin is Satisfied (Approval)
                Twin->>UI: Generate Final Decision & Action Plan
            end
        end

        UI->>User: Display Accordion (Sub-agent Debate) + Final Decision
    end