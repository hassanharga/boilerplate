# Prompt for Claude Code

Copy everything below this line into Claude Code:

---

I want you to plan and then build a personal TDD-based learning repository called `skill-forge`. Its purpose: you write the tests, I write the implementations. This keeps my coding skills sharp while using AI. Plan the full structure first, show me the plan, and wait for my approval before implementing.

## Core concept

- You write complete, well-designed test suites. I write the code to make them pass.
- Never write implementation code for the exercises, not even stubs beyond an empty function/class signature with a TODO comment.
- All exercises must be realistic, real-world scenarios — things a working developer actually builds. No algorithm puzzles, no linked lists, no string reversal, no LeetCode-style problems.

## Repository structure

Create a top-level folder per stack:

- `javascript/` — core language: closures, async patterns, event handling, data transformation
- `typescript/` — typing real APIs, generics in practice, narrowing, utility types on real data models
- `node/` — file handling, streams, HTTP clients, CLI tools, environment config, error handling
- `react/` — hooks, forms, data fetching, state management, component composition (use React Testing Library)
- `frontend/` — DOM, fetch, browser storage, debouncing, accessibility, no-framework UI logic
- `backend/` — Express/Fastify APIs, middleware, validation, auth flows, rate limiting, database-layer logic (mock the DB)

Inside each stack folder, create three difficulty folders: `easy/`, `medium/`, `hard/`. Each difficulty folder contains 3-5 self-contained exercise folders.

## Exercise format

Each exercise folder must contain:

1. `README.md` with:
   - A realistic scenario framing (e.g., "Your team's checkout service is double-charging users when requests retry…")
   - The learning goal (what skill this builds)
   - Acceptance criteria in plain language
   - A "Hints" section with 2-3 progressive hints hidden behind `<details>` tags — concepts to look up, never code
2. A test file with a thorough suite: happy paths, edge cases, error cases. Tests should be readable enough that they double as a spec.
3. A skeleton implementation file: just the exported function/class signature and a `// TODO: implement` comment.
4. A `SOLUTION_NOTES.md` placeholder where I'll write my own retrospective after solving it (leave it with a template: what I learned, what I'd do differently).

## Difficulty calibration

- **Easy**: single function or small module, one clear responsibility (e.g., parse and validate a config object, format a price with currency rules, a useToggle hook)
- **Medium**: multiple interacting parts, async, error handling (e.g., a fetch wrapper with retries and timeout, a form with validation state, paginated API endpoint)
- **Hard**: design-level problems approaching senior work (e.g., a rate limiter middleware, an event-driven job queue, optimistic UI updates with rollback, a caching layer with invalidation)

## Special exercise type: refactoring katas

In each stack's `medium/` and `hard/` folders, include at least one `refactor-*` exercise: you provide ugly but working code WITH passing tests, and my job is to refactor it without breaking the tests. The README should list the code smells to fix.

## Tooling

- Use Vitest as the test runner everywhere (with jsdom + React Testing Library for react/frontend)
- One root `package.json` with workspaces, or per-stack package.json — pick the simpler setup and justify it in the plan
- A root `README.md` explaining the philosophy, the rules I've set for myself (no asking AI for solutions, hints only, 20 minutes of own debugging before asking anything), and how to run tests for any exercise (e.g., `npm test javascript/easy/01-config-parser`)
- Add a `PROGRESS.md` manifest at root: a checklist table of every exercise per stack/difficulty so I can track completion and revisit it as a reference later
- Initialize git with a sensible `.gitignore`

## Rules for you going forward (also write these into the root README under "AI Contract")

1. You write tests and READMEs. You never write exercise implementations.
2. If I'm stuck and ask for help, give me a concept or a question to think about — never code.
3. When my implementation passes, I may ask you to review it like a strict senior engineer: idioms, performance, edge cases the tests missed, naming. Be direct, not flattering.
4. When I ask for new exercises later, follow this same format and slot them into the right folder.

Start by presenting the plan: full folder tree with exercise names and one-line scenario descriptions for each. Wait for my approval, then implement in stages (one stack at a time) so I can review as you go.
