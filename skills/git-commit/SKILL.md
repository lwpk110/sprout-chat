---
name: git-commit
description: Git commit conventions for SproutChat project, including TYPE, task ID association, and atomic commit principles
---

# Git Commit Skill

## Overview
This skill defines Git commit conventions for the SproutChat project, ensuring all commit messages are clear, traceable, and associated with Taskmaster tasks.

## Core Principles

### Atomic Commit Principle
> **Each commit contains only one logical change, batch commits are prohibited.**

### Correct Example
```bash
# Each feature point independently committed
git add backend/app/api/conversations.py
git commit -m "[LWP-1] Implement conversation creation API"

git add backend/app/services/engine.py
git commit -m "[LWP-1] Implement conversation engine core logic"

git add tests/test_engine.py
git commit -m "[LWP-1] Add unit tests"
```

### Incorrect Example
```bash
# ❌ One-time submission of all changes
git add .
git commit -m "LWP-1 complete"  # Violates atomic commit principle
```

---

## Commit Message Format

### Standard Format
```
[TYPE](Task-ID): Short description

Detailed explanation (optional)
- Item 1
- Item 2

Refs: Task-ID

Co-Authored-By: ... (if applicable)
```

### Examples
```bash
# New feature
git commit -m "[LWP-2] Implement OCR image recognition service

- Integrate PaddleOCR
- Create /api/v1/ocr/upload endpoint
- Add image preprocessing pipeline

Refs: LWP-2"

# Bug fix
git commit -m "[LWP-1] Fix session expiration time calculation error"

# Documentation update
git commit -m "[LWP-1] Update API documentation"
```

---

## TYPE Specification

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: Add user registration feature` |
| `fix` | Bug fix | `fix: Fix session timeout issue` |
| `docs` | Documentation update | `docs: Update README` |
| `style` | Code formatting | `style: Format code` |
| `refactor` | Code refactoring | `feat: Optimize conversation engine` |
| `test` | Test related | `test: Add unit tests` |
| `chore` | Build/tool related | `chore: Update dependency versions` |

---

## Task ID Association

### Rules
- All commits must have corresponding Task ID
- Task ID format: `LWP-X` (e.g., LWP-1, LWP-2.2-T025)

### Pre-commit Checklist
```bash
# 1. Syntax check
python -m py_compile backend/app/**/*.py

# 2. Code formatting
black backend/app --check
isort backend/app --check

# 3. Test verification
pytest backend/tests/ -v

# 4. View git status
git status
```

---

## Task Status and Commit Mapping

| Task Status | Expected Commits |
|-------------|------------------|
| In Progress | `test: xxx (Red)` or `feat: xxx (Green)` |
| Done | Final `feat:` or `fix:` commit |
| Refactor | `refactor: xxx` |

---

## Common Scenarios

### TDD Development
```bash
# Red: Test fails
git commit -m "[LWP-3] test: Add teaching test (Red)"

# Green: Test passes
git commit -m "[LWP-3] feat: Implement teaching feature (Green)"

# Refactor: Optimize code
git commit -m "[LWP-3] refactor: Optimize teaching code (Refactor)"
```

### Bug Fix
```bash
# Reproduce Bug
git commit -m "[LWP-1] test: Reproduce session loss bug (Red)"

# Fix Bug
git commit -m "[LWP-1] fix: Fix session state saving issue (Green)"
```

### Documentation Update
```bash
git commit -m "[LWP-1] docs: Update API documentation

- Add new endpoint description
- Update request/response examples

Refs: LWP-1"
```

---

## Error Handling

### Incorrect Commit Messages
```bash
# ❌ Incorrect examples
git commit -m "update code"
git commit -m "fix bug"
git commit -m "wip"  # Work in progress

# ✅ Correct examples
git commit -m "[LWP-1] fix: Fix user login timeout issue"
git commit -m "[LWP-1] test: Add login timeout test (Red)"
```

---

## Verification Steps

Verify after commit:
```bash
# Verify commit success
git log -1

# Verify files committed
git diff HEAD

# Verify task status
task-master list
```

---

## Related Skills
- `tdd-cycle` - TDD development workflow
- `github-sync` - GitHub and Taskmaster synchronization
