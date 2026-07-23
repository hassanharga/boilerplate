# Frontend Failure Modes — React, Angular, Next.js, plain JS

Frontend logic bugs hide behind a rendered UI that _looks_ right. The screenshot passes; the bug is a stale value, a leaked subscription, or a race that only shows on a slow network or a second interaction. Each entry gives a **detection cue** so you can spot it in the diff without a running browser.

Read the section that matches the diff. The **cross-cutting JS/TS** section applies to all of them.

## Contents

**Cross-cutting JS / TS**

- 1. `==` and truthiness that drops `0` / `''` / `false`
- 2. Mutating shared state instead of copying
- 3. Floating-point money and `parseInt` without radix
- 4. `JSON.parse` / `await fetch` with no failure path

**React**

- 5. Stale closure — effect/callback captures an old value
- 6. Missing effect cleanup — leaked subscriptions, timers, listeners
- 7. Fetch race — out-of-order responses render the wrong data
- 8. Derived state stored in `useState`
- 9. `setState` from a stale value instead of the updater form
- 10. List `key` = array index
- 11. Conditional / looped hooks

**Angular**

- 12. Unsubscribed Observable — leak and duplicate work
- 13. Nested `subscribe` instead of a higher-order operator
- 14. Mutating an `@Input` / OnPush not detecting change

**Next.js**

- 15. Server/client boundary — browser API in a server component
- 16. Stale data from default fetch caching
- 17. Secret leaked into the client bundle
- 18. Server Action / route handler with no auth or validation

---

## Cross-cutting JS / TS

### 1. `==` and truthiness that drops `0` / `''` / `false`

**Pattern.** `if (count)`, `value || fallback`, or `==` used where a value can legitimately be `0`, `''`, or `false`.

**Why it bites.** `if (count)` skips the `count === 0` case; `qty || 1` turns a real `0` into `1`. These are silent wrong-answer bugs, not crashes.

**Detection cue.** `||` supplying a default for a numeric/string field, or a bare truthiness check on a value whose valid domain includes `0`/`''`. Prefer `??` for defaults and `=== undefined`/`=== null` for presence.

### 2. Mutating shared state instead of copying

**Pattern.** `array.sort()`, `array.push()`, `Object.assign(existing, ...)`, or splice on a value that came from props, state, a store, or a shared config — instead of copying first.

**Why it bites.** `sort`/`reverse`/`splice` mutate in place. Mutating props or store state breaks change detection (React/Angular don't see a new reference), corrupts other components sharing the object, and causes "why didn't it re-render" bugs.

**Detection cue.** `.sort(`, `.reverse(`, `.push(`, `.splice(` called directly on a prop, `useState` value, `@Input`, or selector result. Should be `[...arr].sort(...)` / `{ ...obj, x }`.

### 3. Floating-point money and `parseInt` without radix

**Pattern.** Currency math in floats (`0.1 + 0.2`), or `parseInt(x)` with no radix.

**Why it bites.** Float rounding produces off-by-a-cent totals; missing radix historically parses `"08"`-style input wrong. Money should be integer minor units (this repo's domain uses `priceCents`-style fields — match it).

**Detection cue.** Arithmetic on a `price`/`amount`/`total` that isn't an integer-cents field; `parseInt(` without a second argument; `Number(x)` on user input with no NaN check.

### 4. `JSON.parse` / `await fetch` with no failure path

**Pattern.** `JSON.parse(res)` or `await fetch(url).then(r => r.json())` with no try/catch and no `res.ok` check.

**Why it bites.** `fetch` does **not** reject on 4xx/5xx — only on network failure. Code that only `.catch`es network errors treats a `500 {error}` body as success and parses garbage. `JSON.parse` on a non-JSON error page throws synchronously.

**Detection cue.** `fetch(...)` whose result is parsed without checking `response.ok`; `JSON.parse` outside a try/catch on data from the network or storage.

---

## React

### 5. Stale closure — effect/callback captures an old value

**Pattern.** A `useEffect`, `useCallback`, event handler, or `setInterval` callback reads a state/prop value, but that value is missing from the dependency array — so the closure keeps seeing the value from the render when it was created.

**Why it bites.** The single most common React logic bug. The UI shows the current value but the callback acts on a stale one — a debounce that saves old text, an interval that always logs the initial count. Invisible until you interact after a state change.

**Detection cue.** A value referenced inside a `useEffect`/`useCallback`/`useMemo` body that is not in its dependency array (and isn't a setter or ref). Also `[]` deps on an effect that reads props/state. Don't accept an eslint-disable of `react-hooks/exhaustive-deps` without a stated reason.

**Bad:**

```tsx
useEffect(() => {
  const id = setInterval(() => save(draft), 1000); // draft frozen at mount
  return () => clearInterval(id);
}, []); // draft missing
```

**Good:** include `draft` in deps, or use the ref/updater pattern if you deliberately want the latest without re-subscribing.

### 6. Missing effect cleanup — leaked subscriptions, timers, listeners

**Pattern.** `useEffect` subscribes, adds an event listener, opens a socket, or starts a timer, but returns no cleanup function.

**Why it bites.** Every re-run/unmount stacks another live subscription — memory leaks, duplicate handlers firing N times, and "state update on unmounted component" when a late callback sets state after the component is gone.

**Detection cue.** Inside `useEffect`: `addEventListener`, `.subscribe(`, `setInterval`, `setTimeout`, `new WebSocket`, `observe(` with no matching cleanup in a `return () => {...}`.

### 7. Fetch race — out-of-order responses render the wrong data

**Pattern.** An effect fetches based on a prop (an id, a search term) and sets state with the result, with no cancellation. When the prop changes quickly, response B (for the new id) can arrive before response A (for the old id), and A's late arrival overwrites B.

**Why it bites.** The user sees data for the wrong id/query — a real correctness bug that only shows on variable latency, never in a fast test. Classic and high-value; teammates who've hit it catch it instantly.

**Detection cue.** A `useEffect` with a dependency that changes (id, query) that calls `fetch`/an async API and calls `setState` in the `.then`, with no `AbortController` and no `let ignore = false; return () => { ignore = true }` guard.

**Good:**

```tsx
useEffect(() => {
  let ignore = false;
  fetchUser(id).then((u) => {
    if (!ignore) setUser(u);
  });
  return () => {
    ignore = true;
  };
}, [id]);
```

### 8. Derived state stored in `useState`

**Pattern.** A value that can be computed from props/other state is copied into its own `useState` and synced with an effect.

**Why it bites.** The copy drifts from its source — the effect misses an update, or renders one frame stale. The bug is a value that's _sometimes_ wrong. Should be computed during render (`const fullName = first + ' ' + last`), or memoized, not stored.

**Detection cue.** `useState` initialized from a prop, plus a `useEffect` that calls its setter when that prop changes. That pattern is almost always derived state that shouldn't be state.

### 9. `setState` from a stale value instead of the updater form

**Pattern.** `setCount(count + 1)` called multiple times in one handler, or inside an async callback / interval, instead of `setCount((c) => c + 1)`.

**Why it bites.** Batched or repeated updates all read the same stale `count`, so three increments land as one. In async callbacks the captured value is stale (see #5).

**Detection cue.** `setX(x + …)` / `setX([...x, …])` where `x` is the current state value, especially more than once per handler or inside a timer/async callback. Should use the functional updater.

### 10. List `key` = array index

**Pattern.** `items.map((item, i) => <Row key={i} … />)` on a list that can reorder, insert, or delete.

**Why it bites.** React reuses DOM/state by key; index keys make it associate the wrong row's state (input values, selection, animations) after a reorder or removal. Visible only after a mutation.

**Detection cue.** `key={index}` / `key={i}` on a list that isn't static and append-only. Use a stable domain id.

### 11. Conditional / looped hooks

**Pattern.** A hook (`useState`, `useEffect`, `useMemo`, …) called inside an `if`, early `return`, loop, or after a conditional return.

**Why it bites.** Hooks must run in the same order every render; a conditional hook corrupts React's internal hook list, causing wrong state associations or a crash on the render where the condition flips.

**Detection cue.** Any `use*` call not at the top level of the component/custom-hook body — nested in a conditional or placed after an early `return`.

---

## Angular

### 12. Unsubscribed Observable — leak and duplicate work

**Pattern.** `.subscribe(...)` in a component with no teardown — no `takeUntil(destroy$)`, no `takeUntilDestroyed()`, and not using the `async` pipe.

**Why it bites.** The subscription outlives the component; every re-creation adds another, so the callback fires N times and holds the component in memory. HTTP subscriptions may re-fire requests.

**Detection cue.** `.subscribe(` inside a component/directive without a corresponding unsubscribe in `ngOnDestroy`, a `takeUntil`/`takeUntilDestroyed` in the pipe, or an `| async` in the template. Prefer the `async` pipe, which unsubscribes automatically.

### 13. Nested `subscribe` instead of a higher-order operator

**Pattern.** `a$.subscribe(a => b$(a).subscribe(...))`.

**Why it bites.** Nested subscribes leak the inner subscription, lose cancellation, and race — a new outer value doesn't cancel the in-flight inner call, so stale responses win (the Angular analogue of #7). Should be `switchMap` (cancel previous), `mergeMap`, `concatMap`, or `exhaustMap` per intent.

**Detection cue.** A `.subscribe(` whose callback body contains another `.subscribe(`. Flag and ask which flattening operator matches the desired cancellation semantics.

### 14. Mutating an `@Input` / OnPush not detecting change

**Pattern.** Mutating an object/array `@Input` in place, or updating data by mutation in an `OnPush` component, expecting the view to refresh.

**Why it bites.** `OnPush` change detection compares references; an in-place mutation keeps the same reference, so the view never updates — a "the data changed but the screen didn't" bug. Mutating an `@Input` also corrupts the parent's state.

**Detection cue.** Assignment to a field of an `@Input` value, or `.push`/`.splice` on `@Input`/store data in a component declared `changeDetection: OnPush`. Should replace the reference (`this.items = [...this.items, x]`).

---

## Next.js (App Router)

### 15. Server/client boundary — browser API in a server component

**Pattern.** `window`, `document`, `localStorage`, `useState`/`useEffect`, or an event handler in a component that isn't marked `'use client'`; or `'use client'` slapped on a component that then can't be `async`/do server data access.

**Why it bites.** Server components run on the server where browser globals are undefined — a runtime crash on render or during build. The reverse (needless `'use client'`) ships server-only code and secrets to the browser and disables server data fetching.

**Detection cue.** `window.`/`document.`/`localStorage`/`useEffect`/`onClick` in a file with no `'use client'` at the top; or `'use client'` on a component doing DB/secret access. Also `useState`/hooks in a server component.

### 16. Stale data from default fetch caching

**Pattern.** A `fetch` in a server component for data that changes, relying on defaults, with no `cache`/`next.revalidate` set — or the opposite, `cache: 'no-store'` on data that's fine to cache, killing performance.

**Why it bites.** Next caches aggressively by default in production builds; dynamic data (prices, availability, user-specific) gets frozen and served stale to everyone. The bug never shows in `next dev` (which doesn't cache the same way) — only after deploy.

**Detection cue.** `fetch(` in a server component / route handler for user- or time-sensitive data with no explicit `{ cache: 'no-store' }` or `{ next: { revalidate: N } }`. Match the caching to the data's volatility and confirm the intent.

### 17. Secret leaked into the client bundle

**Pattern.** An API key, token, or secret read from `process.env.SOMETHING` in code that runs on the client, or exposed via a `NEXT_PUBLIC_` var.

**Why it bites.** Anything reachable from a client component (or prefixed `NEXT_PUBLIC_`) is inlined into the JS bundle and public. A leaked server secret is a security incident.

**Detection cue.** `process.env.<SECRET>` used in a `'use client'` file or passed as a prop into one; a secret named with the `NEXT_PUBLIC_` prefix. Server-only secrets must stay in server components / route handlers / server actions.

### 18. Server Action / route handler with no auth or validation

**Pattern.** A `'use server'` action or `app/**/route.ts` handler that mutates data or reads user-scoped data without checking the session and without validating the input.

**Why it bites.** Server actions and route handlers are public HTTP endpoints — anyone can call them directly, not just your form. Missing auth = any user mutates any record; missing validation = malformed input reaches the domain (same trust-boundary rule as the Nest side).

**Detection cue.** A `'use server'` function or route handler performing a write / privileged read with no session/authz check at the top and no schema validation of its arguments. Treat it exactly like a controller endpoint.
