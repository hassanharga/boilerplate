# Node.js & NestJS Failure Modes

The main skill's Correctness lens already enumerates the generic async bugs (missing `await`, unhandled promises, stale closures, races, non-atomic read-modify-write) and the concurrency/state-machine checklist covers stale-read races, state-pair preconditions, coalescing overwrites, and ordering/partial-failure. **This file adds only what those miss:** the Node execution-model _shapes_ that hide those bugs in a diff, and the NestJS-framework-specific defects that need knowledge of DI scope and lifecycle — things a generic pass has no way to know.

Each entry gives a **detection cue**: what to grep for or notice, so you can find it statically.

## Contents

**Node async — detection cues** (the bugs themselves are in the skill's Correctness lens; these are how they look)

- A. Floating promise / `forEach(async …)`
- B. `.catch(() => {})` — the async rejection black hole
- C. Unhandled rejection outside the request pipeline

**NestJS lifecycle & DI** (not derivable from the generic lenses)

- 1. Request state stored on a singleton provider
- 2. Async lifecycle hook not awaited
- 3. `@OnEvent` / message handler swallows failure past the retry mechanism
- 4. Guard / interceptor returns the wrong shape or doesn't block
- 5. Validation missing at the trust boundary

---

## Node async — detection cues

### A. Floating promise / `forEach(async …)`

**Shape.** A call to a known-async method (`this.repo.save(...)`, `this.emitter.emit(...)`, `this.client.publish(...)`) on its own statement line with no leading `await`/`return` and no `.then`/`.catch` — or the token sequence `.forEach(async` (which ignores every returned promise). Execution continues before the work finishes; a rejection vanishes or surfaces later as a detached unhandled rejection.

**Why it bites.** The happy path passes because the op usually finishes in time; under load or on error the caller reports success while the write never happened. The missing token is one word, so it is easy to skim past — especially inside constructors, `forEach`, event handlers, and `setTimeout`/`setInterval` callbacks.

**Detection cue.** Async call with no `await`/`return`/`.catch`; `.forEach(async`. `array.map(async …)` is fine only when wrapped in `await Promise.all(...)`.

### B. `.catch(() => {})` — the async rejection black hole

**Shape.** A promise chain ending in `.catch` with an empty or log-only handler that lets execution continue as if it succeeded.

**Why it bites.** A failed publish/save/terminate is swallowed, the retry mechanism (BullMQ, envelope resubmission) never fires, and the entity is stranded in a non-terminal state. This is the async twin of the swallowed-error failure mode — the same "false success" hazard the terminal-branch-symmetry check targets, but hidden in a `.catch`.

**Detection cue.** `.catch(` followed by `() => {}`, `() => null`, or a bare `logger.warn(...)` with no rethrow / no failure propagation. Confirm the caller can still tell success from swallowed failure.

### C. Unhandled rejection outside the request pipeline

**Shape.** Async work kicked off in a constructor, `setInterval`, a cron callback, or an EventEmitter listener — outside the request/response cycle Nest's exception filters wrap.

**Why it bites.** Nest's filters only cover the request pipeline. A rejection in a timer or emitter callback becomes a process-level `unhandledRejection`, decoupled from its origin, and can crash or silently no-op depending on process config.

**Detection cue.** `async` callbacks passed to `setInterval`/`setTimeout`/`.on(...)`/scheduling APIs, or async work in a constructor, with no local try/catch.

---

## NestJS lifecycle & DI

### 1. Request state stored on a singleton provider

**Pattern.** A default-scoped (singleton) `@Injectable()` stores per-request data on an instance field — `this.currentUser`, `this.tenantId`, `this.context` — set at the start of a request and read later.

**Why it bites.** Nest providers are singletons by default: one instance shared across every concurrent request. Instance fields set by request A are visible to request B — cross-tenant data bleed, the wrong user's data returned. It passes every single-request test and fails only under concurrency, so it reaches production. Generic reviews never flag it because the code reads fine in isolation.

**Detection cue.** Assignment to `this.<field>` of request-derived data (user, tenant, headers, params) inside a provider method, where a _different_ method reads it. Legit only if the provider is explicitly `@Injectable({ scope: Scope.REQUEST })` — check the decorator.

**Bad:**

```ts
@Injectable()
export class DispatchService {
  private currentDriverId: string; // shared across all requests
  setDriver(id: string) {
    this.currentDriverId = id;
  }
  dispatch() {
    return this.run(this.currentDriverId);
  }
}
```

**Good:** pass the value through the call (`dispatch(driverId)`), use `AsyncLocalStorage`/`nestjs-cls`, or make the provider `Scope.REQUEST` only if there's a real reason (note it forces the injection chain request-scoped).

### 2. Async lifecycle hook not awaited internally

**Pattern.** `onModuleInit` / `onApplicationBootstrap` starts async setup (warm a cache, open a connection, register consumers) but doesn't `await` it, or fires it and returns.

**Why it bites.** Nest only waits for the promise the hook _returns_. Un-awaited setup races with the first incoming request — the app serves traffic before it's ready, producing intermittent "not connected" / empty-cache errors on cold start.

**Detection cue.** Inside `onModuleInit`/`onApplicationBootstrap`, a floating async call or a fire-and-forget `.then(...)`. The hook should be `async` and `await` its setup.

### 3. `@OnEvent` / message handler swallows failure past the retry mechanism

**Pattern.** An event or queue handler does work that can fail but returns/resolves normally on the failure path — or is `@OnEvent` (fire-and-forget) when it needed at-least-once delivery.

**Why it bites.** `@nestjs/event-emitter` `@OnEvent` handlers are fire-and-forget: a throw is not delivered back to the emitter and triggers no retry. If work that must not be lost sits behind `@OnEvent` instead of a durable queue (BullMQ), a failure disappears silently and the entity never reaches its terminal state. Even on a queue, a handler that catches-and-resolves defeats the redelivery it was added to get.

**Detection cue.** `@OnEvent(` decorating a method that performs a persistence write or external call whose loss matters; or a queue processor whose catch block logs and returns instead of rethrowing to trigger nack/retry.

### 4. Guard / interceptor returns the wrong shape or doesn't block

**Pattern.** A `CanActivate` guard returning a truthy non-boolean (e.g. the user object) so it always "passes"; an interceptor that forgets to `return next.handle()` or swallows the stream.

**Why it bites.** A guard meant to enforce authz silently authorizes everyone; an interceptor meant to wrap every response drops it. Security- and correctness-critical, and it looks like working code.

**Detection cue.** A `canActivate` returning something other than `boolean`/`Promise<boolean>`/`Observable<boolean>`; an `intercept` with no `return next.handle()`. Verify the guard actually denies on the negative path — ask for the test that proves a forbidden caller is rejected.

### 5. Validation missing at the trust boundary

**Pattern.** A DTO with no `class-validator` decorators, or a controller not behind a `ValidationPipe` with `whitelist: true`, so unvalidated/extra fields flow into domain logic. Or `@Query`/`@Param` values used as numbers with no `ParseIntPipe` (they arrive as strings).

**Why it bites.** Malformed or extra input reaches the domain; string-vs-number confusion produces `"1" + 1 === "11"`-class bugs and DB filters that never match. The boundary is the one place to reject bad input; skipping it pushes failures deep into the system where they're mislabeled.

**Detection cue.** A new DTO with plain fields and no validators; a numeric query/param used in arithmetic or a filter without a transform pipe. Check `whitelist: true` strips unknown fields.
