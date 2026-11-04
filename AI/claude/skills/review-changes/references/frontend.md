# Frontend Review Prompts

Use this reference for React, Next.js, Angular, and browser-facing changes.
These are investigation prompts, not framework contracts. Before making a
version-sensitive claim, identify the installed framework, router, rendering
mode, and relevant configuration, then verify the behavior against official
documentation or source for that version.

## React state and effects

- Check every effect/callback dependency against values read in its body, while
  respecting stable references and the project’s hooks tooling.
- Async effects need stale-response protection when a later request can finish
  first: abort, request identity, or another proven guard.
- Timers, listeners, observers, sockets, and subscriptions need symmetrical
  teardown when their lifetime can outlive the component.
- `useState(prop)` is a one-time initializer. It is a defect only when the
  component contract says later prop changes must reset local state and no
  remount or explicit synchronization implements that behavior. Do not require
  a `key` or reject an effect categorically; judge the intended UX and render
  semantics.
- For shared-component extraction, compare the original caller’s defaults,
  labels, locale strings, disabled states, and callbacks so reuse does not
  silently change behavior.

For per-row async work, inspect N+1 requests, response ordering, keying, and
cardinality. Recommend batching or concurrency control only when the expected
scale and backend contract justify it.

## Next.js version gates

App Router, Pages Router, data caching, and route output behavior can differ by
version and configuration. For the pinned version, verify:

- the default and explicit caching behavior of server `fetch`, Route Handlers,
  and route output;
- whether `params` and `searchParams` are synchronous, asynchronous, or support
  a compatibility form in the changed API;
- whether a mutation affects a cached read and, if so, which revalidation or
  invalidation mechanism applies;
- whether route-segment options, runtime choice, deployment platform, or
  dynamic APIs change the default.

Do not infer stale data from a missing cache option alone. Trace the affected
read and prove its effective caching behavior first.

Trace client/server imports. Client code must not import secret-bearing values,
database clients, filesystem APIs, or server-only request APIs. Type-only imports
are normally erased, but verify unusual build configurations before asserting a
bundle leak.

Use Suspense and parallel fetching recommendations only with a demonstrated
loading or latency consequence. Sequential work can be required by dependency,
backpressure, or rate limits.

## Angular security and reactivity

For the installed Angular version and the changed binding context, verify what
the framework sanitizes, escapes, trusts, or rejects. An HTML binding alone is
not proof of exploitable XSS. Trace attacker-controlled input to the actual sink
and verify whether a trust-bypass API, direct DOM API, third-party HTML sink,
resource URL, or dynamic template defeats the applicable protection.

Treat `bypassSecurityTrust*` calls as a prompt for deeper source-to-sink review,
not as a sanitizer or proof of exploitation.

For subscriptions, determine whether the observable completes naturally or is
managed by the async pipe/framework helper before requiring teardown. With
`OnPush`, check whether changed state replaces references or otherwise triggers
change detection; mutation is a problem when the view can remain stale.

## Browser injection

Trace untrusted input to executable or HTML/URL sinks:

- React `dangerouslySetInnerHTML`;
- direct `innerHTML`, `insertAdjacentHTML`, `document.write`;
- `eval`, `new Function`, dynamically compiled templates;
- `javascript:` or attacker-controlled resource URLs.

Require a context-appropriate sanitizer or safe construction method supported by
the project. Do not prescribe one library universally. A framework bypass or
“trusted” wrapper is evidence requiring more scrutiny, not proof of safety.

## Accessibility and user behavior

Review keyboard reachability, focus behavior, semantic roles, labels, loading,
error and empty states, and disabled controls when the change affects user
interaction. Tie findings to a blocked user journey or acceptance criterion;
avoid generic accessibility checklists without a concrete changed-line impact.

## Review path for frontend changes

A frontend flow usually starts with a user action or a navigation, not a request.
Pick the entry point the user touches first: the route or page that renders the
changed screen, or the event handler for the changed interaction. Then order the
stops the way the UI runs:

1. route, page, or layout that mounts the changed component;
2. the handler or form submit the user triggers;
3. local state, store, or query-cache update;
4. the API call and how its response, error, and loading states are handled;
5. what renders as a result: success, empty, error, and disabled states.

Put shared components after the screen that uses them, so the reviewer judges
the component against a real caller. Put styles, snapshots, translation files,
and generated API clients on the Skim line unless they carry the changed
behavior.
