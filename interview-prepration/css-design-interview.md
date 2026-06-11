# CSS & Design Interview Reference

A senior-focused reference covering modern CSS, layout systems, responsive design, and the visual/UX design fundamentals that come up in frontend interviews. Concept + code snippet format, organized from foundational to advanced.

---

## Table of Contents

### Part 1: CSS Fundamentals
1. [The Cascade, Specificity & Inheritance](#1-the-cascade-specificity--inheritance)
2. [Box Model & `box-sizing`](#2-box-model--box-sizing)
3. [Units: Absolute, Relative & Viewport](#3-units-absolute-relative--viewport)
4. [Display, Positioning & Stacking Context](#4-display-positioning--stacking-context)

### Part 2: Layout
5. [Flexbox](#5-flexbox)
6. [CSS Grid](#6-css-grid)
7. [Flexbox vs Grid — When to Use Which](#7-flexbox-vs-grid--when-to-use-which)

### Part 3: Responsive & Modern CSS
8. [Responsive Design](#8-responsive-design)
9. [Custom Properties (CSS Variables)](#9-custom-properties-css-variables)
10. [Modern CSS (2023–2026)](#10-modern-css-20232026)
11. [Animations & Transitions](#11-animations--transitions)
12. [CSS Architecture & Methodologies](#12-css-architecture--methodologies)
13. [Performance](#13-performance)

### Part 4: Design
14. [Visual Design Fundamentals](#14-visual-design-fundamentals)
15. [Layout & Composition](#15-layout--composition)
16. [Color Theory](#16-color-theory)
17. [Typography](#17-typography)
18. [Design Systems](#18-design-systems)
19. [UX Principles](#19-ux-principles)
20. [Accessibility (a11y)](#20-accessibility-a11y)

---

# Part 1: CSS Fundamentals

---

## 1. The Cascade, Specificity & Inheritance

When multiple rules target the same element and property, CSS resolves the conflict in this order:

1. **Origin & importance** — browser defaults < author styles < author `!important` < user `!important`
2. **Specificity** — more specific selectors win
3. **Source order** — last declaration wins among equal specificity

**Specificity** is scored as `(inline, IDs, classes/attributes/pseudo-classes, elements/pseudo-elements)`:

```css
/* Specificity examples (higher tuple wins) */
*               { }  /* (0,0,0,0) */
li              { }  /* (0,0,0,1) */
.list li        { }  /* (0,0,1,1) */
#nav .list li   { }  /* (1,0,1,1) */
style="..."          /* (1,0,0,0) — inline */
```

```css
/* :is() takes the specificity of its MOST specific argument */
:is(#a, .b, p) { } /* (1,0,0,0) */

/* :where() ALWAYS has zero specificity — great for low-priority base styles */
:where(#a, .b, p) { } /* (0,0,0,0) — easy to override */
```

**Inheritance** — some properties inherit by default (`color`, `font`, `line-height`, `visibility`), most layout/box properties do not (`margin`, `padding`, `border`, `width`). Control it explicitly:

```css
.child {
  color: inherit;   /* take parent's computed value */
  border: initial;  /* reset to the property's spec default */
  all: unset;        /* inherit if inheritable, else initial */
}
```

> **Interview tip:** Avoid `!important` and ID selectors in component CSS — they break the cascade and force escalation wars. Prefer low, flat specificity (single classes) so styles stay overridable.

---

## 2. Box Model & `box-sizing`

Every element is a box: `content → padding → border → margin`. The critical question is whether `width` includes padding/border.

```css
/* content-box (default): width = content only; padding/border add on top */
.a { box-sizing: content-box; width: 200px; padding: 20px; } /* renders 240px wide */

/* border-box: width INCLUDES padding and border — far more predictable */
.b { box-sizing: border-box; width: 200px; padding: 20px; }  /* renders 200px wide */

/* Standard reset — make everything border-box */
*, *::before, *::after { box-sizing: border-box; }
```

**Margin collapsing** — adjacent vertical margins merge into the larger of the two (a common source of "why is there a gap?"):

```css
/* p { margin: 20px 0 } stacked → 20px between them, NOT 40px */
/* Collapsing is prevented by: flex/grid containers, padding/border between, overflow != visible */
```

---

## 3. Units: Absolute, Relative & Viewport

```css
.examples {
  /* Absolute */
  width: 100px;        /* px — fixed, predictable */

  /* Font-relative */
  font-size: 1.5rem;   /* rem — relative to ROOT font-size (consistent, accessible) */
  padding: 1.5em;      /* em — relative to THIS element's font-size (compounds in nesting) */
  width: 50ch;         /* ch — width of "0"; great for readable line lengths */

  /* Viewport-relative */
  height: 100vh;       /* 1% of viewport height */
  width: 50vw;         /* 1% of viewport width */
  font-size: 4vmin;    /* 1% of the smaller viewport axis */

  /* New viewport units (2023) — handle mobile browser chrome */
  height: 100dvh;      /* dynamic vh — adjusts as URL bar shows/hides */
  min-height: 100svh;  /* small vh — assumes chrome is visible */
  /* lvh = large viewport height (chrome hidden) */
}
```

**Rule of thumb:** `rem` for typography and spacing (respects user font-size settings → accessible), `%`/`fr`/viewport units for layout, `ch` for line-length limits, `px` only for things that should never scale (hairline borders).

---

## 4. Display, Positioning & Stacking Context

```css
/* Positioning */
.relative { position: relative; }  /* offset from its normal spot; new positioning context */
.absolute { position: absolute; top: 0; }  /* relative to nearest positioned ancestor */
.fixed    { position: fixed; }     /* relative to viewport — stays on scroll */
.sticky   { position: sticky; top: 0; } /* relative until it hits a scroll threshold, then fixed */
```

**Stacking context** decides `z-index` painting order. A new one is created by: `position` + `z-index`, `opacity < 1`, `transform`, `filter`, `will-change`, `isolation: isolate`, flex/grid children with `z-index`. The trap:

```css
/* A z-index:9999 child CANNOT escape its parent's stacking context.
   If .parent has opacity:0.99, its child's z-index is local to .parent. */
.parent { opacity: 0.99; }       /* creates a stacking context */
.child  { position: absolute; z-index: 9999; } /* still trapped under .parent's siblings */

/* Fix: raise the parent, or isolate intentionally */
.modal-root { isolation: isolate; } /* new context without other side effects */
```

---

# Part 2: Layout

---

## 5. Flexbox

One-dimensional layout — distributes space along a single axis (row or column).

```css
.container {
  display: flex;
  flex-direction: row;          /* row | column — sets the MAIN axis */
  justify-content: space-between; /* alignment along MAIN axis */
  align-items: center;          /* alignment along CROSS axis */
  gap: 16px;                     /* spacing between items (replaces margin hacks) */
  flex-wrap: wrap;               /* allow items to wrap to new lines */
}

.item {
  /* flex: grow shrink basis */
  flex: 1 1 0;       /* grow & shrink from a 0 basis → equal columns */
  flex: 0 0 200px;   /* fixed 200px, never grow/shrink */
  flex: 1;           /* shorthand for 1 1 0% — fill available space */
  align-self: flex-end; /* override align-items for one item */
}
```

**Common patterns:**

```css
/* Push one item to the right (nav with logo left, links right) */
.nav .spacer { margin-left: auto; }

/* Sticky footer — content fills, footer pinned to bottom */
body { display: flex; flex-direction: column; min-height: 100vh; }
main { flex: 1; }
```

---

## 6. CSS Grid

Two-dimensional layout — rows and columns together.

```css
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 3 equal columns */
  grid-template-rows: auto 1fr auto;
  gap: 16px;
}

/* Responsive without media queries — auto-fit + minmax */
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  /* as many 250px+ columns as fit; they stretch to fill the row */
  gap: 24px;
}
```

**Named areas — readable page layouts:**

```css
.layout {
  display: grid;
  grid-template-columns: 200px 1fr;
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
}
.header  { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main    { grid-area: main; }
.footer  { grid-area: footer; }
```

**`auto-fit` vs `auto-fill`:** `auto-fill` keeps empty phantom columns (items stay their min size); `auto-fit` collapses empties so existing items stretch to fill. Use `auto-fit` for "fill the row," `auto-fill` for "keep a fixed grid."

---

## 7. Flexbox vs Grid — When to Use Which

| | Flexbox | Grid |
|---|---|---|
| Dimension | 1D (row **or** column) | 2D (rows **and** columns) |
| Sizing model | Content-out (items size themselves) | Layout-in (define the structure first) |
| Best for | Toolbars, nav, button groups, distributing items in a line | Page layouts, card galleries, anything with row+column alignment |
| Alignment | Along one axis | Both axes simultaneously |

**Rule of thumb:** Grid for the overall page/section structure; Flexbox for the components inside each grid cell. They compose — a grid cell can be a flex container.

---

# Part 3: Responsive & Modern CSS

---

## 8. Responsive Design

**Mobile-first** — write base styles for small screens, layer enhancements with `min-width` queries.

```css
/* Base = mobile */
.container { padding: 16px; }

/* Tablet and up */
@media (min-width: 768px) {
  .container { padding: 32px; max-width: 720px; margin-inline: auto; }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container { max-width: 1140px; }
}
```

**Container queries (2023)** — respond to the *parent container's* size instead of the viewport. The big shift: truly reusable components that adapt to wherever they're placed.

```css
.card-wrapper { container-type: inline-size; container-name: card; }

@container card (min-width: 400px) {
  .card { display: grid; grid-template-columns: 120px 1fr; }
}
```

**Other responsive tools:**

```css
/* clamp() — fluid sizing without breakpoints: clamp(min, preferred, max) */
font-size: clamp(1rem, 2.5vw, 1.5rem);
width: min(90%, 1200px);   /* whichever is smaller */
padding: max(16px, 5vw);   /* whichever is larger */

/* Respect user preferences */
@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
@media (prefers-color-scheme: dark) { :root { --bg: #111; --fg: #eee; } }
```

---

## 9. Custom Properties (CSS Variables)

Unlike Sass variables, these are **live at runtime**, cascade, inherit, and can be read/written from JavaScript.

```css
:root {
  --primary: #3b82f6;
  --space: 8px;
  --radius: 6px;
}

.button {
  background: var(--primary);
  padding: calc(var(--space) * 2);
  border-radius: var(--radius);
  /* fallback if the variable is undefined */
  color: var(--btn-text, white);
}

/* Theming — override the same variables in a scope */
[data-theme='dark'] { --primary: #60a5fa; }
```

```js
// Read & write from JS — powers dynamic theming, no class swapping
el.style.setProperty('--primary', '#ef4444');
getComputedStyle(el).getPropertyValue('--primary');
```

---

## 10. Modern CSS (2023–2026)

Features that frequently come up as "what's new in CSS" questions:

```css
/* Nesting (native, no preprocessor needed) */
.card {
  padding: 16px;
  & .title { font-weight: 700; }
  &:hover { box-shadow: 0 4px 12px rgba(0,0,0,.1); }
  @media (min-width: 768px) { padding: 24px; }
}

/* :has() — the "parent selector" — style based on descendants/state */
.card:has(img) { padding-top: 0; }
.form:has(input:invalid) .submit { opacity: 0.5; pointer-events: none; }
label:has(+ input:focus) { color: var(--primary); }

/* Cascade layers — control specificity by declaration order, not selector weight */
@layer reset, base, components, utilities;
@layer components { .btn { color: blue; } } /* utilities always beat components */

/* Logical properties — direction-agnostic (RTL/LTR friendly) */
.box { margin-inline: auto; padding-block: 1rem; inset-inline-start: 0; }

/* aspect-ratio — no more padding-top hacks */
.video { aspect-ratio: 16 / 9; width: 100%; }

/* Subgrid — child grid aligns to parent's tracks */
.child { display: grid; grid-template-columns: subgrid; }

/* color-mix() and relative colors */
background: color-mix(in srgb, var(--primary) 80%, white);
--primary-dark: hsl(from var(--primary) h s calc(l - 10%));

/* accent-color — theme native form controls in one line */
:root { accent-color: var(--primary); }

/* Scroll-driven animations, view transitions, anchor positioning (newest, 2024–2026) */
::view-transition-old(root) { animation: fade-out 0.2s; }
```

---

## 11. Animations & Transitions

```css
/* Transition — animate between two states */
.button {
  transition: transform 0.2s ease, background 0.2s ease;
}
.button:hover { transform: translateY(-2px); }

/* Keyframe animation — multi-step, looping */
@keyframes spin { to { transform: rotate(360deg); } }
.spinner { animation: spin 1s linear infinite; }
```

**Performance — only animate cheap properties.** `transform` and `opacity` are GPU-composited and skip layout/paint. Animating `width`, `top`, `margin`, or `box-shadow` triggers layout/paint on every frame and janks.

```css
/* Bad — triggers layout every frame */
.box { transition: width 0.3s, left 0.3s; }

/* Good — composited, 60fps */
.box { transition: transform 0.3s; }
.box:hover { transform: scale(1.1) translateX(20px); }

/* will-change — hint the browser to promote to its own layer (use sparingly) */
.modal { will-change: transform, opacity; }
```

---

## 12. CSS Architecture & Methodologies

Strategies to keep CSS maintainable at scale — interviewers ask how you avoid specificity wars and global-namespace collisions.

- **BEM** (`block__element--modifier`) — flat, low-specificity naming convention. `.card__title--featured`. Predictable, but verbose.
- **Utility-first (Tailwind)** — compose small single-purpose classes in markup (`flex items-center gap-4`). Fast to build, no naming, but markup-heavy.
- **CSS Modules** — locally-scoped class names hashed at build time; no global collisions.
- **CSS-in-JS** (styled-components, Emotion) — co-locate styles with components, dynamic theming via props.
- **Cascade layers + design tokens** — modern native approach: organize with `@layer`, drive values with custom properties.

```css
/* BEM example */
.card { }
.card__title { }
.card__title--featured { }
.card--compact { }
```

> **Interview framing:** there's no single "right" answer — articulate the tradeoff. Utility-first optimizes for build speed and consistency; BEM/Modules optimize for readable, semantic component styles. Pick based on team size and design-system maturity.

---

## 13. Performance

- **Selector cost is rarely the bottleneck** — layout thrashing and paint are. Don't over-optimize selectors; do avoid animating layout properties.
- **`content-visibility: auto`** — skip rendering off-screen content, huge wins on long pages.
- **Critical CSS** — inline above-the-fold styles, defer the rest to avoid render-blocking.
- **Reduce reflows** — batch DOM reads/writes; reading layout (`offsetHeight`) after a write forces synchronous reflow.
- **`contain: layout paint`** — isolate a subtree so changes inside don't reflow the whole page.

```css
.long-list-item {
  content-visibility: auto;
  contain-intrinsic-size: 0 80px; /* reserve space to avoid scrollbar jumps */
}
```

---

# Part 4: Design

---

## 14. Visual Design Fundamentals

The core principles that separate polished UIs from amateur ones. Engineers who understand these implement designs more faithfully and catch issues early.

- **Hierarchy** — guide the eye to what matters first via size, weight, color, and position. Every screen has one primary action.
- **Contrast** — differences (size, color, weight) create emphasis and improve scannability. Low contrast = everything feels equally (un)important.
- **Alignment** — elements share edges/centers on an invisible grid. Misalignment reads as "broken" even when users can't articulate why.
- **Proximity** — related items grouped close; unrelated items spaced apart. Spacing communicates relationships.
- **Repetition / consistency** — reuse styles, spacing, and components so the UI feels coherent and predictable.
- **Balance** — distribute visual weight (symmetric = formal/stable, asymmetric = dynamic).
- **White space** — emptiness is a feature, not wasted space. It creates focus, improves readability, and signals premium quality.

> **Interview framing:** "good design is invisible." When asked to critique a UI, walk through these principles systematically rather than saying "it looks off."

---

## 15. Layout & Composition

- **Grid systems** — most designs sit on a 12-column grid; it provides structure and consistent alignment. Translate to CSS Grid/Flexbox.
- **Spacing scale** — use a consistent scale (e.g. 4px base: 4, 8, 12, 16, 24, 32, 48, 64). Arbitrary spacing (`13px`, `27px`) is the #1 tell of unsystematic design.
- **The 8-point grid** — size and space everything in multiples of 8 (occasionally 4) for rhythm and pixel-snapping across screen densities.
- **Visual rhythm** — consistent vertical spacing between sections creates a predictable scanning pattern.
- **Optical vs mathematical alignment** — sometimes you nudge an element a pixel off-center so it *looks* centered (e.g. a play-button triangle, which is right-heavy). Trust the eye over the ruler.
- **Z-pattern / F-pattern** — eyes scan landing pages in a Z and text-heavy pages in an F. Place key elements along those paths.

---

## 16. Color Theory

```
HSL is the most intuitive model for UI: hsl(hue, saturation, lightness)
  - Hue (0–360°): the color itself
  - Saturation (0–100%): intensity/vividness
  - Lightness (0–100%): how light/dark
Adjusting lightness while keeping hue/saturation → clean tints & shades for a palette.
```

- **Palette structure** — a primary (brand), a secondary/accent, and a neutral ramp (grays for text, borders, backgrounds). Most of a real UI is neutrals; color is used sparingly for emphasis.
- **The 60-30-10 rule** — 60% dominant (usually neutral background), 30% secondary, 10% accent (CTAs, highlights).
- **Color relationships** — complementary (opposite on the wheel, high energy), analogous (adjacent, harmonious), triadic (balanced variety).
- **Semantic colors** — success (green), warning (amber), danger (red), info (blue). Keep them consistent system-wide.
- **Don't rely on color alone** — pair it with icons/text for colorblind users and accessibility.
- **Contrast for accessibility** — WCAG AA requires **4.5:1** for body text, **3:1** for large text (18px bold / 24px). Verify with a contrast checker.

```css
/* Generate a tint/shade ramp from one hue via lightness */
:root {
  --brand-h: 217; --brand-s: 91%;
  --brand-500: hsl(var(--brand-h) var(--brand-s) 60%);
  --brand-700: hsl(var(--brand-h) var(--brand-s) 45%); /* darker for hover */
  --brand-100: hsl(var(--brand-h) var(--brand-s) 92%); /* light tint for backgrounds */
}
```

---

## 17. Typography

- **Type scale** — pick a modular scale (e.g. ratio 1.25 "major third": 16, 20, 25, 31, 39…) rather than arbitrary sizes. Creates harmony between heading levels.
- **Line height (leading)** — ~1.5 for body text, tighter (~1.1–1.3) for large headings. Improves readability.
- **Line length (measure)** — 45–75 characters per line is optimal for reading. Cap it with `max-width: 65ch`.
- **Hierarchy** — distinguish levels with size, weight, and spacing — not just bigger text. Limit to a few weights (e.g. 400/600/700).
- **Font pairing** — typically one display/heading font + one body font; ensure they contrast yet harmonize. When unsure, a single well-chosen family with multiple weights is safest.
- **Pairing units to accessibility** — size body text in `rem` so it honors the user's browser font-size setting.

```css
body {
  font-size: 1rem;        /* respects user settings */
  line-height: 1.6;
  max-width: 65ch;        /* readable measure */
  font-family: 'Inter', system-ui, sans-serif;
}
h1 { font-size: 2.441rem; line-height: 1.15; font-weight: 700; }
h2 { font-size: 1.953rem; line-height: 1.2; }
```

---

## 18. Design Systems

A design system is the single source of truth that keeps product, design, and engineering aligned — and is increasingly expected knowledge for senior frontend roles.

- **Design tokens** — named primitives for color, spacing, typography, radii, shadows, z-index. The bridge between design tools and code (often the same JSON drives Figma and CSS variables).
- **Components** — reusable, documented building blocks (Button, Input, Modal) with defined variants and states.
- **Atomic design** — a mental model: atoms (button, label) → molecules (search field) → organisms (header) → templates → pages.
- **States** — every interactive component needs default, hover, focus, active, disabled, loading, and error states designed up front.
- **Documentation** — usage guidelines, do/don't examples, accessibility notes. Tools: Storybook, Figma libraries.
- **Why it matters:** consistency at scale, faster delivery (build once, reuse everywhere), and a shared vocabulary between disciplines.

```css
/* Tokens as CSS variables — the implementation layer of a design system */
:root {
  /* color tokens */
  --color-text: hsl(222 47% 11%);
  --color-bg: hsl(0 0% 100%);
  /* spacing scale */
  --space-1: 4px;  --space-2: 8px;  --space-3: 16px;  --space-4: 24px;
  /* elevation */
  --shadow-sm: 0 1px 2px rgba(0,0,0,.05);
  --radius-md: 8px;
}
```

---

## 19. UX Principles

- **Affordances & signifiers** — make interactive elements *look* interactive (buttons look pressable, links underlined). Don't make users guess.
- **Feedback** — every action gets an immediate, visible response (hover states, loading spinners, success toasts). Silence feels broken.
- **Consistency** — same patterns behave the same way everywhere; leverage platform conventions so users transfer existing knowledge.
- **Error prevention & recovery** — disable invalid actions, confirm destructive ones, write clear error messages that say how to fix the problem.
- **Recognition over recall** — show options rather than make users remember them (menus, autocomplete).
- **Progressive disclosure** — reveal complexity gradually; show the essentials first, advanced options on demand.
- **Fitts's Law** — bigger, closer targets are faster to hit. Make primary actions large; put related controls near each other.
- **Hick's Law** — more choices = slower decisions. Reduce options to speed users up.
- **The fold is a myth, but priority isn't** — users scroll, but what's first still sets expectations.
- **Loading & empty states** — design them deliberately. Skeleton screens feel faster than spinners; empty states should guide the next action.

> Nielsen's 10 usability heuristics are the canonical checklist — worth knowing by name (visibility of system status, match to real world, user control, consistency, error prevention, recognition, flexibility, minimalist design, error recovery, help).

---

## 20. Accessibility (a11y)

Accessibility is a design *and* engineering responsibility, and a common senior interview topic.

- **Semantic HTML first** — native `<button>`, `<a>`, `<nav>`, `<label>` give you keyboard support, focus, and screen-reader roles for free. Reach for ARIA only when no native element fits.
- **Keyboard navigation** — everything operable by mouse must work via keyboard. Maintain a logical tab order and a **visible focus indicator** (never `outline: none` without a replacement).
- **Color contrast** — WCAG AA: 4.5:1 for normal text, 3:1 for large text and UI components.
- **Don't rely on color alone** — pair color with text/icons (e.g. error fields get an icon + message, not just red).
- **Alt text** — meaningful images get descriptive `alt`; decorative images get `alt=""` so screen readers skip them.
- **ARIA when needed** — `aria-label`, `aria-live` (announce dynamic updates), `role`, `aria-expanded` for custom widgets. The first rule of ARIA: don't use ARIA if a native element works.
- **Respect preferences** — `prefers-reduced-motion`, `prefers-color-scheme`, and zoom up to 200% without breaking layout.
- **Forms** — every input needs an associated `<label>`; group related fields with `<fieldset>`/`<legend>`; surface errors programmatically.

```css
/* Visible focus for keyboard users without showing it on mouse click */
:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }

/* Screen-reader-only text — visually hidden but announced */
.sr-only {
  position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0;
}
```

---

_Last updated: 2026-06-11_
