---
name: commit-staged
description: Generates a commit message from staged changes.
---

Your task is to help the user to generate a commit message and commit the changes using git.

## Guidelines

- DO NOT add any ads such as "Generated with [Claude Code](https://claude.ai/code)"
- DO NOT add any ads such as "Co-Authored-By [Claude Code](https://claude.ai/code)"
- Only generate the message for staged files/changes
- Don't add any files using `git add`. The user will decide what to add.
- Ensure I'm not on main or master branch before committing.
- Use conventional commits.
- Follow the rules below for the commit message.

## Format

```
<type>:<space><message title>

<bullet points summarizing what was updated>
```

## Example Titles

```
feat: add JWT login flow
fix: handle null pointer in sidebar
refactor: split user controller logic
docs: add usage section
```

## Example with Title and Body

```
feat(auth): add JWT login flow

- Implemented JWT token validation logic
- Added documentation for the validation component
```

## Rules

- title is lowercase, no period at the end.
- Title should be a clear summary, max 50 characters.
- Use the body (optional) to explain _why_, not just _what_.
- Bullet points should be concise and high-level.

Avoid

- Vague titles like: "update", "fix stuff"
- Overly long or unfocused titles
- Excessive detail in bullet points

## Allowed Types

| Type     | Description                           |
| -------- | ------------------------------------- |
| feat     | New feature                           |
| fix      | Bug fix                               |
| chore    | Maintenance (e.g., tooling, deps)     |
| docs     | Documentation changes                 |
| refactor | Code restructure (no behavior change) |
| test     | Adding or refactoring tests           |
| style    | Code formatting (no logic change)     |
| perf     | Performance improvements              |
