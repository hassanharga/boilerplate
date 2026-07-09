# Angular Interview Reference

A senior-focused reference covering modern Angular: standalone architecture, signals, the new control flow, forms, routing, SSR, testing, and the signal-first APIs introduced through **Angular v22** (June 2026). Concept + code snippet format. Assumes Angular 17+ defaults (standalone, esbuild/Vite, new control flow) unless noted.

---

## Table of Contents

### Part 1: Angular Core
1. [Architecture & Bootstrapping](#1-architecture--bootstrapping)
2. [Components & Templates](#2-components--templates)
3. [Standalone Components & APIs](#3-standalone-components--apis)
4. [Dependency Injection](#4-dependency-injection)
5. [Directives](#5-directives)
6. [Pipes](#6-pipes)
7. [Built-in Control Flow](#7-built-in-control-flow)
8. [Deferrable Views (`@defer`)](#8-deferrable-views-defer)
9. [Lifecycle Hooks](#9-lifecycle-hooks)
10. [Content Projection](#10-content-projection)

### Part 2: Reactivity & Change Detection
11. [Signals — Fundamentals](#11-signals--fundamentals)
12. [Signal Inputs, Outputs & Queries](#12-signal-inputs-outputs--queries)
13. [`linkedSignal` & the Resource API](#13-linkedsignal--the-resource-api)
14. [RxJS Interop](#14-rxjs-interop)
15. [Change Detection & Zoneless](#15-change-detection--zoneless)

### Part 3: Data & Forms
16. [HttpClient & Interceptors](#16-httpclient--interceptors)
17. [`httpResource`](#17-httpresource)
18. [Reactive & Template-Driven Forms](#18-reactive--template-driven-forms)
19. [Signal Forms](#19-signal-forms)

### Part 4: Routing & SSR
20. [Router](#20-router)
21. [SSR, Hydration & Incremental Hydration](#21-ssr-hydration--incremental-hydration)

### Part 5: Testing & Tooling
22. [Testing](#22-testing)
23. [Performance & Optimization](#23-performance--optimization)

### Part 6: What's New
24. [Version Timeline: v17 → v22](#24-version-timeline-v17--v22)
25. [Angular v22 Deep Dive](#25-angular-v22-deep-dive)

---

# Part 1: Angular Core

---

## 1. Architecture & Bootstrapping

Angular is a component-based framework built on TypeScript. The modern app is **standalone-first** — `NgModule` is no longer required (and as of v19 components/directives/pipes are standalone by default; you no longer write `standalone: true`).

### Bootstrapping a standalone app

```ts
// main.ts
import { bootstrapApplication } from '@angular/platform-browser';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { App } from './app/app';
import { routes } from './app/app.routes';

bootstrapApplication(App, {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
  ],
});
```

`bootstrapApplication` replaces `platformBrowserDynamic().bootstrapModule(AppModule)`. Application-wide services and features are wired through `provideX()` functions instead of a root module's `imports`/`providers`.

### NgModule vs Standalone

| | NgModule era | Standalone era |
|---|---|---|
| Declaration | `declarations: [...]` in a module | nothing — components declare their own `imports` |
| Sharing | `SharedModule` re-exports | import the component/pipe directly |
| Root config | `AppModule` + `@NgModule` | `bootstrapApplication` + `provideX()` |
| Lazy loading | `loadChildren: () => import().then(m => m.Mod)` | `loadComponent` / `loadChildren` returning routes |

NgModules still work for backward compatibility, but new code uses standalone.

---

## 2. Components & Templates

A component is a class decorated with `@Component`, pairing a TypeScript class with an HTML template and styles.

```ts
import { Component, signal } from '@angular/core';

@Component({
  selector: 'app-counter',
  template: `
    <button (click)="dec()">-</button>
    <span>{{ count() }}</span>
    <button (click)="inc()">+</button>
  `,
  styles: `span { font-weight: bold; }`,
})
export class Counter {
  count = signal(0);
  inc() { this.count.update(c => c + 1); }
  dec() { this.count.update(c => c - 1); }
}
```

### Template binding syntax

| Syntax | Direction | Example |
|---|---|---|
| `{{ expr }}` | interpolation (one-way → DOM) | `{{ user.name }}` |
| `[prop]="expr"` | property binding | `[disabled]="isBusy()"` |
| `(event)="handler()"` | event binding | `(click)="save()"` |
| `[(ngModel)]="x"` | two-way (banana-in-a-box) | needs `FormsModule` |
| `[class.x]` / `[style.x]` | class/style binding | `[class.active]="isActive()"` |
| `#ref` | template reference variable | `<input #email>` → `email.value` |

Two-way binding `[(x)]` is sugar for `[x]="v"` + `(xChange)="v = $event"`.

---

## 3. Standalone Components & APIs

A standalone component imports exactly what its template uses — no module indirection.

```ts
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { UpperCasePipe } from '@angular/common';
import { UserCard } from './user-card';

@Component({
  selector: 'app-users',
  imports: [RouterLink, UpperCasePipe, UserCard], // only what the template references
  template: `
    <a routerLink="/new">Add</a>
    <app-user-card [name]="(name | uppercase)" />
  `,
})
export class Users {}
```

### Providing services / features

`provideX` functions are the standalone replacement for module `providers` and `forRoot()`:

- `provideRouter(routes, withComponentInputBinding(), withViewTransitions())`
- `provideHttpClient(withInterceptors([...]), withFetch())`
- `provideClientHydration(withIncrementalHydration())`
- `provideAnimationsAsync()` (lazy animations)

---

## 4. Dependency Injection

Angular's DI is hierarchical: injectors form a tree mirroring the component tree, plus a root (application) injector.

### `inject()` vs constructor injection

The functional `inject()` is now idiomatic — it works in field initializers, factory functions, route guards, and interceptors where constructor params can't reach.

```ts
import { inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export class UserService {
  private http = inject(HttpClient); // preferred over constructor(private http: HttpClient)
}
```

### Provider scopes

```ts
@Injectable({ providedIn: 'root' }) // tree-shakeable app-wide singleton
export class Logger {}

// Component-scoped instance (new instance per component subtree)
@Component({ providers: [LocalState] })
export class Panel {}
```

### Injection tokens & multi-providers

```ts
export const API_URL = new InjectionToken<string>('API_URL');

providers: [
  { provide: API_URL, useValue: 'https://api.example.com' },
  { provide: Logger, useClass: ProdLogger },
  { provide: VALIDATORS, useValue: emailValidator, multi: true }, // accumulates into an array
]
```

`useClass`, `useValue`, `useExisting` (alias), `useFactory` (with `deps`) cover the resolution strategies. Resolution modifiers: `@Optional()`, `@Self()`, `@SkipSelf()`, `@Host()` (or the `inject(X, { optional: true, skipSelf: true })` options form).

---

## 5. Directives

Three kinds: **components** (directives with a template), **attribute** directives (change appearance/behavior), **structural** directives (change layout via `*`).

### Attribute directive with host bindings

```ts
import { Directive, ElementRef, inject, input, HostListener } from '@angular/core';

@Directive({ selector: '[appHighlight]' })
export class Highlight {
  color = input('yellow');
  private el = inject(ElementRef);

  @HostListener('mouseenter') onEnter() {
    this.el.nativeElement.style.background = this.color();
  }
  @HostListener('mouseleave') onLeave() {
    this.el.nativeElement.style.background = '';
  }
}
```

Prefer the `host` metadata object for static bindings:

```ts
@Directive({
  selector: '[appHighlight]',
  host: { '[style.background]': 'color()', '(click)': 'toggle()' },
})
```

### Directive composition API

A component/directive can apply other directives via `hostDirectives` — composition without inheritance:

```ts
@Component({
  selector: 'app-menu',
  hostDirectives: [{ directive: CdkMenu, inputs: ['cdkMenuOrientation: orientation'] }],
})
export class Menu {}
```

---

## 6. Pipes

Pipes transform values in templates. Standalone and pure by default (recomputed only when the input reference changes).

```ts
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'truncate' }) // pure: true is the default
export class Truncate implements PipeTransform {
  transform(value: string, limit = 20): string {
    return value.length > limit ? value.slice(0, limit) + '…' : value;
  }
}
```

Built-ins: `async` (subscribes/unsubscribes to Observables/Promises), `date`, `currency`, `json`, `keyvalue`, `slice`. The `| async` pipe is the canonical way to render Observables without manual subscription.

**Impure pipes** (`pure: false`) run on every change-detection cycle — use sparingly; signals/`computed` are usually a better fit.

---

## 7. Built-in Control Flow

Since v17, Angular has a built-in block control-flow syntax that replaces `*ngIf`, `*ngFor`, `*ngSwitch`. It's faster, type-checked, and needs no imports. (A migration schematic, `ng generate @angular/core:control-flow`, converts the old directives.)

### `@if` / `@else`

```html
@if (user(); as u) {
  <p>Welcome {{ u.name }}</p>
} @else if (loading()) {
  <spinner />
} @else {
  <p>Not signed in</p>
}
```

### `@for` (mandatory `track`)

```html
@for (item of items(); track item.id) {
  <li>{{ item.name }}</li>
} @empty {
  <li>No items</li>
}
```

`track` is **required** — it replaces `trackBy` and is the single biggest list-perf lever (avoids destroying/recreating DOM on reorder). Contextual variables: `$index`, `$first`, `$last`, `$even`, `$odd`, `$count`.

### `@switch`

```html
@switch (status()) {
  @case ('active') { <badge-green /> }
  @case ('paused') { <badge-amber /> }
  @default { <badge-grey /> }
}
```

### `@let` (template-local variables, v18+)

```html
@let total = price() * qty();
<p>Total: {{ total | currency }}</p>
```

`@let` is read-only in the template and reactive — it re-evaluates when its dependencies change.

---

## 8. Deferrable Views (`@defer`)

`@defer` lazily loads a block's components, directives, pipes (and their dependencies) and renders it only when a trigger fires — built-in code-splitting with zero router/lazy-module plumbing.

```html
@defer (on viewport; prefetch on idle) {
  <heavy-chart [data]="data()" />
} @placeholder (minimum 500ms) {
  <p>Chart will load when scrolled into view</p>
} @loading (after 100ms; minimum 1s) {
  <spinner />
} @error {
  <p>Failed to load chart</p>
}
```

**Triggers:** `on idle` (default), `on viewport`, `on interaction`, `on hover`, `on timer(2s)`, `on immediate`, plus `when <expr>` for a custom boolean. `prefetch` fetches the bundle ahead of render. Deferred dependencies that are *only* used inside `@defer` are split into their own chunk.

---

## 9. Lifecycle Hooks

Order on a typical component:

1. `constructor` — DI only, no inputs yet.
2. `ngOnChanges(changes)` — on decorator-`@Input` changes (not fired for signal inputs).
3. `ngOnInit` — once, after first inputs bound.
4. `ngDoCheck` — every change-detection run (custom dirty checks).
5. `ngAfterContentInit` / `ngAfterContentChecked` — projected content.
6. `ngAfterViewInit` / `ngAfterViewChecked` — own view & child views ready.
7. `ngOnDestroy` — cleanup (unsubscribe, clear timers).

### Modern alternatives

- `afterNextRender` / `afterRender` — run code after the DOM is painted (browser-only; safe for direct DOM/measurement, skipped on the server).
- `effect()` — react to signal changes; replaces a lot of `ngOnChanges`/`ngDoCheck` logic.
- `takeUntilDestroyed()` — auto-unsubscribe tied to the injection context, removing most `ngOnDestroy` boilerplate.

```ts
import { afterNextRender, DestroyRef, inject } from '@angular/core';

afterNextRender(() => chart.measure()); // DOM is ready & painted
inject(DestroyRef).onDestroy(() => clearInterval(this.timer));
```

---

## 10. Content Projection

`<ng-content>` projects markup from the parent into the component (slot-based, like web-component slots).

```ts
@Component({
  selector: 'app-card',
  template: `
    <header><ng-content select="[card-title]" /></header>
    <section><ng-content /></section> <!-- default slot -->
  `,
})
export class Card {}
```

```html
<app-card>
  <h2 card-title>Title</h2>
  <p>Body goes into the default slot.</p>
</app-card>
```

`select` accepts CSS selectors. `ng-container` is a logical grouping element that renders no DOM. `ng-template` defines a template fragment instantiated via `ngTemplateOutlet` or structural directives.

---

# Part 2: Reactivity & Change Detection

---

## 11. Signals — Fundamentals

Signals (stable since v16/v17, core primitives stable in v20) are reactive values that track their readers. They are the foundation of Angular's modern, fine-grained reactivity and zoneless future.

```ts
import { signal, computed, effect } from '@angular/core';

const count = signal(0);              // WritableSignal<number>
const double = computed(() => count() * 2); // derived, memoized, read-only

count.set(5);                          // replace
count.update(c => c + 1);              // derive from current

effect(() => console.log('count is', count())); // runs now + whenever count changes
```

- **`signal(initial)`** — read with `count()`, write with `.set()` / `.update()`.
- **`computed(fn)`** — lazily evaluated, memoized; recomputes only when a dependency it actually read changes.
- **`effect(fn)`** — side effects; auto-tracks dependencies, runs after render, auto-cleans on destroy. Don't set signals inside an effect to drive state (use `computed`); reserve effects for syncing to non-reactive sinks (logging, `localStorage`, third-party libs).
- **`untracked(fn)`** — read a signal inside a `computed`/`effect` *without* subscribing to it.

Equality: signals use `Object.is` by default; pass `{ equal }` for custom comparison to suppress no-op notifications.

**Why signals matter:** they enable change detection to update only the views that read a changed signal, instead of dirty-checking the whole tree — the basis for zoneless apps.

---

## 12. Signal Inputs, Outputs & Queries

Signal-based component APIs (stable in v19) replace the `@Input()`/`@Output()`/`@ViewChild()` decorators.

```ts
import {
  input, output, model, viewChild, viewChildren, contentChild,
} from '@angular/core';

export class UserCard {
  // Inputs are read-only signals
  name = input.required<string>();        // required input
  role = input('member');                  // with default → Signal<string>
  id = input(0, { transform: numberAttribute });

  // Output is an emitter (no more EventEmitter import needed)
  selected = output<string>();

  // Two-way binding: pairs an input with a `<name>Change` output automatically
  expanded = model(false);                 // [(expanded)] in the parent

  // Queries return signals
  header = viewChild<ElementRef>('header');         // Signal<ElementRef | undefined>
  items = viewChildren(ItemComponent);              // Signal<readonly ItemComponent[]>
  projected = contentChild(IconComponent);

  pick() { this.selected.emit(this.name()); }
}
```

| Decorator (legacy) | Signal API |
|---|---|
| `@Input()` | `input()` / `input.required()` |
| `@Output()` | `output()` |
| `@Input()` + `@Output()` (two-way) | `model()` |
| `@ViewChild` / `@ViewChildren` | `viewChild()` / `viewChildren()` |
| `@ContentChild` / `@ContentChildren` | `contentChild()` / `contentChildren()` |

Signal inputs don't trigger `ngOnChanges`; react to them with `computed`/`effect` instead. Query signals resolve after view init and update reactively.

---

## 13. `linkedSignal` & the Resource API

### `linkedSignal` (stable v20)

A writable signal that **resets to a computed value** when its source changes, but can also be locally overridden. Ideal for "editable copy of derived/async data" and selection state.

```ts
import { linkedSignal } from '@angular/core';

// Selected option resets when the list changes, but the user can still override it
const options = signal(['a', 'b', 'c']);
const choice = linkedSignal(() => options()[0]);

choice.set('b');          // local override
options.set(['x', 'y']);  // resets choice to 'x'
```

Advanced form with `source` + `computation` (access the previous value):

```ts
const choice = linkedSignal({
  source: options,
  computation: (opts, prev) =>
    opts.includes(prev?.value as string) ? prev!.value : opts[0],
});
```

### Resource API (`resource` / `rxResource`) — stable in v22

`resource` runs an async loader when its reactive `params` change and exposes the result as signals (`value`, `status`, `error`, `isLoading`). It became **stable in Angular v22** (experimental in v19–v21).

```ts
import { resource, signal } from '@angular/core';

const userId = signal(1);

const userResource = resource({
  params: () => ({ id: userId() }),          // reactive — re-runs loader on change
  loader: async ({ params, abortSignal }) => {
    const res = await fetch(`/api/users/${params.id}`, { signal: abortSignal });
    return res.json();
  },
});

userResource.value();      // the data signal
userResource.isLoading();  // boolean signal
userResource.error();      // error signal
userResource.reload();     // re-trigger manually
```

Key behaviors:
- If `params` returns `undefined`, the loader is skipped and status becomes `'idle'`.
- A pending request is **aborted** (via `abortSignal`) when params change again.
- Since v20, reading `.value()` while in the error state throws — guard with `hasValue()`.
- `rxResource` is the same idea with an RxJS `stream`/Observable loader.

---

## 14. RxJS Interop

Angular still uses RxJS heavily (HttpClient, router events, forms valueChanges). `@angular/core/rxjs-interop` bridges Observables and signals.

```ts
import { toSignal, toObservable, takeUntilDestroyed } from '@angular/core/rxjs-interop';

// Observable → Signal (auto-subscribes, auto-unsubscribes on destroy)
readonly user = toSignal(this.http.get<User>('/me'), { initialValue: null });

// Signal → Observable
readonly query$ = toObservable(this.query);

// Auto-unsubscribe without ngOnDestroy
this.ticks$.pipe(takeUntilDestroyed()).subscribe(/* ... */);
```

- `toSignal` needs an `initialValue` (or yields `undefined` until first emission); it's a synchronous read of the latest emission.
- `takeUntilDestroyed()` ties teardown to the current injection context — call it in a field initializer/constructor, or pass an explicit `DestroyRef`.

**Rule of thumb:** signals for synchronous derived state; RxJS for event streams, complex async composition (debounce, switchMap, retry).

---

## 15. Change Detection & Zoneless

### Classic Zone.js change detection

Historically Angular patched async APIs (`setTimeout`, events, XHR) via **zone.js** to know *when* to run change detection, then dirty-checked the component tree top-down.

### `ChangeDetectionStrategy.OnPush`

`OnPush` skips a component's subtree unless: an `@Input`/signal it reads changed, an event fired in it, an `async` pipe emitted, or `markForCheck()` was called. It's the standard performance strategy.

```ts
@Component({ changeDetection: ChangeDetectionStrategy.OnPush, /* ... */ })
```

> **v22 change:** components **without** an explicit `changeDetection` now default to `OnPush`. `ng update` adds `ChangeDetectionStrategy.Eager` to existing components to preserve old always-check behavior. (`Eager` is the new name for the legacy default.)

### Zoneless (default in v21)

Zoneless removes zone.js entirely. Change detection is driven by explicit signals: signal writes, `markForCheck`, `async` pipe, template event bindings, and `AfterRenderRef`. Benefits: smaller bundle, cleaner stack traces, no needless CD cycles, better Core Web Vitals.

```ts
import { provideZonelessChangeDetection } from '@angular/core';

bootstrapApplication(App, {
  providers: [provideZonelessChangeDetection()],
});
```

Zoneless was experimental in v18, stable in v20.2, and the **default for new projects in v21** (existing apps keep zone.js until they opt out). Going zoneless effectively requires signal-driven (or OnPush + `async`) components so CD knows what changed.

---

# Part 3: Data & Forms

---

## 16. HttpClient & Interceptors

`provideHttpClient()` registers `HttpClient`, which returns cold Observables.

```ts
import { HttpClient } from '@angular/common/http';

export class UserApi {
  private http = inject(HttpClient);
  getUser(id: number) {
    return this.http.get<User>(`/api/users/${id}`);
  }
  save(u: User) {
    return this.http.post<User>('/api/users', u, { headers: { 'X-Trace': '1' } });
  }
}
```

### Functional interceptors

```ts
import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = inject(AuthStore).token();
  return next(token ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }) : req);
};

provideHttpClient(withInterceptors([authInterceptor]), withFetch());
```

`withFetch()` switches to the Fetch API backend (better for SSR/streaming). Other features: `withInterceptorsFromDi()`, `withJsonpSupport()`. The **transfer cache** (SSR) is configured via `withHttpTransferCache()` — and as of v22 it skips `withCredentials`/cookie-bearing requests so user-specific responses don't leak into transferred state.

---

## 17. `httpResource`

`httpResource` (stable in v22) is a signal-native wrapper over `HttpClient`: request status and response are exposed as signals, and it **re-fetches automatically** when a reactive dependency changes.

```ts
import { httpResource } from '@angular/common/http';

const filter = signal({ from: 'GRZ', to: 'FRA' });

const flights = httpResource<Flight[]>(
  () => ({
    url: 'https://api.example.com/flight',
    params: { from: filter().from, to: filter().to },
  }),
  { defaultValue: [] },
);
```

```html
@if (flights.isLoading()) {
  <spinner />
} @else if (flights.error()) {
  <p>Failed to load</p>
} @else {
  @for (f of flights.value(); track f.id) {
    <flight-card [item]="f" />
  }
}
```

- Reactive: changing `filter()` issues a new request and **cancels** any in-flight one.
- Requires `provideHttpClient()`; supports interceptors like any HttpClient call.
- Parses JSON by default; use `httpResource.text()`, `.blob()`, `.arrayBuffer()` for other types.
- `parse` option integrates schema validators (Zod/Valibot) and the parse return type becomes the value type.
- Reading `value()` in an error state throws — guard with `hasValue()`.

**`httpResource` vs `HttpClient.get()`:** use `httpResource` for declarative, signal-driven reads tied to UI state; use `HttpClient` directly for imperative one-shot calls, mutations (POST/PUT), and complex RxJS pipelines.

---

## 18. Reactive & Template-Driven Forms

Two classic systems coexist (and Signal Forms is the third — see next section).

### Reactive forms (explicit, typed)

```ts
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';

@Component({ imports: [ReactiveFormsModule], /* ... */ })
export class SignupForm {
  private fb = inject(FormBuilder);
  form = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
  });

  submit() {
    if (this.form.valid) console.log(this.form.getRawValue()); // strongly typed
  }
}
```

```html
<form [formGroup]="form" (ngSubmit)="submit()">
  <input formControlName="email" />
  @if (form.controls.email.invalid && form.controls.email.touched) {
    <small>Valid email required</small>
  }
  <button [disabled]="form.invalid">Sign up</button>
</form>
```

Forms are **strictly typed** since v14. `valueChanges`/`statusChanges` are Observables (combine with `toSignal`).

### Template-driven (simple, `ngModel`)

```html
<form #f="ngForm" (ngSubmit)="save(f.value)">
  <input name="email" [(ngModel)]="email" required email />
</form>
```

| | Reactive | Template-driven |
|---|---|---|
| Source of truth | component class | template |
| Validation | functions in code | directives in template |
| Best for | complex, dynamic, testable forms | small/simple forms |

---

## 19. Signal Forms

Signal Forms (`@angular/forms/signals`) are a brand-new, signal-native forms system — **experimental in v21, stable in v22**. The form structure is *derived from a writable signal model*; values, validation, and submission state are all signals.

```ts
import { Component, signal } from '@angular/core';
import { form, FormField, required, email, minLength } from '@angular/forms/signals';

interface LoginData { email: string; password: string; }

@Component({
  selector: 'app-login',
  imports: [FormField],
  template: `
    <input [formField]="loginForm.email" />
    @if (loginForm.email().touched() && !loginForm.email().valid()) {
      <small>{{ loginForm.email().errors() | json }}</small>
    }
    <input type="password" [formField]="loginForm.password" />
  `,
})
export class Login {
  model = signal<LoginData>({ email: '', password: '' });

  loginForm = form(this.model, (path) => {
    required(path.email, { message: 'Email is required' });
    email(path.email, { message: 'Enter a valid email' });
    required(path.password);
    minLength(path.password, 8);
  });
}
```

### Structure vs state — the key mental model

- `loginForm.email` → a **FormField** (structural; bind it with `[formField]`).
- `loginForm.email()` → a **FieldState** — call it to access signals: `.value()`, `.valid()`, `.touched()`, `.errors()`, `.pending()`.

```ts
loginForm.email().value();              // read
loginForm.email().value.set('a@b.com'); // write (updates field AND the model signal)
```

### Validators & schema logic

Built-ins: `required`, `email`, `min`/`max`, `minLength`/`maxLength`, `pattern`. All rules run on every change (no short-circuit). Conditional and composed logic:

```ts
import { schema, applyWhen, disabled, validateAsync } from '@angular/forms/signals';

// Conditional validation (the `when` option exists on required)
required(path.promoCode, { when: ({ valueOf }) => valueOf(path.applyDiscount) });

// Other field rules
disabled(path.password, { when: ({ valueOf }) => !valueOf(path.createAccount) });

// Reusable schema
const addressSchema = schema<Address>((a) => {
  required(a.street); required(a.city); pattern(a.zip, /^\d{5}$/);
});

// Whole rule-set applied conditionally (re-evaluated reactively)
applyWhen(path, ({ valueOf }) => valueOf(path.country) === 'US',
  (p) => { required(p.zip); pattern(p.zip, /^\d{5}(-\d{4})?$/); });
```

Async validation uses `validateAsync()` (the `onError` handler is required); sync rules must pass before async ones run (`pending()` is true meanwhile).

### Submission

```ts
import { FormRoot, submit } from '@angular/forms/signals';

loginForm = form(this.model, loginSchema, {
  submission: {
    action: async (f) => this.api.login(f),
    onInvalid: (f) => this.report(f),
  },
});
```

```html
<form [formRoot]="loginForm">
  <!-- fields -->
  <button>Sign in</button>
</form>
```

**Why Signal Forms:** they unify the strong typing of reactive forms, the ergonomics of template-driven forms, and signal reactivity into one declarative, composable model — and they fit naturally into zoneless apps.

---

# Part 4: Routing & SSR

---

## 20. Router

Routes are plain config arrays, registered via `provideRouter`.

```ts
export const routes: Routes = [
  { path: '', component: Home },
  {
    path: 'users/:id',
    loadComponent: () => import('./user-detail').then(m => m.UserDetail), // lazy
    canActivate: [authGuard],
    resolve: { user: userResolver },
  },
  {
    path: 'admin',
    loadChildren: () => import('./admin/routes').then(m => m.ADMIN_ROUTES), // lazy child routes
  },
  { path: '**', component: NotFound },
];
```

### Functional guards & resolvers

```ts
import { CanActivateFn, ResolveFn, Router } from '@angular/router';

export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthStore);
  return auth.isLoggedIn() || inject(Router).createUrlTree(['/login']);
};

export const userResolver: ResolveFn<User> = (route) =>
  inject(UserApi).getUser(Number(route.paramMap.get('id')));
```

Guard types: `CanActivateFn`, `CanActivateChildFn`, `CanDeactivateFn`, `CanMatchFn` (gate lazy loading), and the function form of resolvers. Class-based guards are deprecated in favor of these.

### Route params as component inputs

```ts
provideRouter(routes, withComponentInputBinding());
```

```ts
// path: 'users/:id' → `id` is bound directly to an input
export class UserDetail {
  id = input.required<string>(); // route param, query param, and resolved data all bind to inputs
}
```

Other features: `withViewTransitions()` (View Transitions API), `withInMemoryScrolling()`, `withHashLocation()`, `withPreloading(PreloadAllModules)`.

> **v22:** route parameter inheritance from *all* parent routes is the default; route injectors are auto-cleaned up; a reactive `isActive()` signal helper is available.

---

## 21. SSR, Hydration & Incremental Hydration

`ng add @angular/ssr` sets up server-side rendering (Angular Universal is now folded into `@angular/ssr`).

### Hydration

`provideClientHydration()` enables **non-destructive hydration** — the client reuses server-rendered DOM instead of re-rendering it from scratch (no flicker, preserves first paint). Combine with `provideHttpClient(withFetch())` and the transfer cache to avoid duplicate requests across server/client.

```ts
import { provideClientHydration, withIncrementalHydration } from '@angular/platform-browser';

bootstrapApplication(App, {
  providers: [provideClientHydration(withIncrementalHydration())],
});
```

### Incremental hydration (default in v22)

Incremental hydration hydrates parts of the page **on demand**, driven by `@defer` triggers (`on viewport`, `on interaction`, …). Server-rendered HTML is shipped, but the JS for a block isn't loaded/hydrated until its trigger fires — lower TBT, smaller initial JS.

```html
@defer (hydrate on viewport) {
  <comments-section />
}
```

Was a developer preview in v19; **enabled by default in v22**. Related roadmap items: streamed SSR and event replay (`withEventReplay()`, default since v18) so user clicks before hydration aren't lost.

---

# Part 5: Testing & Tooling

---

## 22. Testing

### TestBed + component test

```ts
import { TestBed } from '@angular/core/testing';
import { Counter } from './counter';

describe('Counter', () => {
  beforeEach(() => TestBed.configureTestingModule({ imports: [Counter] }));

  it('increments', () => {
    const fixture = TestBed.createComponent(Counter);
    fixture.detectChanges();
    const btn = fixture.nativeElement.querySelector('button:last-child');
    btn.click();
    fixture.detectChanges();
    expect(fixture.componentInstance.count()).toBe(1);
  });
});
```

### HTTP testing

```ts
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';

TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
const ctrl = TestBed.inject(HttpTestingController);
ctrl.expectOne('/api/users/1').flush({ id: 1 });
ctrl.verify();
```

`httpResource` is tested with the same `HttpTestingController` since it wraps `HttpClient`.

### Vitest (v21+)

Angular's CLI moved its default unit-test runner toward **Vitest** (replacing the deprecated Karma/Jasmine setup). Vitest is faster, ESM-native, and shares config with the esbuild/Vite build pipeline. Component Test Harnesses (`@angular/cdk/testing`) remain the recommended way to interact with Material/CDK components in tests, independent of runner.

---

## 23. Performance & Optimization

- **`track` in `@for`** — the highest-leverage list optimization; avoids DOM churn on reorder.
- **`OnPush` / signals / zoneless** — minimize change-detection scope (default `OnPush` in v22).
- **`@defer`** — defer + code-split heavy, below-the-fold components.
- **Lazy routes** — `loadComponent` / `loadChildren` split per-route bundles; `withPreloading` warms them.
- **SSR + hydration** — faster first paint; incremental hydration cuts initial JS/TBT.
- **`NgOptimizedImage`** (`ngSrc`) — lazy loading, `srcset` generation, priority hints, layout-shift prevention.
- **`computed` over methods in templates** — template method calls run every CD cycle; `computed` memoizes.
- **`injectAsync`** (v22) — service-level code splitting; defer large dependencies until needed.
- **Bundle budgets** in `angular.json` to fail the build when bundles regress; esbuild/Vite builder is the default and much faster than the old Webpack builder (Webpack builders are deprecated in v22).

---

# Part 6: What's New

---

## 24. Version Timeline: v17 → v22

| Version | Date | Headline features |
|---|---|---|
| **v17** | Nov 2023 | Built-in control flow (`@if`/`@for`/`@switch`), deferrable views (`@defer`), esbuild/Vite dev server default, new `angular.dev` docs & branding, `@angular/ssr` |
| **v18** | May 2024 | Zoneless change detection (experimental), Material 3 stable, event replay, route redirects as functions, `@angular/build` |
| **v19** | Nov 2024 | Standalone by default (`standalone: true` no longer needed), signal `input`/`output`/`model`/queries stable, `linkedSignal` & `resource` (experimental), incremental hydration (preview), HMR for templates/styles |
| **v20** | May 2025 | Core signal primitives stable (`effect`, `linkedSignal`, `toSignal`), `resource`/`httpResource` polished (still experimental), zoneless stabilizing (stable in 20.2), DevTools profiling |
| **v21** | Nov 2025 | **Zoneless default** for new projects, **Signal Forms (experimental)**, **Vitest** as default test runner, Angular Aria directives, enhanced MCP server / AI tooling |
| **v22** | Jun 2026 | **Signal Forms, Resource API & Angular Aria stable**; **OnPush default**; incremental hydration default; `@Service`, `injectAsync`, `debounced`; `@boundary` (preview); TypeScript 6; Webpack deprecated |

---

## 25. Angular v22 Deep Dive

v22 (June 3, 2026) is a **consolidation release** — the point where three years of signal/reactivity/accessibility work becomes the default way Angular apps are built.

### Graduated to stable
- **Signal Forms** (`@angular/forms/signals`) — see §19.
- **Resource API** — `resource`, `rxResource`, `httpResource` (§13, §17).
- **Angular Aria** — accessibility primitives/directives for building accessible components.

### Changed defaults
- **`OnPush` by default** — components without an explicit strategy use `OnPush`; `ng update` inserts `ChangeDetectionStrategy.Eager` on existing components to preserve always-check behavior.
- **Incremental hydration** enabled by default.
- **Router** inherits route params from all parent routes by default.

### New building blocks

**`@Service` decorator** — concise tree-shakeable singleton; `@Service()` ≈ `@Injectable({ providedIn: 'root' })`.

```ts
import { Service } from '@angular/core';

@Service() // app-wide singleton, no repeated config
export class FlightClient {}

@Service({ autoProvided: false }) // opt out of auto-provisioning
export class TabRegistry {}
```

**`injectAsync`** — asynchronous DI / service-level code splitting; defer heavy dependencies until needed, with optional prefetch.

```ts
import { injectAsync, onIdle } from '@angular/core';

private upgrade = injectAsync(
  () => import('./upgrade-service').then(m => m.UpgradeService),
  { prefetch: onIdle },
);
async run() { (await this.upgrade()).upgrade(); }
```

**`debounced`** — a debounced view of a signal.

```ts
import { debounced } from '@angular/core';
const query = signal('');
const debouncedQuery = debounced(query, 300); // read debouncedQuery.value()
```

**`@boundary` (developer preview, ~Q3 2026)** — error boundary block; an isolated component failure renders fallback content instead of taking down the page.

### Template syntax enhancements
- Object/array **spread** in bindings: `[class]="{ ...base, active: isActive() }"`.
- **Arrow functions** in templates: `(click)="select(x => x.id === item.id)"`.
- **`instanceof`** narrowing inside `@if`.
- **Exhaustive `@switch`** with `never(state)` in `@default` for compile-time exhaustiveness.

### Platform / tooling / security
- **TypeScript 6** support; team focusing on **TSGo** in the application builder.
- **Webpack support deprecated** (`@angular-devkit/build-angular` Webpack path, `@ngtools/webpack`).
- Security hardening: `platform-server` guards against SSRF and path hijacking, rejects protocol-relative/backslash URLs; HTTP transfer cache skips `withCredentials`/cookie requests.
- **WebMCP** — expose your app/forms as tools callable by in-browser AI agents.

---

## Sources

Key references used for the v20–v22 material:

- [Announcing Angular v22 — Angular Blog](https://blog.angular.dev/announcing-angular-v22-c52bb83a4664)
- [Angular v22 — most important new features (ANGULARarchitects)](https://www.angulararchitects.io/en/blog/angular-22-the-most-important-new-features-at-a-glance/)
- [What's new in Angular 21 (ANGULARarchitects)](https://www.angulararchitects.io/blog/whats-new-in-angular-21-signal-forms-zone-less-vitest-angular-aria-cli-with-mcp-server/)
- [Announcing Angular v20 — Angular Blog](https://blog.angular.dev/announcing-angular-v20-b5c9c06cf301)
- [Forms with signals — angular.dev](https://angular.dev/essentials/signal-forms) · [Signal Forms validation](https://angular.dev/guide/forms/signals/validation)
- [Async reactivity with resources — angular.dev](https://angular.dev/guide/signals/resource) · [httpResource](https://angular.dev/guide/http/http-resource)
- [Angular Roadmap](https://angular.dev/roadmap)
