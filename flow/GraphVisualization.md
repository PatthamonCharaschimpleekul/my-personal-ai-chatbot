# Graph Visualization

This document provides a visualization of the LangGraph workflow used in this project.

## Mermaid Diagram

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<b>__start__</b>]):::first
	western_research(western_research)
	eastern_research(eastern_research)
	technical(technical)
	devils_advocate(devils_advocate)
	synthesizer(synthesizer)
	digital_twin(digital_twin)
	__end__([<b>__end__</b>]):::last
	__start__ --> eastern_research;
	__start__ --> western_research;
	devils_advocate --> synthesizer;
	digital_twin -. "end" .-> __end__;
	digital_twin -. "continue" .-> western_research;
	eastern_research --> devils_advocate;
	eastern_research --> technical;
	synthesizer --> digital_twin;
	technical --> synthesizer;
	western_research --> devils_advocate;
	western_research --> technical;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```

## Workflow Explanation

1.  **Parallel Research Entry**: The system starts by concurrently launching `western_research` and `eastern_research` to gather global perspectives.
2.  **Deep Analysis**: After both research nodes complete, the data flows into `technical` (for implementation details) and `devils_advocate` (for critical scrutiny).
3.  **Synthesis**: The `synthesizer` merges the research and analysis into a cohesive response.
4.  **Final Verdict (Digital Twin)**: The `digital_twin` agent reviews the output.
5.  **Iteration Loop**: 
    - If the Digital Twin is **satisfied**, the process terminates (`__end__`).
    - If **unsatisfied**, it loops back to the start (`western_research`) for refinement, incrementing the rejection count.

## Configuration Limits
- **Max Rejections**: Governed by `MAX_REJECTIONS` in `src/config.py`.
