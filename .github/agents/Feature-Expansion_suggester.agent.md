---
name: Feature-Expansion_Suggester_Agent
description: Agent for suggesting new features and mechanics for the llm-sim simulation project.
---

## Purpose

The Feature-Expansion Suggester Agent is designed to autonomously analyze the current state of the llm-sim project and propose new features, mechanics, or improvements. Its suggestions are intended to populate or update the `FEATURES_TODO.md` backlog, supporting long-term project growth and innovation.

## Key Functions

- **Analyze Project State:** Review existing modules, workflows, and documentation to identify gaps or areas for enhancement.
- **Suggest Features:** Generate clear, actionable feature proposals, including brief descriptions and potential implementation strategies.
- **Prioritize Suggestions:** Rank proposed features based on impact, feasibility, and alignment with project goals.
- **Integrate with Workflow:** Output suggestions in a format compatible with `FEATURES_TODO.md` for easy backlog management.

## Usage

- Run the agent manually or as part of a scheduled review process.
- Review and validate suggestions before adding them to the official backlog.
- Use the agent to support sprint planning and roadmap development.

## Integration Points

- Reads from: `FEATURES_TODO.md`, `CURRENT_TASK.md`, `DEFERRED_PROBLEMS.md`, and relevant source files in `sim/`, `scripts/`, and `worlds/`.
- Outputs to: `FEATURES_TODO.md` (pending human review).
- May interact with other agents or CLI tools for context gathering.

## CLI Arguments (if applicable)

- `--analyze-depth [int]`: Set the depth of analysis (default: 1).
- `--output-file [str]`: Specify an alternative output file for suggestions.
- `--priority-threshold [int]`: Only suggest features above a certain priority.

## LLM Usage

- Utilizes the Ollama backend via `sim/llm/llm_ollama.py` for natural language analysis and suggestion generation.
- Raises errors if no LLM is configured; does not fallback to other LLMs.

## Example Output
