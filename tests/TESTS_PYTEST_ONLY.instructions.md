---
description: All tests in llm-sim must use pytest.
name: TESTS_PYTEST_ONLY.instructions.md
applyTo: "tests/**/*.py"
---
# Test Framework Policy: pytest Only

- All test files in the `tests/` directory must use the `pytest` framework.
- Do not use `unittest.TestCase` or the `unittest` module for new or refactored tests.
- Use function-based tests, direct assertions, and pytest fixtures where appropriate.
- Remove any calls to `unittest.main()`.
- For mocking, use `pytest` and `pytest-mock` or the standard `unittest.mock` library with pytest.
- All future test contributions must follow pytest conventions for consistency and maintainability.
