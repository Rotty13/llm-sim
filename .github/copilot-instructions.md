---
description: Project-wide Copilot custom instructions for llm-sim workspace.
name: llm-sim_Copilot_Instructions

# General Coding Guidelines


## Big Picture Architecture

- **Modular Simulation Engine:** Core logic is split across `sim/` submodules: `agents`, `actions`, `memory`, `scheduler`, `inventory`, `llm`, and `world`. Each module encapsulates a distinct simulation concern.
- **World Management:** Worlds are compartmentalized in `worlds/`, each with its own YAML configs (`city.yaml`, `personas.yaml`, `names.yaml`, `world.yaml`) and logs. The `WorldManager` (`sim/world/world_manager.py`) handles all file I/O and data loading for worlds.
- **Agents:** Defined in `sim/agents/agents.py` as `Agent`, `Persona`, and `Physio` classes. Agents interact with the world, make decisions, and store episodic/semantic memories (`sim/memory/memory.py`).
- **LLM Integration:** All LLM calls use the Ollama backend via `sim/llm/llm_ollama.py`. No fallback to other LLMs; raise errors if not configured.
- **Actions:** Canonical agent/system actions are normalized via `sim/actions/actions.py` using a DSL string format (e.g., `SAY()`, `MOVE({"to":"place"})`).
- **Scheduling:** Agent schedules and time-based movement are managed by `sim/scheduler/scheduler.py`.

## Developer Workflows

- **Setup:** Use `python -m venv .venv && .venv\Scripts\activate` (Windows) and `pip install -r requirements.txt`.
- **Run Simulation:** `python scripts/run_sim.py` or use CLI: `python scripts/world_cli.py run World_0 --ticks 100`.
- **World Management:** Use `scripts/world_cli.py` for creating, listing, info, deleting, and running worlds. Example: `python scripts/world_cli.py create World_1 --city "New City" --year 2025`.
- **Testing:** Automated tests are planned for all core modules in `sim/` and user-facing scripts in `scripts/`.
- **Data Validation:** All config/data files (YAML/JSON) should have schemas enforced via logic in `WorldManager` and data loaders.

## Project-Specific Conventions

- **Docstrings:** All Python scripts must start with a multi-line docstring describing purpose, key functions/classes, LLM usage, and CLI arguments.
- **No LLM Fallback:** Do not implement or inject LLM fallback behavior; raise clear errors if no LLM is configured.
- **File Operations:** Always prompt for confirmation before moving or deleting files.
- **Ignore Outputs:** Do not read or write to `outputs/` unless explicitly instructed.
- **PEP 8:** Use PEP 8 style guide for all Python code.
- **Descriptive Naming:** Prioritize clarity and descriptive names for all functions, classes, and variables.

## Integration Points & Patterns

- **External Dependencies:** Only `requests` and `PyYAML` are required (see `requirements.txt`).
- **Cross-Component Communication:** All agent/world interactions are routed through the `WorldManager` and agent classes. LLM calls are centralized in `sim/llm/llm_ollama.py`.
- **Logging & Metrics:** Logging for simulation runs, agent actions, and world events is planned but not yet implemented.

## Key Files & Directories

- `sim/`: Core simulation modules.
- `scripts/`: CLI tools and utilities.
- `worlds/`: Example worlds and scenario templates.
- `configs/`: Data schemas and config files.

---

**Example Workflow:**
1. Create a world: `python scripts/world_cli.py create World_1 --city "New City" --year 2025`
2. Run simulation: `python scripts/world_cli.py run World_1 --ticks 100`
3. Inspect agent memories: See `sim/memory/memory.py` for API.

---

## Purpose of Documentation Files

### `CURRENT_TASK.md`
- **Purpose**: Tracks the current development goals, tasks, and priorities.
- **Usage**: Refer to this file to understand the immediate focus of the project. Update it whenever a new task is started or completed. The file should contain a single active task or be left empty/blank.
- **Update Frequency**: Daily or as tasks are completed.
- **Rule Update: Task Management**: `CURRENT_TASK.md` is for active tasks only. Completed tasks must be removed immediately upon completion.

### `FEATURES_TODO.md`
- **Purpose**: Catalogs all features and mechanics that need to be implemented or further defined.
- **Usage**: Use this file to identify long-term goals and features. It serves as a backlog for the project.
- **Update Frequency**: As new features are proposed or existing ones are completed.

### `DEFFERED_PROBLEMS.md`
- **Purpose**: Logs unresolved issues or problems that require further investigation.
- **Usage**: Add entries here for any blockers or unresolved issues encountered during development. Periodically review to check if they can be resolved.
- **Update Frequency**: Whenever a new problem is identified or resolved.

## Development Process Flow

### General Workflow

1. **Choose Task**:
   - Select a task to begin or continue development on.
   - Refer to `FEATURES_TODO.md` for long-term goals and features.
   - Refer to `DEFERRED_PROBLEMS.md` for unresolved issues that need attention.

2. **Feature-File Pairing Requirement**:
   - For every feature marked as "in progress" in `FEATURES_TODO.md`, always pair the feature entry with its corresponding main implementation file (or files) in the documentation. This ensures traceability and clarity for ongoing work.

2. **Set Current Task**:
   - Update `CURRENT_TASK.md` to reflect the task you are working on.
   - Clearly define the task, its goals, and any dependencies.

3. **Begin Development**:
   - Autonomously work on the task until completion or until encountering multiple task failures.

4. **Task Completion**:
   - If the task is a feature:
     - Mark the feature as complete in `FEATURES_TODO.md`.
   - If the task resolves a deferred problem:
     - Remove the problem from `DEFERRED_PROBLEMS.md`.

5. **Task Failure**:
   - If the task cannot be completed:
     - Document the issue in `DEFERRED_PROBLEMS.md`.
     - Include details about the failure and any blockers encountered.

6. **Repeat**:
   - Return to Step 1 and select the next task to work on.
