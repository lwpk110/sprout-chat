---
name: github-sync
description: Standardize GitHub operations and Taskmaster task synchronization rules
---

# GitHub Sync Skill

## Overview
This skill defines synchronization rules between GitHub operations and Taskmaster tasks, ensuring all GitHub actions (Issue, PR, Commit) are timely synchronized to Taskmaster.

## Core Principle

> **"All GitHub operations must synchronize with Taskmaster after completion"**

---

## Synchronization Rules

| GitHub Operation | Taskmaster Action | Priority |
|------------------|-------------------|----------|
| Create Issue | Create corresponding task or update related task | P0 |
| Close Issue | Update task status to done | P0 |
| Merge PR | Update task status to done | P0 |
| Create Commit | Record task progress (optional) | P1 |

---

## Scenario: Create Issue

### Rules
1. After Issue creation, must create corresponding Taskmaster task
2. Task priority determined by Issue labels
3. Task description should contain Issue link

### Execution Steps

```bash
# 1. Create Issue
gh issue create --title "Feature description" --body "Detailed description"

# 2. Create Taskmaster task
task-master add-task --prompt="Feature description (Issue #123)

Detailed description...

Ref: https://github.com/lwpk110/sprout-chat/issues/123" --priority=P1

# 3. Create synchronization record
git commit --allow-empty -m "docs: Issue #123 synced to Taskmaster

- Issue: Feature description
- Taskmaster task pending
- Priority: P1

Refs: #123"
```

---

## Scenario: Close Issue

### Rules
1. After Issue closing, find corresponding Taskmaster task
2. Update task status to done
3. If there are related code commits, reference commit records

### Execution Steps

```bash
# 1. Close Issue
gh issue close 123

# 2. Update Taskmaster task status
task-master set-status --id=LWP-X --status=done

# 3. Create closing record
git commit --allow-empty -m "docs: Issue #123 closed, task completed

- Feature implemented and merged
- Taskmaster task LWP-X marked as done

Refs: #123"
```

---

## Scenario: Merge Pull Request

### Rules
1. After PR merge, find associated Taskmaster task
2. Update task status to done
3. Record merge information and related commits

### Execution Steps

```bash
# 1. Merge PR
gh pr merge 456 --squash --delete-branch

# 2. Update Taskmaster task status
task-master set-status --id=LWP-X --status=done

# 3. Create merge record
git commit --allow-empty -m "docs: PR #456 merged, feature complete

- Task LWP-X completed
- Contains commits: abc1234, def5678

Refs: LWP-X, PR-456"
```

---

## Priority Mapping

### Issue Labels to Task Priority

| Issue Label | Task Priority |
|-------------|---------------|
| bug | P0 |
| critical | P0 |
| enhancement | P1 |
| feature | P1 |
| documentation | P2 |
| backlog | P3 |

---

## Verification Checklist

### After Creating Issue
- [ ] Taskmaster task created
- [ ] Task description contains Issue link
- [ ] Priority set
- [ ] Synchronization commit created

### After Closing Issue
- [ ] Taskmaster task updated to done
- [ ] Closing reason recorded
- [ ] Related commits referenced

---

## Best Practices

1. **Timely synchronization**
   - Complete synchronization within 24 hours of Issue creation
   - Avoid omissions and duplicate work

2. **Maintain consistency**
   - Always use the same synchronization format
   - Follow conventions defined in this skill

3. **Complete recording**
   - Create independent commit for each synchronization
   - Include all relevant reference links

---

## Related Skills
- `git-commit` - Commit message conventions
- `tdd-cycle` - TDD development workflow
