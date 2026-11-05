# Code commenting style

When creating or substantially editing a non-trivial code file, follow the
commenting style in `scripts/create_policies_kb.py`:

- Start with a one-line module docstring that explains the file's overall job.
- Before each major part of the workflow, add a short divider-style header:

  ```python
  # -----------------------------------------------------------------------------
  # Step 1: Describe this part of the workflow.
  # -----------------------------------------------------------------------------
  ```

- Put a concise beginner-friendly comment directly above non-obvious constants,
  regular expressions, data transformations, validation, cleanup, or external
  service calls.
- Give each function a short docstring explaining what it returns or changes.
- Explain the reason for a decision (for example, why data is copied, sorted,
  or deleted), not a line-by-line restatement of obvious Python syntax.
- Keep all comments short. Tiny files do not need artificial section headers.
