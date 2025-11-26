---
description: Agent file operation safety policy.
name: agent_file_operation_policy
applyTo: "**/*"
---
# Agent File Operation Policy
- Always prompt the user for confirmation before moving or deleting files.
- Do not proceed with file operations unless the user explicitly confirms.
- Applies to all file operations in scripts, source, data, and configuration folders.
- Prevents accidental data loss and ensures user control.
