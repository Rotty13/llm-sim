---
description: Script documentation requirements for Python files.
name: script_doc_policy
applyTo: "scripts/**/*.py"
---
# Script Documentation Policy
- All Python scripts must begin with a multi-line docstring describing:
  - Purpose and main functionality
  - Key functions/classes
  - Any LLM or external system usage
  - Usage notes or CLI arguments (if applicable)
- Update docstrings if the script's purpose or features change.
- PR reviewers should reject scripts without proper docstrings.
- Automated checks may be added in the future.
