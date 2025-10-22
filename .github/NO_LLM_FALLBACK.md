Global instruction: Do not implement or inject LLM fallback behaviour in scripts or library modules.

- Purpose: Ensure simulations and tools always use a real configured LLM backend. Fallback LLMs (no-op or stub) are prohibited because they mask missing configuration and lead to misleading runs.

- Rule for developers: If the environment lacks a configured LLM, the script or module should raise a clear error explaining how to configure the LLM. Do not silently create or inject a fake LLM.

- Suggested message: "No LLM configured: sim.llm.llm_ollama.llm is None. Configure your LLM backend and retry."

- Rationale: For correctness and to avoid accidental acceptance of behavior produced by stubs. Simulation runs should be reproducible and explicit about external dependencies.
