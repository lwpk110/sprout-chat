---
name: teaching-strategy
description: Automatically select optimal guided teaching strategy based on problem type, including problem classification, strategy templates, and metaphor resources
---

# Teaching Strategy Skill

## Overview
This skill defines SproutChat's problem classification system and corresponding teaching strategy selection logic, ensuring each problem type receives the most suitable guidance.

## Problem Type Classification

### Six Core Types

| Type | Identifier | Keywords | Difficulty |
|------|------------|----------|------------|
| Addition | ADDITION | 加, 一共有, 总共, 合起来 | ⭐ |
| Subtraction | SUBTRACTION | 减, 剩下, 吃掉, 拿走 | ⭐ |
| Multiplication | MULTIPLICATION | 乘, 倍, 每组, 共 | ⭐⭐ |
| Division | DIVISION | 除, 平均, 平分, 分给 | ⭐⭐ |
| Comparison | COMPARISON | 大, 小, 多, 少, 比较 | ⭐⭐ |
| Word Problem | WORD_PROBLEM | 有, 个, 只, 还, 最后 | ⭐⭐⭐ |

---

## Teaching Strategy Templates

### Addition Strategy

**Default Metaphor**: Building blocks
**Default Action**: Stacking blocks
**Alternative Metaphors**: Candy, toys, fruits

```python
ADDITION_STRATEGY = {
    "template": "Let's play a {action} game! Imagine there are {metaphor}...",
    "questions": [
        "How many {metaphor} are here?",
        "How many more {metaphor} should we add?",
        "How many {metaphor} are there now?"
    ]
}
```

### Subtraction Strategy

**Default Metaphor**: Apples
**Default Action**: Distributing apples
**Alternative Metaphors**: Candy, blocks, cake

```python
SUBTRACTION_STRATEGY = {
    "template": "Let's share {metaphor}! Originally there are {metaphor}...",
    "questions": [
        "How many {metaphor} were there originally?",
        "How many {metaphor} were taken (eaten)?",
        "How many {metaphor} are left?"
    ]
}
```

---

## Strategy Selection Flow

### Decision Tree

```
Question Input
    ↓
Extract Keywords
    ↓
Match Problem Type
    ↓
Select Teaching Strategy
    ↓
Apply Metaphor and Template
    ↓
Generate Guidance Questions
```

---

## Metaphor Selection Rules

### Priority
1. **Student Age**: Use simple metaphors for 6-7 years old
2. **Student Interests**: Based on historical conversations
3. **Problem Scenario**: Choose metaphor matching problem context
4. **Cultural Adaptation**: Choose items familiar to Chinese students

### Metaphor Library

| Age Group | Recommended Metaphors | Avoid Metaphors |
|-----------|----------------------|-----------------|
| 6 years | Candy, blocks, small animals, picture books | Electronic products, abstract concepts |
| 7 years | Toys, fruits, animals, snacks | Too childish metaphors |

---

## Related Skills
- `sprout-persona` - Persona and language specifications
- `socratic-teaching` - Guided teaching
- `tdd-cycle` - TDD development workflow
