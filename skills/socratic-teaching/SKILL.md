---
name: socratic-teaching
description: Implement Socratic guided teaching through questioning, supporting 7 guidance types and error type mappings
---

# Socratic Teaching Skill

## Overview
This skill defines Socratic guided teaching logic, generating targeted guidance feedback based on student error types to help students think and find answers themselves.

## Guidance Type Definition

### Seven Guidance Types

| Type | Identifier | Function | Example |
|------|------------|----------|---------|
| Clarify | clarify | Clarify student understanding | "What do you think this question is asking?" |
| Hint | hint | Give hints without direct answers | "Let's first look at what numbers are in the question?" |
| Break Down | break_down | Decompose problem into small steps | "What should we do first?" |
| Visualize | visualize | Suggest visualization methods | "Can you draw this problem?" |
| Check Work | check_work | Guide student to check answer | "Let's verify together?" |
| Alternative Method | alternative_method | Suggest other methods | "Any other ways to solve this?" |
| Encourage | encourage | Give encouragement and confidence | "You're close, think again!" |

---

## Error Type Classification

### Four Error Types

| Type | Identifier | Manifestation | Cause |
|------|------------|---------------|-------|
| Calculation Error | calculation | Steps correct, result wrong | Careless, calculation error |
| Concept Error | concept | Both steps and result wrong | Conceptual misunderstanding |
| Understanding Error | understanding | Misread question | Reading comprehension issue |
| Careless Error | careless | Occasional error | Lack of concentration |

---

## Error-Guidance Mapping

### First Attempt Mapping

```python
FIRST_ATTEMPT_MAPPING = {
    "calculation": ["hint", "check_work"],
    "concept": ["clarify", "break_down"],
    "understanding": ["clarify"],
    "careless": ["check_work", "encourage"],
}
```

### Multiple Attempts Mapping

```python
RETRY_MAPPING = {
    "calculation": ["break_down", "visualize"],
    "concept": ["visualize", "alternative_method"],
    "understanding": ["break_down", "hint"],
    "careless": ["encourage", "check_work"],
}
```

### Mapping Usage Rules

| Attempt Count | Error Type | Suggested Guidance Type |
|---------------|------------|------------------------|
| 1st | Calculation Error | Hint, Check Work |
| 2nd | Calculation Error | Break Down, Visualize |
| 1st | Concept Error | Clarify, Break Down |
| 2nd | Concept Error | Visualize, Alternative Method |

---

## Guidance Flow

### Decision Flowchart

```
Student Answer
    ↓
Analyze Error Type
    ↓
Select Guidance Strategy
    ↓
Generate Guidance Content
    ↓
Evaluate Student Response
    ↓
Adjust Strategy or Escalate
```

---

## Response Examples

### Example 1: Calculation Error

**Question**: 5 + 3 = ?
**Student Answer**: 7

**Guidance Flow**:
1. Identify error type: Calculation error
2. Select guidance type: Hint
3. Generate guidance:
   ```
   "5+3=7 is close! Let's count together:
   Hold up 5 fingers, then count 3 more......
   5,6,7,8......it's 8!"
   ```

### Example 2: Concept Error

**Question**: 5 + 3 = ?
**Student Answer**: 15

**Guidance Flow**:
1. Identify error type: Concept error
2. Select guidance type: Clarify
3. Generate guidance:
   ```
   "5+3=15 is the result of multiplication!
   Addition means 'put together'.
   5 apples plus 3 more apples, together how many?
   Let's count with sticks!"
   ```

---

## Escalation Strategy

### After Multiple Attempts

```python
ESCALATION_RULES = {
    "calculation error": "Hint → Break Down → Visualize",
    "concept error": "Clarify → Break Down → Alternative Method",
    "understanding error": "Clarify → Reread → Step-by-step",
    "careless error": "Check → Encourage → Simplify",
}
```

### Abandon Conditions
- Same question attempted more than 5 times
- Student shows obvious frustration
- Need to switch teaching mode

---

## Related Skills
- `sprout-persona` - Persona and language specifications
- `teaching-strategy` - Problem type identification
- `tdd-cycle` - TDD development workflow
