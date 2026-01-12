# SproutChat Skills

This directory contains Agent Skills for the SproutChat project. These skills define reusable development patterns and best practices.

## Skills Structure

```
skills/
├── tdd-cycle/SKILL.md           # TDD Red-Green-Refactor cycle
├── git-commit/SKILL.md          # Git commit conventions
├── sprout-persona/SKILL.md      # Sprout AI persona definition
├── teaching-strategy/SKILL.md   # Teaching strategy selection
├── socratic-teaching/SKILL.md   # Socratic guided teaching
└── github-sync/SKILL.md         # GitHub-Taskmaster sync
```

## Usage

These skills are loaded by Claude when working on the SproutChat project. They provide:

- Development workflow guidelines
- Coding conventions
- Teaching methodology
- Process automation rules

## Skills Overview

### Development Workflow
- **tdd-cycle**: Test-Driven Development process
- **git-commit**: Commit message standards
- **github-sync**: GitHub and Taskmaster synchronization

### Teaching Methodology
- **sprout-persona**: AI tutor personality and language style
- **teaching-strategy**: Problem classification and strategy selection
- **socratic-teaching**: Guided teaching through questioning

## Adding New Skills

To add a new skill:
1. Create a new directory under `skills/`
2. Add `SKILL.md` with YAML frontmatter
3. Define name, description, and detailed instructions

---

Generated: 2026-01-12
