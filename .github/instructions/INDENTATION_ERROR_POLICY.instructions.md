---
description: Indentation error handling policy for agents and contributors.
name: indentation_error_policy
applyTo: "**/*"
---
# Indentation Error Handling Policy

- If indentation errors are detected during code editing or patching, agents must request the user to fix the indentation before proceeding with further changes.
- Agents should not attempt to auto-correct indentation errors unless explicitly instructed by the user.
- Contributors should ensure all code is properly indented and formatted before submitting changes or patches.
- This policy applies to all Python files and any other code files where indentation is significant.
- The goal is to prevent cascading errors and maintain codebase consistency.
