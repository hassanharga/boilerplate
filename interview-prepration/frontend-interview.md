# Frontend Interview Reference

A senior-focused reference covering HTML, CSS, browser internals, Web APIs, performance, accessibility, and build tools. Concept + code snippet format.

---

## Table of Contents

### Part 1: HTML
1. [Semantic HTML](#1-semantic-html)
2. [Forms](#2-forms)
3. [Meta & Head](#3-meta--head)
28. [SEO Beyond Meta Tags](#28-seo-beyond-meta-tags)

### Part 2: CSS
4. [Cascade, Specificity & Inheritance](#4-cascade-specificity--inheritance)
5. [Box Model & Layout](#5-box-model--layout)
6. [Flexbox](#6-flexbox)
7. [CSS Grid](#7-css-grid)
8. [Positioning & Stacking Context](#8-positioning--stacking-context)
9. [Responsive Design](#9-responsive-design)
10. [Animations & Transitions](#10-animations--transitions)
11. [CSS Variables & Modern Features](#11-css-variables--modern-features)
26. [CSS Architecture](#26-css-architecture)

### Part 3: Browser & Web APIs
12. [Browser Rendering Pipeline](#12-browser-rendering-pipeline)
13. [DOM & Events](#13-dom--events)
14. [Storage](#14-storage)
15. [Web APIs](#15-web-apis)
16. [HTTP & Networking](#16-http--networking)
17. [Security](#17-security)
23. [Service Workers & PWA](#23-service-workers--pwa)
29. [Global Error Handling](#29-global-error-handling)

### Part 4: Performance
18. [Core Web Vitals](#18-core-web-vitals)
19. [Loading Performance](#19-loading-performance)
20. [Runtime Performance](#20-runtime-performance)
24. [Image Optimization](#24-image-optimization)
25. [Memory Leaks](#25-memory-leaks)
30. [Performance Monitoring](#30-performance-monitoring)

### Part 5: Accessibility
21. [Accessibility Essentials](#21-accessibility-essentials)

### Part 6: Build Tools
22. [Bundlers & Build Pipeline](#22-bundlers--build-pipeline)

### Part 7: Testing
27. [Frontend Testing](#27-frontend-testing)

---

# Part 1: HTML

---

## 1. Semantic HTML

Semantic elements carry meaning about the content they wrap — they tell the browser, search engines, and assistive technologies what a piece of content *is*, not just how it looks.

```html
<!-- Non-semantic — no meaning, just structure -->
<div class="header">
  <div class="nav">...</div>
</div>
<div class="main">
  <div class="article">...</div>
  <div class="aside">...</div>
</div>
<div class="footer">...</div>

<!-- Semantic — communicates structure and meaning -->
<header>
  <nav aria-label="Main navigation">...</nav>
</header>
<main>
  <article>
    <h1>Article Title</h1>
    <section>...</section>
  </article>
  <aside aria-label="Related links">...</aside>
</main>
<footer>...</footer>
```

### Landmark Elements

| Element | Role | Use |
|---|---|---|
| `<header>` | `banner` | Site or section header |
| `<nav>` | `navigation` | Navigation links |
| `<main>` | `main` | Primary content (one per page) |
| `<article>` | `article` | Self-contained content |
| `<section>` | `region` | Thematic grouping (needs a heading) |
| `<aside>` | `complementary` | Tangentially related content |
| `<footer>` | `contentinfo` | Site or section footer |

### Heading Hierarchy

One `<h1>` per page. Never skip levels (e.g., `h1` → `h3`). Headings define document outline — screen readers navigate by them.

```html
<h1>Page Title</h1>
  <h2>Section</h2>
    <h3>Subsection</h3>
    <h3>Subsection</h3>
  <h2>Another Section</h2>
```

---

## 2. Forms

### Input Types & Validation

```html
<form action="/submit" method="POST" novalidate>
  <!-- novalidate disables browser UI but keeps constraint API -->

  <fieldset>
    <legend>Personal Information</legend>

    <label for="name">Full name <span aria-hidden="true">*</span></label>
    <input
      id="name"
      name="name"
      type="text"
      required
      minlength="2"
      maxlength="100"
      autocomplete="name"
    />

    <label for="email">Email</label>
    <input id="email" name="email" type="email" required autocomplete="email" />

    <label for="age">Age</label>
    <input id="age" name="age" type="number" min="0" max="150" />

    <label for="dob">Date of birth</label>
    <input id="dob" name="dob" type="date" />

    <label for="website">Website</label>
    <input id="website" name="website" type="url" />

    <label for="phone">Phone</label>
    <input id="phone" name="phone" type="tel" autocomplete="tel" />

    <!-- password field -->
    <label for="password">Password</label>
    <input
      id="password"
      name="password"
      type="password"
      required
      minlength="8"
      autocomplete="new-password"
    />
  </fieldset>

  <!-- Group related radio/checkboxes in fieldset -->
  <fieldset>
    <legend>Preferred contact</legend>
    <label><input type="radio" name="contact" value="email" /> Email</label>
    <label><input type="radio" name="contact" value="phone" /> Phone</label>
  </fieldset>

  <label>
    <input type="checkbox" name="agree" required />
    I agree to the terms
  </label>

  <button type="submit">Submit</button>
</form>
```

### Constraint Validation API

```js
const input = document.getElementById('email');

input.checkValidity();       // boolean — does it pass all constraints?
input.validity.valueMissing; // true if required and empty
input.validity.typeMismatch; // true if value doesn't match type
input.validity.tooShort;     // true if below minlength
input.setCustomValidity('This email is already taken'); // custom error
input.setCustomValidity(''); // clear custom error

// Show errors on submit
form.addEventListener('submit', (e) => {
  if (!form.checkValidity()) {
    e.preventDefault();
    [...form.elements].forEach((el) => {
      if (!el.checkValidity()) {
        el.closest('.field')?.querySelector('.error')
          ?.textContent = el.validationMessage;
      }
    });
  }
});
```

---

## 3. Meta & Head

```html
<head>
  <meta charset="UTF-8" />

  <!-- Viewport — critical for responsive design -->
  <meta name="viewport" content="width=device-width, initial-scale=1" />

  <title>Page Title — Site Name</title>
  <meta name="description" content="150-160 char page summary for SEO" />

  <!-- Open Graph — controls link previews on social media -->
  <meta property="og:title" content="Page Title" />
  <meta property="og:description" content="Description" />
  <meta property="og:image" content="https://example.com/og-image.jpg" />
  <meta property="og:url" content="https://example.com/page" />
  <meta property="og:type" content="website" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Page Title" />

  <!-- Canonical URL — prevents duplicate content penalty -->
  <link rel="canonical" href="https://example.com/page" />

  <!-- Favicon -->
  <link rel="icon" href="/favicon.ico" sizes="any" />
  <link rel="icon" href="/icon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />

  <!-- CSS — render-blocking by default, load early -->
  <link rel="stylesheet" href="/styles.css" />

  <!-- Resource hints -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preload" href="/hero.jpg" as="image" />
  <link rel="prefetch" href="/next-page.js" />

  <!-- Scripts -->
  <!-- defer: download in parallel, execute after HTML parsed (in order) -->
  <script src="/app.js" defer></script>
  <!-- async: download in parallel, execute immediately when ready (order not guaranteed) -->
  <script src="/analytics.js" async></script>
  <!-- Module scripts are deferred by default -->
  <script type="module" src="/main.js"></script>
</head>
```

### `defer` vs `async` vs module

| | Download | Execution | Order |
|---|---|---|---|
| none | Blocks parsing | Immediately | In order |
| `defer` | Parallel | After HTML parsed | In order |
| `async` | Parallel | As soon as ready | Not guaranteed |
| `type="module"` | Parallel | After HTML parsed (like defer) | In order |

Use `defer` for scripts that need the DOM or depend on each other. Use `async` for independent scripts (analytics, ads).

---

# Part 2: CSS

---

## 4. Cascade, Specificity & Inheritance

### Cascade

When multiple rules target the same element and property, the cascade determines which wins — in priority order:

1. **Origin** — browser defaults < author styles < `!important` author styles
2. **Specificity** — more specific selector wins
3. **Source order** — later rule wins on a tie

### Specificity

Specificity is a 3-part score: `(ID, CLASS, TYPE)`.

| Selector | Score |
|---|---|
| `*` | 0,0,0 |
| `p`, `div` (type) | 0,0,1 |
| `.class`, `[attr]`, `:hover` | 0,1,0 |
| `#id` | 1,0,0 |
| Inline style | 1,0,0,0 (above IDs) |
| `!important` | Overrides everything |

```css
p { color: black; }             /* 0,0,1 */
.text { color: blue; }          /* 0,1,0 — wins */
#title { color: red; }          /* 1,0,0 — wins */
p.text#title { color: green; }  /* 1,1,1 — wins */
```

**Avoid `!important`** — it breaks the cascade and makes debugging painful. Use more specific selectors or CSS Layers instead.

### CSS Layers (`@layer`)

Layers let you explicitly control specificity order — styles in a higher-priority layer win regardless of selector specificity.

```css
@layer reset, base, components, utilities;

@layer reset {
  * { margin: 0; padding: 0; }
}

@layer components {
  .btn { background: blue; } /* wins over reset, loses to utilities */
}

@layer utilities {
  .mt-4 { margin-top: 1rem; } /* always wins within layers */
}
```

### Inheritance

Some properties (`color`, `font-*`, `line-height`, `text-*`) inherit from parent elements by default. Others (`margin`, `padding`, `border`, `background`) do not.

```css
/* Force inheritance */
.child { color: inherit; }

/* Reset to browser default */
.child { color: initial; }

/* Inherit or initial depending on whether property normally inherits */
.child { color: unset; }
```

---

## 5. Box Model & Layout

### Box Model

Every element is a rectangular box: **content → padding → border → margin**.

```css
/* Default: width = content only, padding/border added on top */
.default { width: 200px; padding: 20px; border: 2px solid; }
/* Total width = 200 + 40 + 4 = 244px */

/* border-box: width includes padding and border — far more intuitive */
* { box-sizing: border-box; }
.box { width: 200px; padding: 20px; border: 2px solid; }
/* Total width = 200px exactly */
```

### Margin Collapse

Adjacent vertical margins collapse into one (the larger value). Only happens between block-level elements in normal flow — not in flex/grid containers.

```css
/* These margins collapse — gap is 30px, not 50px */
.top    { margin-bottom: 30px; }
.bottom { margin-top: 20px; }

/* Fix: use flex/grid on parent, or add padding/border/overflow to parent */
```

### `display` Values

| Value | Behaviour |
|---|---|
| `block` | Full width, starts on new line, respects width/height/margin |
| `inline` | Fits content, no new line, ignores width/height/vertical margin |
| `inline-block` | Flows inline but respects width/height/margin like block |
| `flex` | Flex container |
| `grid` | Grid container |
| `none` | Removed from layout (and accessibility tree) |
| `contents` | Element itself disappears, children remain |

```css
/* inline — ignores width/height */
span { display: inline; width: 100px; } /* width has no effect */

/* inline-block — respects width/height, stays in line flow */
span { display: inline-block; width: 100px; height: 40px; } /* works */

/* Common use: navigation items, icon+text combos */
nav a { display: inline-block; padding: 8px 16px; }
```

### Block Formatting Context (BFC)

A BFC is an isolated formatting region. Creating one:
- Contains floated children (prevents float collapse)
- Prevents margin collapse with children
- Doesn't overlap floated siblings

```css
/* Ways to create a BFC */
.bfc { overflow: hidden; }         /* classic float clearfix */
.bfc { display: flow-root; }       /* modern, no side effects */
.bfc { display: flex; }            /* flex containers are BFCs */
.bfc { position: absolute; }
```

---

## 6. Flexbox

Flexbox is one-dimensional — it lays items along a single axis (row or column).

```css
.container {
  display: flex;
  flex-direction: row;          /* row | row-reverse | column | column-reverse */
  flex-wrap: wrap;              /* nowrap | wrap | wrap-reverse */
  justify-content: space-between; /* align on MAIN axis */
  align-items: center;          /* align on CROSS axis */
  align-content: flex-start;    /* align WRAPPED lines on cross axis */
  gap: 16px;                    /* gap: row-gap column-gap */
}

.item {
  flex-grow: 1;    /* how much to grow relative to siblings (default: 0) */
  flex-shrink: 1;  /* how much to shrink (default: 1) */
  flex-basis: 0%;  /* initial size before growing/shrinking (default: auto) */

  /* shorthand */
  flex: 1;         /* grow:1 shrink:1 basis:0% — "take equal share" */
  flex: 0 0 200px; /* fixed 200px, no grow or shrink */
  flex: auto;      /* 1 1 auto */

  align-self: flex-end;  /* override container's align-items for this item */
  order: 2;              /* visual order (not DOM order — impacts a11y) */
}
```

### Common Patterns

```css
/* Perfect centering */
.center {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Sticky footer — main grows to push footer down */
body {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
main { flex: 1; }

/* Equal-width columns that wrap */
.grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
.grid > * {
  flex: 1 1 200px; /* grow and shrink, min 200px before wrapping */
}
```

---

## 7. CSS Grid

Grid is two-dimensional — rows and columns simultaneously.

```css
.container {
  display: grid;

  /* Explicit tracks */
  grid-template-columns: 200px 1fr 1fr; /* fixed | fraction */
  grid-template-rows: auto 1fr auto;

  /* Named areas */
  grid-template-areas:
    "header header header"
    "sidebar main main"
    "footer footer footer";

  gap: 16px; /* row-gap column-gap */
  align-items: start;    /* align items in their cell vertically */
  justify-items: stretch; /* align items in their cell horizontally */
}

/* Place items by area name */
.header  { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main    { grid-area: main; }
.footer  { grid-area: footer; }

/* Place items by line numbers */
.item {
  grid-column: 1 / 3;   /* span columns 1 to 3 */
  grid-row: 2 / 4;
  grid-column: 1 / -1;  /* span full width */
  grid-column: span 2;  /* span 2 columns from current position */
}
```

### `auto-fill` vs `auto-fit`

```css
/* auto-fill — creates as many tracks as fit, including empty ones */
grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));

/* auto-fit — collapses empty tracks, items stretch to fill */
grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));

/* Result when 3 items in a 900px container (200px min):
   auto-fill: | item | item | item | empty |  — 4 tracks, last empty
   auto-fit:  | item     | item     | item  |  — 3 tracks, items stretch */
```

### `fr` Unit

`1fr` = one fraction of the **available space** (after fixed/auto tracks are placed).

```css
/* 3 equal columns */
grid-template-columns: repeat(3, 1fr);

/* Sidebar + main: sidebar is 250px, main takes the rest */
grid-template-columns: 250px 1fr;

/* 1:2:1 ratio */
grid-template-columns: 1fr 2fr 1fr;
```

### Subgrid

Child elements can participate in the parent grid's tracks — solves alignment of nested components.

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: auto auto 1fr auto; /* title, image, body, footer */
}

.card {
  display: grid;
  grid-row: span 4;
  grid-template-rows: subgrid; /* inherit parent's row definitions */
}
/* All cards now have aligned titles, images, body, and footers */
```

---

## 8. Positioning & Stacking Context

### Position Values

| Value | Behaviour |
|---|---|
| `static` | Default. Not positioned — `top`/`left`/`z-index` have no effect |
| `relative` | Offset from its normal position. Still occupies original space |
| `absolute` | Removed from flow. Positioned relative to nearest non-static ancestor |
| `fixed` | Removed from flow. Positioned relative to the viewport. Stays on scroll |
| `sticky` | Acts like `relative` until it hits a scroll threshold, then acts like `fixed` |

```css
/* relative — offset but still in flow */
.badge {
  position: relative;
  top: -2px; /* nudge up 2px from where it would normally sit */
}

/* absolute — positioned relative to nearest positioned ancestor */
.card { position: relative; } /* establishes containing block */
.card .badge {
  position: absolute;
  top: 8px;
  right: 8px; /* 8px from card's top-right corner */
}

/* fixed — always visible, scrolls with viewport */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 100;
}

/* sticky — sticks within its scroll container */
.table-header th {
  position: sticky;
  top: 0; /* sticks when it reaches 0px from top of scroll container */
  background: white; /* needed — sticky doesn't paint background by default */
}
```

### `z-index` & Stacking Context

`z-index` only works on positioned elements (`position` ≠ `static`). Elements are painted in stacking order: lower `z-index` first (behind), higher last (in front).

A **stacking context** is an isolated z-index universe. Elements inside a stacking context are stacked relative to each other, but the entire context is stacked as a unit in the parent context — a child with `z-index: 9999` cannot escape its parent's stacking order.

```css
/* These create a new stacking context: */
.context {
  position: relative; z-index: any-integer; /* most common */
  opacity: < 1;
  transform: any-value;
  filter: any-value;
  isolation: isolate; /* explicit, no side effects */
  will-change: transform;
}
```

**Classic bug — modal hidden behind lower element:**

```css
/* Problem: .modal has z-index: 1000 but .parent creates a stacking context with z-index: 1 */
.parent  { position: relative; z-index: 1; }  /* stacking context */
.sibling { position: relative; z-index: 2; }  /* higher context */
.modal   { position: fixed; z-index: 1000; }  /* INSIDE parent — limited to z:1 world */

/* Fix: move .modal to be a sibling of .parent, not a child */
/* Or use isolation: isolate on a container that doesn't need z-index */
```

---

## 9. Responsive Design

### `px` vs `em` vs `rem`

| Unit | Relative to | Use case |
|---|---|---|
| `px` | Absolute (device pixels) | Borders, shadows, fine details that shouldn't scale |
| `em` | Parent element's font-size | Component-level scaling — padding/margin relative to text |
| `rem` | Root element's font-size (`<html>`) | Global spacing, font sizes — consistent across components |
| `%` | Parent element's dimension | Fluid widths, positioning |
| `vw`/`vh` | Viewport width/height | Full-screen sections, hero heights |
| `ch` | Width of `0` character | Ideal line length for text (50–75ch) |

```css
html { font-size: 16px; } /* 1rem = 16px */

/* rem — consistent, predictable */
h1 { font-size: 2rem; }     /* always 32px regardless of parent */
p  { font-size: 1rem; }
.container { padding: 1.5rem; }

/* em — compounds with parent — good for component spacing */
.btn {
  font-size: 1rem;
  padding: 0.5em 1em; /* relative to button's own font-size — scales with text */
}
.btn-lg { font-size: 1.25rem; /* padding auto-scales */ }

/* px — when you don't want it to scale */
.border { border: 1px solid; }
.shadow { box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
```

**Best practice:** use `rem` for font sizes and global spacing, `em` for component-internal spacing (so the component scales with its font size), `px` for borders and fine details.

---

### Media Queries

```css
/* Mobile-first — start with base (mobile) styles, add complexity for larger screens */
.container { padding: 1rem; }

@media (min-width: 768px) {
  .container { padding: 2rem; }
}

@media (min-width: 1024px) {
  .container { max-width: 1200px; margin: 0 auto; }
}

/* Feature queries */
@media (hover: hover) {
  .btn:hover { background: darkblue; } /* only on devices with hover */
}

@media (prefers-color-scheme: dark) {
  :root { --bg: #121212; --text: #e0e0e0; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; }
}
```

### `clamp()` — Fluid Typography & Spacing

`clamp(min, preferred, max)` — a value that scales with the viewport between a min and max.

```css
/* Font size: min 1rem, preferred 4vw, max 3rem */
h1 { font-size: clamp(1.5rem, 4vw + 1rem, 3rem); }

/* Fluid padding */
.section { padding: clamp(2rem, 5vw, 5rem); }

/* Fluid container */
.container { width: clamp(320px, 90%, 1200px); }
```

### Container Queries

Respond to the size of the parent container, not the viewport — essential for reusable components.

```css
.card-wrapper {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 400px) {
  .card { flex-direction: row; }
  .card-image { width: 200px; }
}
```

---

## 10. Animations & Transitions

### Transitions

Smooth change between two states triggered by a state change (hover, focus, class toggle).

```css
.btn {
  background: blue;
  transform: scale(1);
  /* Only transition specific properties for performance */
  transition: background 200ms ease, transform 200ms ease;
}

.btn:hover {
  background: darkblue;
  transform: scale(1.05);
}

/* transition shorthand */
transition: property duration timing-function delay;
transition: all 300ms ease-in-out;  /* avoid 'all' — triggers on every property */
```

### `@keyframes` Animations

```css
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal {
  animation: slideIn 300ms ease forwards;
  /* name | duration | timing | fill-mode */
}

/* Multiple keyframes */
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50%       { transform: scale(1.05); }
}

.loading { animation: pulse 1.5s ease-in-out infinite; }
```

### Performance — Animate the Right Properties

Only `transform` and `opacity` can be animated on the **compositor thread** (GPU) without triggering layout or paint. Animating any other property forces the CPU to do more work.

```css
/* GOOD — compositor only, no reflow/repaint */
.slide { transition: transform 300ms ease; }
.fade  { transition: opacity 200ms ease; }

/* BAD — triggers layout (reflow) on every frame */
.bad { transition: width 300ms; }
.bad { transition: top 300ms; }
.bad { transition: margin 300ms; }
```

### `will-change`

Hints to the browser that an element will be animated, promoting it to its own compositor layer ahead of time.

```css
/* Only add when you measure a real performance problem */
.animated-card { will-change: transform; }

/* Remove after animation completes to free memory */
element.addEventListener('transitionend', () => {
  element.style.willChange = 'auto';
});
```

### `prefers-reduced-motion`

Always respect the user's OS setting for reduced motion.

```css
@media (prefers-reduced-motion: reduce) {
  .animated { animation: none; transition: none; }
}

/* Or use the no-preference query to only add animations when OK */
@media (prefers-reduced-motion: no-preference) {
  .hero { animation: fadeIn 1s ease; }
}
```

---

## 11. CSS Variables & Modern Features

### Custom Properties (CSS Variables)

```css
:root {
  /* Declare globally */
  --color-primary: #0070f3;
  --color-text: #111;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 2rem;
  --radius: 8px;
}

.btn {
  background: var(--color-primary);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius);
  color: var(--color-text, black); /* fallback value */
}

/* Override in scope */
.dark-theme {
  --color-primary: #60a5fa;
  --color-text: #f0f0f0;
}

/* Dynamic theming via JS */
document.documentElement.style.setProperty('--color-primary', '#ff0000');
```

### `:is()`, `:where()`, `:has()`

```css
/* :is() — matches any selector in the list, takes highest specificity of list */
:is(h1, h2, h3, h4) { margin-top: 1.5rem; }
/* Equivalent to: h1, h2, h3, h4 { ... } but more maintainable */

/* :where() — same as :is() but specificity is always 0 — easy to override */
:where(h1, h2, h3) { margin: 0; } /* can be overridden by any selector */

/* :has() — "parent selector" — select based on children */
.card:has(img) { padding: 0; }              /* card with an image */
label:has(+ input:required)::after {        /* label before required input */
  content: ' *';
  color: red;
}
form:has(input:invalid) button[type=submit] {
  opacity: 0.5;
  pointer-events: none;
}
```

### Logical Properties

Logical properties adapt to writing direction (LTR/RTL, horizontal/vertical) automatically.

```css
/* Physical → Logical */
margin-left  → margin-inline-start
margin-right → margin-inline-end
margin-top   → margin-block-start
padding-left → padding-inline-start
width        → inline-size
height       → block-size
top          → inset-block-start
left         → inset-inline-start

/* Use logical properties for i18n-ready layouts */
.text { margin-inline-start: 1rem; } /* left in LTR, right in RTL */
```

---

# Part 3: Browser & Web APIs

---

## 12. Browser Rendering Pipeline

Understanding the pipeline helps you know what triggers expensive work.

```
Parse HTML → Build DOM
Parse CSS  → Build CSSOM
             ↓
         DOM + CSSOM → Render Tree (only visible nodes)
                          ↓
                       Layout  (calculate geometry — positions and sizes)
                          ↓
                       Paint   (fill in pixels — colors, borders, text)
                          ↓
                       Composite (layer ordering, GPU upload)
                          ↓
                       Display
```

### Critical Rendering Path

The CRP is the sequence of steps to render the initial page. Optimizing it = faster First Contentful Paint.

**Render-blocking resources:**
- CSS in `<head>` is render-blocking — browser won't render until CSSOM is built
- `<script>` without `defer`/`async` is both parser-blocking and render-blocking

```html
<!-- Inline critical CSS in <head> — no network round trip -->
<style>
  /* above-the-fold styles only */
  body { margin: 0; font-family: sans-serif; }
  .hero { background: #000; color: #fff; min-height: 100vh; }
</style>

<!-- Load full CSS asynchronously -->
<link rel="preload" href="/styles.css" as="style" onload="this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="/styles.css"></noscript>

<!-- Defer non-critical scripts -->
<script src="/app.js" defer></script>
```

### Reflow vs Repaint vs Composite

| Operation | Cost | Trigger |
|---|---|---|
| **Reflow (Layout)** | Expensive | Changing geometry: `width`, `height`, `margin`, `padding`, `font-size`, `top`, `left` |
| **Repaint** | Moderate | Changing visuals without geometry: `color`, `background`, `visibility`, `border-color` |
| **Composite** | Cheap (GPU) | `transform`, `opacity` only |

**Avoiding forced synchronous layout (layout thrashing):**

```js
// BAD — alternating read/write forces multiple reflows
elements.forEach((el) => {
  const width = el.offsetWidth;     // READ — forces layout
  el.style.width = width * 2 + 'px'; // WRITE — invalidates layout
});

// GOOD — batch reads, then batch writes
const widths = elements.map((el) => el.offsetWidth); // all reads
elements.forEach((el, i) => {
  el.style.width = widths[i] * 2 + 'px';             // all writes
});

// Properties that trigger reflow when read:
// offsetWidth/Height, clientWidth/Height, scrollWidth/Height,
// getBoundingClientRect(), getComputedStyle()
```

### Cumulative Layout Shift (CLS)

CLS measures unexpected layout shifts — elements moving around after initial render. Caused by images without dimensions, late-loading fonts, dynamically injected content.

```html
<!-- Always set width and height on images — reserves space -->
<img src="hero.jpg" width="800" height="400" alt="Hero" />

<!-- Or use aspect-ratio in CSS -->
<style>
  img { aspect-ratio: 16/9; width: 100%; }
</style>

<!-- Font swap causes CLS — use font-display: optional or preload fonts -->
<link rel="preload" href="/font.woff2" as="font" type="font/woff2" crossorigin />
<style>
  @font-face {
    font-family: 'MyFont';
    src: url('/font.woff2') format('woff2');
    font-display: optional; /* don't swap if not loaded in time */
  }
</style>

<!-- Reserve space for dynamic content (ads, embeds) -->
<div style="min-height: 250px;">
  <!-- ad loads here -->
</div>
```

---

## 13. DOM & Events

### Event Propagation

Events propagate in 3 phases:
1. **Capture** — from window down to target
2. **Target** — at the element itself
3. **Bubble** — from target back up to window

```js
// Third argument: true = capture phase, false/omitted = bubble phase
element.addEventListener('click', handler, true);  // capture
element.addEventListener('click', handler, false); // bubble (default)

// Stop propagation
event.stopPropagation();      // stop bubbling/capturing
event.stopImmediatePropagation(); // also stop other handlers on this element

// Prevent default browser action (form submit, link navigation, etc.)
event.preventDefault();
```

### Event Delegation

Attach one listener to a parent instead of many listeners on each child. Efficient for dynamic lists, and uses less memory.

```js
document.getElementById('list').addEventListener('click', (e) => {
  const item = e.target.closest('[data-id]');
  if (!item) return; // click was outside a list item

  handleItemClick(item.dataset.id);
});

// Works for dynamically added items — no re-registration needed
```

### `MutationObserver`

Watch for changes to the DOM tree.

```js
const observer = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    if (mutation.type === 'childList') {
      mutation.addedNodes.forEach((node) => console.log('Added:', node));
    }
    if (mutation.type === 'attributes') {
      console.log(`${mutation.attributeName} changed`);
    }
  }
});

observer.observe(document.getElementById('container'), {
  childList: true,   // direct children added/removed
  subtree: true,     // all descendants
  attributes: true,  // attribute changes
  characterData: true, // text changes
});

observer.disconnect(); // stop observing
```

### `ResizeObserver` & `IntersectionObserver`

```js
// ResizeObserver — watch element size changes (not window resize)
const resizeObserver = new ResizeObserver((entries) => {
  for (const entry of entries) {
    const { width, height } = entry.contentRect;
    console.log(`Element is now ${width}x${height}`);
  }
});
resizeObserver.observe(document.querySelector('.panel'));

// IntersectionObserver — detect when element enters/leaves viewport
const intersectionObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        intersectionObserver.unobserve(entry.target); // stop watching after first time
      }
    });
  },
  {
    root: null,        // viewport
    rootMargin: '0px', // extend/shrink viewport boundary
    threshold: 0.1,    // fire when 10% visible
  }
);

document.querySelectorAll('.lazy').forEach((el) => intersectionObserver.observe(el));
```

---

## 14. Storage

| Mechanism | Capacity | Persistence | Accessible from | Sent with requests |
|---|---|---|---|---|
| `localStorage` | ~5MB | Until cleared | Same origin | No |
| `sessionStorage` | ~5MB | Tab session | Same origin, same tab | No |
| Cookie | ~4KB | Configurable | Same origin (or wider) | Yes (automatic) |
| `IndexedDB` | 50MB+ | Until cleared | Same origin | No |
| `Cache API` | Large | Until cleared | Service Worker + page | No |

```js
// localStorage — synchronous, strings only
localStorage.setItem('theme', 'dark');
localStorage.getItem('theme');      // 'dark'
localStorage.removeItem('theme');
localStorage.clear();

// Always serialize objects
localStorage.setItem('user', JSON.stringify({ id: 1, name: 'Alice' }));
const user = JSON.parse(localStorage.getItem('user') ?? 'null');

// sessionStorage — same API, clears when tab closes

// Cookie — set from JS
document.cookie = 'name=Alice; path=/; max-age=3600; SameSite=Lax; Secure';

// Set from server (more secure — can use HttpOnly to block JS access)
// Set-Cookie: token=xyz; HttpOnly; Secure; SameSite=Strict; Max-Age=86400

// IndexedDB — async, stores structured data including Blobs
const request = indexedDB.open('MyDB', 1);
request.onupgradeneeded = (e) => {
  const db = e.target.result;
  db.createObjectStore('users', { keyPath: 'id' });
};
request.onsuccess = (e) => {
  const db = e.target.result;
  const tx = db.transaction('users', 'readwrite');
  tx.objectStore('users').add({ id: 1, name: 'Alice' });
};
```

---

## 15. Web APIs

### `fetch`

```js
// Basic GET
const data = await fetch('/api/users').then(r => {
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
});

// POST with JSON
const user = await fetch('/api/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Alice' }),
}).then(r => r.json());

// Abort long-running requests
const controller = new AbortController();
setTimeout(() => controller.abort(), 5000); // timeout after 5s

fetch('/api/slow', { signal: controller.signal })
  .catch((err) => {
    if (err.name === 'AbortError') console.log('Request cancelled');
  });
```

### Web Workers

Run JavaScript in a background thread — doesn't block the main thread.

```js
// main.js
const worker = new Worker('/worker.js');

worker.postMessage({ type: 'PROCESS', data: largeArray });

worker.onmessage = (e) => {
  console.log('Result:', e.data);
};

worker.onerror = (err) => console.error(err);

// worker.js
self.onmessage = (e) => {
  if (e.data.type === 'PROCESS') {
    const result = heavyComputation(e.data.data);
    self.postMessage(result);
  }
};
```

### WebSockets

Full-duplex communication channel — server can push data without client request.

```js
const ws = new WebSocket('wss://example.com/socket');

ws.onopen    = () => ws.send(JSON.stringify({ type: 'HELLO' }));
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.onclose   = (e) => console.log('Closed:', e.code, e.reason);
ws.onerror   = (e) => console.error(e);

// Reconnection with exponential backoff
function connect(attempt = 0) {
  const ws = new WebSocket(url);
  ws.onclose = () => {
    const delay = Math.min(1000 * 2 ** attempt, 30_000);
    setTimeout(() => connect(attempt + 1), delay);
  };
  return ws;
}
```

---

## 16. HTTP & Networking

### HTTP/1.1 vs HTTP/2 vs HTTP/3

| Feature | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---|---|---|---|
| Protocol | Text | Binary | Binary (over QUIC/UDP) |
| Multiplexing | No (1 request/connection) | Yes (many over 1 connection) | Yes |
| Head-of-line blocking | Yes | Yes (TCP level) | No (per-stream) |
| Header compression | No | HPACK | QPACK |
| Server push | No | Yes | Yes |
| Connection | 6 per origin | 1 per origin | 1 per origin |

**Implications for frontend:** HTTP/2 makes domain sharding and asset bundling less necessary. HTTP/3 performs better on unstable networks (mobile, high packet loss).

### Caching Headers

```
# Cache-Control — most important header

Cache-Control: no-store              # never cache
Cache-Control: no-cache              # cache but revalidate every time
Cache-Control: max-age=31536000      # cache for 1 year (immutable assets with hash)
Cache-Control: max-age=0, must-revalidate # revalidate on every use
Cache-Control: private, max-age=300  # user-specific, 5 minutes
Cache-Control: public, max-age=600, stale-while-revalidate=60

# ETag — fingerprint for conditional requests
ETag: "33a64df5"
# Browser sends: If-None-Match: "33a64df5"
# Server: 304 Not Modified (no body) if unchanged

# Last-Modified — date-based conditional
Last-Modified: Wed, 21 Oct 2023 07:28:00 GMT
# Browser sends: If-Modified-Since: Wed, 21 Oct 2023 07:28:00 GMT
```

**Caching strategy:**
- **HTML**: `no-cache` or short `max-age` — must fetch fresh to get new asset URLs
- **JS/CSS with content hash** (`main.a3f2b1.js`): `max-age=31536000, immutable` — safe to cache forever, hash changes when content changes
- **Images**: `max-age=86400` to `max-age=2592000` depending on update frequency

### CORS

CORS allows a server to permit requests from a different origin. The browser enforces it — the server opts in.

**Simple request** (GET/POST with basic headers): browser sends request, server responds with `Access-Control-Allow-Origin`.

**Preflight** (PUT, DELETE, custom headers): browser sends `OPTIONS` first:

```
# Preflight request
OPTIONS /api/users HTTP/1.1
Origin: https://app.example.com
Access-Control-Request-Method: DELETE
Access-Control-Request-Headers: Authorization

# Preflight response
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400       # cache preflight for 24h
Access-Control-Allow-Credentials: true  # allow cookies
```

---

## 17. Security

### Cross-Site Scripting (XSS)

XSS is injecting malicious scripts into a page viewed by other users. Always sanitize/escape HTML output.

```js
// VULNERABLE — directly inserting user input as HTML
element.innerHTML = userInput;

// NEVER use document.write() — deprecated, blocks parsing, and is an XSS vector
// document.write(userInput); ← don't do this

// SAFE — text only
element.textContent = userInput;

// SAFE — sanitize before HTML insertion
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```

**Content Security Policy (CSP)** — restricts which scripts, styles, and resources can load:

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-{random}';   # only inline scripts with this nonce
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https://cdn.example.com;
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';               # prevent clickjacking
```

### Cross-Site Request Forgery (CSRF)

CSRF tricks users into making authenticated requests to a site they're logged into. Defenses:

1. **`SameSite` cookies** — prevents cookies being sent in cross-site requests:
```
Set-Cookie: token=xyz; SameSite=Strict  # never sent cross-site
Set-Cookie: token=xyz; SameSite=Lax     # sent on top-level navigation (links), not embeds
Set-Cookie: token=xyz; SameSite=None; Secure # always sent — needs explicit opt-in
```

2. **CSRF tokens** — server-issued random token, validated on state-changing requests
3. **`Origin`/`Referer` header validation** on the server

### Subresource Integrity (SRI)

Ensure CDN resources haven't been tampered with:

```html
<script
  src="https://cdn.example.com/lib.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
  crossorigin="anonymous"
></script>
```

### Secure Cookies Checklist

```
Set-Cookie: session=xyz;
  HttpOnly;    # inaccessible to JS — prevents XSS token theft
  Secure;      # HTTPS only
  SameSite=Lax; # CSRF protection
  Path=/;
  Max-Age=86400;
  Domain=example.com
```

---

# Part 4: Performance

---

## 18. Core Web Vitals

Core Web Vitals are Google's user-experience metrics used in search ranking.

### LCP — Largest Contentful Paint

Measures how long until the largest visible content element (image or text block) is rendered. Target: **≤ 2.5s**.

**Common causes:** slow server response, render-blocking resources, slow image load, client-side rendering.

```html
<!-- Preload LCP image — tells browser to fetch early -->
<link rel="preload" href="/hero.jpg" as="image" fetchpriority="high" />

<!-- Set fetchpriority="high" on the image itself -->
<img src="/hero.jpg" alt="Hero" fetchpriority="high" />

<!-- Avoid lazy loading the LCP element -->
<!-- BAD: <img src="/hero.jpg" loading="lazy" /> -->
```

### CLS — Cumulative Layout Shift

Measures unexpected movement of page content after initial render. Target: **≤ 0.1**.

**Causes and fixes:**

```html
<!-- Images without dimensions shift on load -->
<!-- BAD: <img src="photo.jpg" /> -->
<!-- GOOD: reserve space with explicit dimensions or aspect-ratio -->
<img src="photo.jpg" width="800" height="450" alt="" />

<!-- Fonts cause text reflow when they load -->
<style>
  @font-face {
    font-family: 'Body';
    src: url('/fonts/body.woff2');
    font-display: swap;     /* FOUT — swap causes CLS */
    font-display: optional; /* no swap — better for CLS */
  }
</style>

<!-- Dynamic content — always reserve space -->
<div class="ad-slot" style="min-height: 250px;">
  <!-- ad loads async -->
</div>
```

### INP — Interaction to Next Paint *(replaced FID in March 2024)*

Measures responsiveness — the time from a user interaction to the next paint. Target: **≤ 200ms**. FID (First Input Delay) only measured the first interaction; INP measures all interactions throughout the page lifetime.

**Fix:** break long tasks into smaller chunks, move heavy work to Web Workers, use `scheduler.yield()` to give the browser a chance to render between tasks.

```js
// Break long task into smaller chunks
async function processLargeList(items) {
  for (let i = 0; i < items.length; i++) {
    processItem(items[i]);

    // Yield every 50 items — let browser paint between chunks
    if (i % 50 === 0) {
      await scheduler.yield?.() ?? new Promise(r => setTimeout(r, 0));
    }
  }
}
```

### Measuring Core Web Vitals

```js
import { onLCP, onCLS, onINP } from 'web-vitals';

onLCP(({ value, rating }) => {
  console.log(`LCP: ${value}ms — ${rating}`); // 'good', 'needs-improvement', 'poor'
  analytics.track('web-vital', { name: 'LCP', value, rating });
});

onCLS(({ value }) => analytics.track('web-vital', { name: 'CLS', value }));
onINP(({ value }) => analytics.track('web-vital', { name: 'INP', value }));
```

---

## 19. Loading Performance

### Resource Hints

```html
<!-- preconnect — establish connection early (DNS + TCP + TLS) -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />

<!-- dns-prefetch — DNS lookup only (lighter than preconnect) -->
<link rel="dns-prefetch" href="https://cdn.example.com" />

<!-- preload — fetch critical resource at high priority -->
<link rel="preload" href="/hero.jpg" as="image" fetchpriority="high" />
<link rel="preload" href="/fonts/body.woff2" as="font" type="font/woff2" crossorigin />
<link rel="preload" href="/critical.js" as="script" />

<!-- prefetch — fetch low-priority resource for future navigation -->
<link rel="prefetch" href="/next-page-bundle.js" />
```

### Lazy Loading

```html
<!-- Native lazy loading — defer off-screen images/iframes -->
<img src="below-fold.jpg" loading="lazy" alt="..." />
<iframe src="/embed" loading="lazy"></iframe>

<!-- Never lazy-load above-the-fold or LCP elements -->
```

### Code Splitting

Load only the JavaScript needed for the current page.

```js
// Dynamic import — split at route level
const route = location.pathname;
if (route === '/dashboard') {
  const { Dashboard } = await import('./Dashboard.js');
  render(Dashboard);
}

// React.lazy (see React doc for full example)
const Dashboard = React.lazy(() => import('./Dashboard'));

// Webpack magic comments — control chunk naming
const Chart = React.lazy(() =>
  import(/* webpackChunkName: "chart" */ './HeavyChart')
);
```

### Font Loading Strategy

```css
/* font-display values */
font-display: auto;     /* browser decides */
font-display: block;    /* invisible text until font loads (FOIT) */
font-display: swap;     /* fallback font shown, swaps when ready (FOUT) — risks CLS */
font-display: fallback; /* short block period (100ms), then swap if loaded, else fallback forever */
font-display: optional; /* very short block, no swap — best for CLS */
```

---

## 20. Runtime Performance

### `requestAnimationFrame`

Schedule visual updates to run before the browser's next paint — ensures animations run at the display's refresh rate (60fps = 16.6ms per frame).

```js
// BAD — setTimeout not synced to frame rate, may cause visual artifacts
setInterval(updateAnimation, 16);

// GOOD — runs before each paint
function animate(timestamp) {
  const elapsed = timestamp - startTime;
  element.style.transform = `translateX(${elapsed * 0.1}px)`;

  if (elapsed < duration) {
    requestAnimationFrame(animate);
  }
}

requestAnimationFrame(animate);

// Cancel if needed
const id = requestAnimationFrame(animate);
cancelAnimationFrame(id);
```

### `requestIdleCallback`

Schedule non-urgent work during the browser's idle time — won't block animations or interactions.

```js
requestIdleCallback((deadline) => {
  while (deadline.timeRemaining() > 0 && tasks.length > 0) {
    doTask(tasks.shift());
  }

  if (tasks.length > 0) {
    requestIdleCallback(processTasks); // continue in next idle period
  }
}, { timeout: 2000 }); // force run within 2s even if not idle
```

### Long Tasks & the Main Thread

Tasks over 50ms block the main thread — making the page feel unresponsive. Break them up:

```js
// Chunk array processing to avoid blocking
async function processInChunks(items, chunkSize = 100) {
  for (let i = 0; i < items.length; i += chunkSize) {
    const chunk = items.slice(i, i + chunkSize);
    processChunk(chunk);
    await new Promise(resolve => setTimeout(resolve, 0)); // yield main thread
  }
}

// Use Performance API to measure task duration
performance.mark('task-start');
doHeavyWork();
performance.mark('task-end');
performance.measure('task', 'task-start', 'task-end');
const [entry] = performance.getEntriesByName('task');
console.log(`Task took ${entry.duration}ms`);
```

---

# Part 5: Accessibility

---

## 21. Accessibility Essentials

### ARIA Roles, Properties, States

ARIA (Accessible Rich Internet Applications) supplements HTML to communicate semantics to assistive technologies. **First rule of ARIA: don't use ARIA if native HTML conveys the meaning.**

```html
<!-- Roles — what is this element? -->
<div role="button" tabindex="0">Click me</div>  <!-- prefer <button> instead -->
<div role="dialog" aria-modal="true" aria-labelledby="dialog-title">...</div>
<nav role="navigation" aria-label="Main">...</nav>

<!-- Properties — describe characteristics (don't change) -->
<input aria-required="true" />
<div aria-labelledby="section-heading" aria-describedby="help-text">...</div>
<button aria-haspopup="menu">Options</button>
<img aria-hidden="true" />  <!-- decorative image, hide from screen reader -->

<!-- States — describe current condition (may change) -->
<button aria-expanded="false" aria-controls="menu">Menu</button>
<li role="option" aria-selected="true">Item</li>
<input aria-invalid="true" aria-errormessage="error-id" />
<div role="progressbar" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100" />

<!-- Live regions — announce dynamic changes -->
<div aria-live="polite">   <!-- wait for user to be idle -->
  {statusMessage}
</div>
<div aria-live="assertive"> <!-- interrupt immediately — use sparingly -->
  {errorMessage}
</div>
```

### Keyboard Navigation

All interactive elements must be keyboard accessible. Tab order must be logical (follows DOM order unless `tabindex` is set).

```html
<!-- Focusable elements: a[href], button, input, select, textarea, [tabindex] -->

<!-- tabindex="0" — add element to tab order -->
<div role="button" tabindex="0" onclick="..." onkeydown="handleKey">Click</div>

<!-- tabindex="-1" — programmatically focusable, not in tab order -->
<div tabindex="-1" id="dialog">...</div>
<!-- dialog.focus() — useful for modals and focus management -->

<!-- Never use tabindex > 0 — breaks natural tab order -->
```

```js
// Keyboard event handling for custom interactive elements
function handleKey(e) {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    activate();
  }
}
```

### Focus Management

When opening a modal/dialog:
1. Move focus into the dialog
2. Trap focus inside the dialog (Tab/Shift+Tab cycle within)
3. Restore focus to the trigger element when closed

```js
function openModal(modal, trigger) {
  modal.removeAttribute('hidden');
  const focusable = modal.querySelectorAll(
    'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const first = focusable[0];
  const last = focusable[focusable.length - 1];

  first.focus();

  modal.addEventListener('keydown', (e) => {
    if (e.key !== 'Tab') return;
    if (e.shiftKey) {
      if (document.activeElement === first) { e.preventDefault(); last.focus(); }
    } else {
      if (document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  modal.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal(modal, trigger);
  });
}

function closeModal(modal, trigger) {
  modal.setAttribute('hidden', '');
  trigger.focus(); // return focus to where user was
}
```

### WCAG 2.2 Key Principles (POUR)

| Principle | Key requirements |
|---|---|
| **Perceivable** | Alt text, captions, color contrast ≥ 4.5:1 (AA), don't use color alone |
| **Operable** | Keyboard accessible, no keyboard traps, enough time, no seizure-triggering content |
| **Understandable** | Readable text, predictable behavior, error identification and suggestions |
| **Robust** | Valid HTML, name/role/value for all UI components |

---

# Part 6: Build Tools

---

## 22. Bundlers & Build Pipeline

### Vite vs Webpack

| | Vite | Webpack |
|---|---|---|
| Dev server | Native ESM — no bundling in dev | Bundles everything — slower cold start |
| HMR | Near-instant (module-level) | Slower (larger bundles) |
| Build | Rollup under the hood | Webpack |
| Config | Minimal by default | Highly configurable |
| Ecosystem | Growing — most Webpack plugins have equivalents | Mature, vast plugin ecosystem |
| Best for | New projects, frameworks (Vue, React, Svelte) | Complex enterprise apps with custom build needs |

```js
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    target: 'es2015',
    outDir: 'dist',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['recharts'],
        },
      },
    },
  },
  server: {
    proxy: {
      '/api': 'http://localhost:3000',
    },
  },
});
```

### Tree-Shaking

Tree-shaking removes unused exports from the final bundle. Requires:
- ES module syntax (`import`/`export`) — CJS `require()` is not statically analyzable
- No side effects on import (`"sideEffects": false` in `package.json`)

```js
// Only import what you use — bundler can eliminate the rest
import { debounce } from 'lodash-es'; // ✓ tree-shakeable ESM version
import _ from 'lodash';               // ✗ imports entire library

// Mark your package as side-effect free
// package.json
{
  "sideEffects": false
  // or list files with side effects:
  "sideEffects": ["./src/polyfills.js", "*.css"]
}
```

### Code Splitting

```js
// Webpack — dynamic import creates a separate chunk automatically
const LazyComponent = React.lazy(() => import('./HeavyComponent'));

// Webpack magic comments
const Chart = React.lazy(() =>
  import(/* webpackChunkName: "chart", webpackPrefetch: true */ './Chart')
);

// Vite — dynamic import works the same way, no config needed
```

### Source Maps

```js
// webpack.config.js
module.exports = {
  devtool: process.env.NODE_ENV === 'production'
    ? 'hidden-source-map'  // prod: maps exist but URL not appended to bundle
    : 'eval-source-map',   // dev: fastest rebuild, inline maps
};

// 'hidden-source-map' — upload to error tracking (Sentry) but don't expose publicly
```

### `browserslist`

Defines which browsers your build targets — used by Babel, PostCSS, and bundlers to determine what to transpile/polyfill.

```
# .browserslistrc
> 1%               # browsers used by more than 1% of users
last 2 versions    # last 2 versions of each browser
not dead           # browsers with official support
not ie 11          # explicitly exclude IE11

# Modern-only (smaller bundle)
> 0.5%, last 2 versions, Firefox ESR, not dead
```

```js
// Check what gets targeted
npx browserslist "> 1%, last 2 versions, not dead"

// Babel uses browserslist automatically via @babel/preset-env
// esbuild target override
import { build } from 'esbuild';
build({ target: ['es2020', 'chrome90', 'firefox88', 'safari14'] });
```

---

# Part 3 (continued): Browser & Web APIs

---

## 23. Service Workers & PWA

Service Workers are a browser-managed proxy running in a background thread — enabling offline support, background sync, and push notifications.

### Service Worker Lifecycle

```js
// main.js — register
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    const reg = await navigator.serviceWorker.register('/sw.js');
    console.log('SW registered:', reg.scope);
  });
}

// sw.js — install: precache static assets
const CACHE_NAME = 'v1';
const PRECACHE = ['/', '/index.html', '/styles.css', '/app.js'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE))
  );
  self.skipWaiting(); // activate immediately, don't wait for old SW to unload
});

// activate: clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim(); // take control of existing open tabs
});
```

### Caching Strategies

```js
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Cache First — static assets (images, fonts, hashed JS/CSS)
  if (request.destination === 'image' || request.destination === 'font') {
    event.respondWith(
      caches.match(request).then((cached) =>
        cached ?? fetch(request).then((res) => {
          caches.open(CACHE_NAME).then((c) => c.put(request, res.clone()));
          return res;
        })
      )
    );
    return;
  }

  // Network First — API data (fresh preferred, cache as offline fallback)
  if (request.url.includes('/api/')) {
    event.respondWith(
      fetch(request)
        .then((res) => {
          caches.open(CACHE_NAME).then((c) => c.put(request, res.clone()));
          return res;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Stale-While-Revalidate — HTML pages (show cached immediately, update in background)
  event.respondWith(
    caches.open(CACHE_NAME).then((cache) =>
      cache.match(request).then((cached) => {
        const networkFetch = fetch(request).then((res) => {
          cache.put(request, res.clone());
          return res;
        });
        return cached ?? networkFetch;
      })
    )
  );
});
```

### Caching Strategy Guide

| Strategy | Use for | Trade-off |
|---|---|---|
| **Cache First** | Hashed static assets (JS/CSS/fonts) | Stale until cache busted |
| **Network First** | API data | No offline if no cached fallback |
| **Stale-While-Revalidate** | HTML, semi-static content | May briefly show stale content |
| **Network Only** | Auth, payments | No offline support |
| **Cache Only** | Precached app shell | Never updates without new SW |

### Background Sync

```js
// sw.js — retry queued requests when connection restores
self.addEventListener('sync', (event) => {
  if (event.tag === 'submit-form') {
    event.waitUntil(submitQueuedForms());
  }
});

// main.js — queue on failure, register sync
async function submitForm(data) {
  try {
    await fetch('/api/submit', { method: 'POST', body: JSON.stringify(data) });
  } catch {
    await saveToIndexedDB(data);
    const reg = await navigator.serviceWorker.ready;
    await reg.sync.register('submit-form');
  }
}
```

### Push Notifications

```js
// Request permission and subscribe
const permission = await Notification.requestPermission();
if (permission !== 'granted') return;

const reg = await navigator.serviceWorker.ready;
const sub = await reg.pushManager.subscribe({
  userVisibleOnly: true,
  applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
});
await fetch('/api/push/subscribe', { method: 'POST', body: JSON.stringify(sub) });

// sw.js — receive push
self.addEventListener('push', (event) => {
  const { title, body, icon } = event.data.json();
  event.waitUntil(self.registration.showNotification(title, { body, icon }));
});
```

### Web App Manifest

```json
{
  "name": "My App",
  "short_name": "App",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#0070f3",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

```html
<link rel="manifest" href="/manifest.json" />
<meta name="theme-color" content="#0070f3" />
```

---

# Part 4 (continued): Performance

---

## 24. Image Optimization

### `srcset` and `sizes` — Responsive Images

```html
<!-- srcset: multiple resolutions — browser picks best fit -->
<img
  src="/hero-800.jpg"
  srcset="/hero-400.jpg 400w,
          /hero-800.jpg 800w,
          /hero-1600.jpg 1600w"
  sizes="(max-width: 768px) 100vw,
         (max-width: 1200px) 50vw,
         800px"
  alt="Hero"
  width="800"
  height="450"
/>
<!-- sizes: tells browser how wide the image renders at each breakpoint -->
<!-- browser calculates: rendered_width × pixel_density → picks smallest srcset entry that fits -->
```

### `<picture>` — Art Direction & Format Selection

```html
<!-- Art direction: different crops per breakpoint -->
<picture>
  <source media="(max-width: 600px)" srcset="/hero-portrait.jpg" />
  <source media="(min-width: 601px)" srcset="/hero-landscape.jpg" />
  <img src="/hero-landscape.jpg" alt="Hero" />
</picture>

<!-- Modern format with fallback -->
<picture>
  <source type="image/avif" srcset="/hero.avif" />
  <source type="image/webp" srcset="/hero.webp" />
  <img src="/hero.jpg" alt="Hero" width="800" height="450" />
</picture>
```

### Modern Formats

| Format | Compression | Support | Best for |
|---|---|---|---|
| **JPEG** | Lossy | Universal | Photos |
| **PNG** | Lossless | Universal | Transparency, screenshots |
| **WebP** | Lossy/Lossless | 95%+ | Replace JPEG/PNG — 25–35% smaller |
| **AVIF** | Lossy/Lossless | 90%+ | Best compression — 50% smaller than JPEG |
| **SVG** | Vector | Universal | Icons, logos, illustrations |

### Loading Priority

```html
<!-- LCP image: high priority, never lazy -->
<img src="hero.jpg" fetchpriority="high" loading="eager" alt="Hero" />

<!-- Below-fold images: defer until near viewport -->
<img src="photo.jpg" loading="lazy" decoding="async" alt="..." width="400" height="300" />

<!-- Preload LCP image in <head> so browser discovers it early -->
<link rel="preload" href="/hero.jpg" as="image" fetchpriority="high" />
```

---

## 25. Memory Leaks

### Detached DOM Nodes

```js
// LEAK: node removed from DOM but still referenced in JS — can't be GC'd
let detachedEl;
function create() {
  const el = document.createElement('div');
  document.body.appendChild(el);
  detachedEl = el;              // global keeps it alive
  document.body.removeChild(el); // removed from DOM but not from memory
}

// FIX: null the reference when done
detachedEl = null;
```

### Forgotten Timers & Intervals

```js
// LEAK: interval keeps running (and holding closure) after component unmounts
function startPolling() {
  setInterval(() => fetchData(), 1000); // id never stored — impossible to clear
}

// FIX: always return a cleanup that clears the timer
useEffect(() => {
  const id = setInterval(fetchData, 1000);
  return () => clearInterval(id);
}, []);
```

### Event Listener Leaks

```js
// LEAK: anonymous function — no stable reference to remove
window.addEventListener('resize', () => this.handleResize());

// FIX: stable reference, matched add/remove
class Widget {
  constructor() {
    this.onResize = this.handleResize.bind(this); // stable ref
  }
  mount()   { window.addEventListener('resize', this.onResize); }
  unmount() { window.removeEventListener('resize', this.onResize); }
}

// React
useEffect(() => {
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []);
```

### Closure Leaks

```js
// LEAK: closure captures large object even though handler doesn't need it
function createHandler() {
  const hugeData = new Array(1_000_000).fill('x'); // ~8MB
  return function handler() {
    console.log('clicked'); // hugeData never used but still captured
  };
}

// FIX: extract only what you need before closing
function createHandler() {
  const hugeData = new Array(1_000_000).fill('x');
  const count = hugeData.length; // extract primitive
  return function handler() {
    console.log(count); // only number held in closure
  };
}
```

### WeakMap / WeakRef — Leak-Safe References

```js
// WeakMap — values GC'd when key is no longer referenced elsewhere
const cache = new WeakMap();
function process(el) {
  if (cache.has(el)) return cache.get(el);
  const result = expensiveCompute(el);
  cache.set(el, result); // auto-released if el is removed from DOM
  return result;
}

// WeakRef — hold reference without preventing GC
const ref = new WeakRef(largeObject);
const obj = ref.deref(); // undefined if already GC'd
if (obj) use(obj);
```

### Detecting Leaks in Chrome DevTools

1. **Memory → Heap Snapshot** — take before/after an action
2. Filter "Objects allocated between snapshots"
3. Look for: **Detached HTMLElement**, objects with unexpectedly large counts
4. **Performance tab → JS Heap** — flat upward slope = leak; sawtooth = healthy GC

---

# Part 2 (continued): CSS

---

## 26. CSS Architecture

### BEM — Block Element Modifier

Flat naming convention — eliminates specificity conflicts by making every selector a single class.

```css
/* Block */
.card {}

/* Element: block__element */
.card__title {}
.card__image {}
.card__footer {}

/* Modifier: block--modifier or element--modifier */
.card--featured {}
.card__title--large {}
```

```html
<article class="card card--featured">
  <img class="card__image" src="..." />
  <h2 class="card__title card__title--large">Title</h2>
  <footer class="card__footer">...</footer>
</article>
```

**Pros:** No specificity wars, grep-friendly, explicit relationships  
**Cons:** Verbose class names, manual discipline required

### CSS Modules

Classes scoped at build time — compiled to unique hashes, zero runtime cost.

```css
/* Button.module.css */
.btn { background: blue; padding: 0.5rem 1rem; }
.primary { font-weight: bold; }
```

```jsx
import styles from './Button.module.css';
import clsx from 'clsx';

// Compiled output: <button class="Button_btn__a3f2 Button_primary__b1c9">
<button className={clsx(styles.btn, isPrimary && styles.primary)}>
  Click
</button>
```

**Pros:** True scoping, works with any CSS, great TypeScript support  
**Cons:** Dynamic styles based on JS values are awkward, needs build tooling

### CSS-in-JS — styled-components / Emotion

```jsx
import styled from 'styled-components';

const Button = styled.button<{ $primary?: boolean }>`
  background: ${({ $primary }) => ($primary ? 'blue' : 'white')};
  color: ${({ $primary }) => ($primary ? 'white' : 'blue')};
  padding: 0.5rem 1rem;
  border-radius: 4px;
`;

<Button $primary>Submit</Button>
```

**Pros:** Co-located styles, full dynamic styling from props, auto-scoped  
**Cons:** Runtime overhead (CSS generated at render), larger JS bundles, SSR complexity

**Zero-runtime alternatives:** Linaria, vanilla-extract — extract static CSS at build time.

### Utility-First — Tailwind CSS

```html
<button class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors">
  Submit
</button>
```

**Pros:** No naming decisions, minimal CSS (dead code purged), enforces design system  
**Cons:** HTML bloat, readability requires familiarity, repeated patterns need component extraction

### Comparison

| Approach | Scoping | Dynamic styles | Bundle impact | Best for |
|---|---|---|---|---|
| **BEM** | Convention | Extra modifier classes | Minimal | Discipline without tooling |
| **CSS Modules** | Build-time hash | Limited | Minimal | Component libs, React apps |
| **CSS-in-JS** | Runtime | Full (JS props) | +JS bundle | Highly dynamic theming |
| **Tailwind** | Utility classes | Limited | Minimal CSS | Rapid dev, design systems |

---

# Part 7: Testing

---

## 27. Frontend Testing

### Testing Pyramid

```
         [  E2E  ]    ← few, slow, expensive  (Playwright, Cypress)
       [Integration]  ← component + API tests  (Testing Library)
      [  Unit Tests ] ← many, fast, cheap      (Vitest, Jest)
```

### Unit Testing with Vitest / Jest

```ts
// utils.test.ts
import { describe, it, expect, vi } from 'vitest';
import { formatCurrency } from './utils';

describe('formatCurrency', () => {
  it('formats positive amounts', () => {
    expect(formatCurrency(1234.5)).toBe('$1,234.50');
  });
  it('handles zero', () => {
    expect(formatCurrency(0)).toBe('$0.00');
  });
});

// Mocking modules
vi.mock('./api', () => ({
  fetchUser: vi.fn().mockResolvedValue({ id: 1, name: 'Alice' }),
}));
```

### Component Testing with Testing Library

```tsx
// Button.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

it('calls onClick when clicked', async () => {
  const handleClick = vi.fn();
  render(<Button onClick={handleClick}>Submit</Button>);

  await userEvent.click(screen.getByRole('button', { name: 'Submit' }));
  expect(handleClick).toHaveBeenCalledOnce();
});

it('shows loading state', () => {
  render(<Button loading>Submit</Button>);
  expect(screen.getByRole('button')).toBeDisabled();
});

// Async data loading
it('shows users after load', async () => {
  render(<UserList />);
  expect(screen.getByText('Loading...')).toBeInTheDocument();
  await waitFor(() => {
    expect(screen.getByText('Alice')).toBeInTheDocument();
  });
});
```

**Key principles:**
- Query by what users see: `getByRole`, `getByText`, `getByLabelText` — never by class or test IDs
- `userEvent` over `fireEvent` — simulates real pointer/keyboard interactions
- `getBy*` throws if not found. `queryBy*` returns null. `findBy*` is async (awaitable)

### E2E Testing with Playwright

```ts
// checkout.spec.ts
import { test, expect } from '@playwright/test';

test('user completes checkout', async ({ page }) => {
  await page.goto('/shop');
  await page.getByRole('button', { name: 'Add to cart' }).first().click();
  await page.getByRole('link', { name: 'Cart (1)' }).click();
  await page.getByRole('button', { name: 'Checkout' }).click();
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByRole('button', { name: 'Pay' }).click();
  await expect(page.getByText('Order confirmed')).toBeVisible();
});

// Intercept API requests in tests
test('shows error on API failure', async ({ page }) => {
  await page.route('/api/orders', (route) => route.fulfill({ status: 500 }));
  await page.goto('/checkout');
  await expect(page.getByText('Something went wrong')).toBeVisible();
});
```

### What to Test at Each Layer

| Layer | Focus | Tool |
|---|---|---|
| Pure functions | Logic, edge cases | Vitest/Jest |
| Components | Render, interactions, a11y | Testing Library |
| Custom hooks | State transitions, side effects | `renderHook` |
| Forms | Validation, submit, error states | Testing Library |
| Critical flows | Happy path + failure paths end-to-end | Playwright |
| Visual regressions | CSS changes, layout breakage | Storybook + Chromatic |

---

# Part 1 (continued): HTML

---

## 28. SEO Beyond Meta Tags

### Structured Data — JSON-LD

Structured data tells search engines what content *means* — enables rich results (star ratings, prices, events) in SERPs.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Wireless Headphones",
  "description": "Premium noise-canceling headphones",
  "image": "https://example.com/headphones.jpg",
  "offers": {
    "@type": "Offer",
    "price": "299.00",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.7",
    "reviewCount": "1284"
  }
}
</script>
```

Other common types: `Article`, `BreadcrumbList`, `FAQPage`, `Organization`, `Event`, `Recipe`

### SSR vs CSR — SEO Implications

```
CSR (React SPA):
  Browser → empty HTML → JS downloads → JS runs → content renders
  Googlebot sees content, but timing is unreliable — indexing may be delayed

SSR (Next.js getServerSideProps):
  Browser → full HTML with content → JS hydrates
  Googlebot indexes full content immediately on first request

SSG (Static Site Generation):
  HTML pre-rendered at build time — best for SEO + performance

ISR (Incremental Static Regeneration):
  Static HTML + background revalidation — fresh content without per-request SSR cost
```

```jsx
// Next.js ISR — static with periodic revalidation
export async function getStaticProps() {
  const products = await fetchProducts();
  return {
    props: { products },
    revalidate: 3600, // regenerate at most every hour
  };
}
```

### `robots.txt`

```
User-agent: *
Allow: /

Disallow: /admin/
Disallow: /api/
Disallow: /private/

# Block AI crawlers from training data
User-agent: GPTBot
Disallow: /

Sitemap: https://example.com/sitemap.xml
```

### `sitemap.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2026-01-01</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/products</loc>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

### Canonicals & Hreflang

```html
<!-- Prevent duplicate-content penalty from URL variations -->
<link rel="canonical" href="https://example.com/product/headphones" />
<!-- Handles: ?utm_source=..., trailing slashes, www vs non-www -->

<!-- Language/region variants -->
<link rel="alternate" hreflang="en" href="https://example.com/en/page" />
<link rel="alternate" hreflang="ar" href="https://example.com/ar/page" />
<link rel="alternate" hreflang="x-default" href="https://example.com/page" />
```

Core Web Vitals (LCP, CLS, INP) are Google ranking factors — a technically well-structured page with poor performance loses ranking to a comparable page with good CWV.

---

# Part 3 (continued): Browser & Web APIs

---

## 29. Global Error Handling

### `window.onerror` and `addEventListener('error')`

```js
// window.onerror — catches uncaught synchronous errors
window.onerror = function (message, source, lineno, colno, error) {
  reportToSentry(error ?? new Error(message));
  return true; // suppress default browser error UI
};

// addEventListener — also catches resource load failures (img, script, link)
window.addEventListener('error', (event) => {
  if (event.target !== window) {
    // Resource failed to load
    console.error('Resource load failed:', event.target.src || event.target.href);
    return;
  }
  reportToSentry(event.error);
}, true); // true = capture phase — required for resource errors
```

### `unhandledrejection` — Unhandled Promise Rejections

```js
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  reportToSentry(event.reason);
  event.preventDefault(); // suppress browser console warning
});

// Fires if a previously unhandled rejection later gets a .catch()
window.addEventListener('rejectionhandled', (event) => {
  console.log('Late handler attached:', event.reason);
});
```

### Error Boundaries (React)

```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    // info.componentStack — which component threw
    Sentry.captureException(error, { contexts: { react: info } });
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? <div>Something went wrong.</div>;
    }
    return this.props.children;
  }
}

// Wrap sections independently so one failure doesn't crash the whole app
<ErrorBoundary fallback={<ErrorPage />}>
  <App />
</ErrorBoundary>
```

### Centralized Error Reporter

```js
function reportError(error, context = {}) {
  if (process.env.NODE_ENV === 'development') {
    console.error(error, context);
  }
  Sentry.captureException(error, { extra: context });
  if (context.userFacing) {
    showToast({ type: 'error', message: context.message ?? 'Something went wrong' });
  }
}
```

---

# Part 4 (continued): Performance

---

## 30. Performance Monitoring

### Lighthouse

Scores (0–100) across Performance, Accessibility, Best Practices, and SEO.

```bash
# Run against a URL
npx lighthouse https://example.com --output html --view

# CI — fail build if performance drops below threshold
npx lighthouse https://example.com --budget-path=budget.json
```

**Key Performance metrics:** LCP, TBT (Total Blocking Time — lab proxy for INP), CLS, Speed Index, TTFB

### Performance Budgets

```json
[
  {
    "path": "/*",
    "timings": [
      { "metric": "interactive",           "budget": 3500 },
      { "metric": "first-contentful-paint","budget": 1500 }
    ],
    "resourceSizes": [
      { "resourceType": "script", "budget": 300 },
      { "resourceType": "total",  "budget": 1000 }
    ]
  }
]
```

### RUM — Real User Monitoring

Lighthouse measures synthetic (lab) performance. RUM captures actual user experience.

```js
import { onLCP, onCLS, onINP, onFCP, onTTFB } from 'web-vitals';

function send({ name, value, rating }) {
  fetch('/analytics', {
    method: 'POST',
    body: JSON.stringify({ metric: name, value, rating }),
    keepalive: true, // completes even if page unloads
  });
}

onLCP(send);
onCLS(send);
onINP(send);
onFCP(send);
onTTFB(send);
```

### `PerformanceObserver`

```js
// Long tasks > 50ms — main thread blocked, interaction latency spike
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.warn(`Long task: ${entry.duration.toFixed(1)}ms`);
  }
}).observe({ entryTypes: ['longtask'] });

// Navigation timing — full page load breakdown
const [nav] = performance.getEntriesByType('navigation');
console.log({
  dns:            nav.domainLookupEnd - nav.domainLookupStart,
  tcp:            nav.connectEnd - nav.connectStart,
  ttfb:           nav.responseStart - nav.requestStart,
  domInteractive: nav.domInteractive,
  domComplete:    nav.domComplete,
});
```

### Monitoring Tools

| Tool | Type | What it measures |
|---|---|---|
| **Lighthouse** | Lab (synthetic) | Scores, opportunities, full audit |
| **WebPageTest** | Lab | Waterfall, filmstrip, multi-region |
| **Chrome UX Report (CrUX)** | Field (RUM) | 75th-percentile CWV from real Chrome users |
| **web-vitals.js** | Field (RUM) | CWV from your own users |
| **Sentry Performance** | Field + tracing | Slowest transactions, error correlation |
| **Datadog RUM** | Field | Session replay, custom metrics |

---

*Last updated: 2026-06-04*
