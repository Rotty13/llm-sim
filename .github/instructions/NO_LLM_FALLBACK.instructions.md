---
description: LLM fallback prohibition for all modules.
name: no_llm_fallback
applyTo: "**/*.py"
---
# No LLM Fallback Policy
- Do not implement or inject LLM fallback behavior in scripts or modules.
- If no LLM is configured, raise a clear error explaining how to configure the LLM.
- Do not silently create or inject a fake LLM.
- Ensures correctness and reproducibility of simulation runs.
