---
name: tdd-cycle
description: Execute Test-Driven Development Red-Green-Refactor cycle for Python/FastAPI projects with atomic commits
---

# TDD Cycle Skill

## Overview
This skill enforces strict TDD discipline for SproutChat backend development. All feature development must follow the Red-Green-Refactor cycle.

## Core Principle
> **"No code without test first"** - Every feature change must begin with a failing test.

## Phase 1: Red (Write Failing Test)

### Before Writing
1. Identify the task ID (e.g., LWP-3)
2. Create test file in `backend/tests/` if not exists
3. Write test that describes expected behavior

### Test Naming Convention
```
test_<feature_name>.py
- test_create_session()
- test_send_message_timeout()
- test_conversation_history_limit()
```

### Test Structure
```python
def test_feature_description():
    """Test should fail before implementation"""
    # Given: Set up test data
    # When: Call the function
    # Then: Assert expected behavior
```

### Required Steps
1. Write test file
2. Run `pytest tests/test_<feature>.py` → **Must FAIL**
3. Commit: `[TASK-ID] test: <description> (Red)`

---

## Phase 2: Green (Minimal Implementation)

### Implementation Rule
> **"Write the minimum code to pass the test"** - No refactoring, no extra features.

### Required Steps
1. Implement feature in `backend/app/services/`
2. Run `pytest tests/test_<feature>.py` → **Must PASS**
3. Commit: `[TASK-ID] feat: <description> (Green)`

---

## Phase 3: Refactor (Optional)

### Refactoring Rules
1. Only refactor after tests pass
2. Maintain same behavior
3. Improve code quality (naming, structure, duplication)

### Required Steps
1. Refactor code
2. Run `pytest tests/test_<feature>.py` → **Must still PASS**
3. Commit: `[TASK-ID] refactor: <description> (Refactor)`

---

## Verification Checklist

Before moving to next task:
- [ ] All tests pass (`pytest`)
- [ ] Test coverage ≥ 80%
- [ ] No new lint errors (`black . && isort .`)
- [ ] Commit message follows convention
- [ ] Task status updated in Taskmaster

---

## Common Patterns

### New Feature Pattern
```bash
# 1. Red Phase
vim tests/test_new_feature.py
pytest  # ❌ FAIL
git add tests/test_new_feature.py
git commit -m "[LWP-X] test: Add new feature test (Red)"

# 2. Green Phase
vim backend/app/services/new_feature.py
pytest  # ✅ PASS
git add backend/app/services/new_feature.py
git commit -m "[LWP-X] feat: Implement new feature (Green)"

# 3. Refactor (optional)
vim backend/app/services/new_feature.py
pytest  # ✅ PASS
git commit -m "[LWP-X] refactor: Optimize code (Refactor)"
```

### Bug Fix Pattern
```bash
# Red: Write test that exposes bug
vim tests/test_bug.py
pytest  # ❌ FAIL (bug reproduced)
git commit -m "[LWP-X] test: Reproduce bug (Red)"

# Green: Fix the bug
vim backend/app/services/bug.py
pytest  # ✅ PASS (bug fixed)
git commit -m "[LWP-X] fix: Fix bug (Green)"
```

---

## Important Notes

### DO
- Always run pytest before committing
- Keep commits atomic (one logical change per commit)
- Use descriptive test names
- Follow project naming conventions

### DON'T
- Skip Red phase
- Write implementation before test
- Mix multiple changes in one commit
- Refactor in Green phase

---

## Related Skills
- `git-commit` - Commit message conventions
- `github-sync` - GitHub and Taskmaster synchronization
