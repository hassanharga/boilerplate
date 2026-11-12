# Accessibility and localization

Use this reference for interactive UI. It helps specify and verify accessible
behavior; it does not prove compliance.

## Establish the target

For new web work, use WCAG 2.2 Level AA as the default design baseline unless an
approved product requirement says otherwise. Verify the current standard before
citing it. WCAG 3 is not a replacement target until it becomes a completed
standard and the product adopts it.

Native applications also need current Apple, Android, Windows, or other applicable
platform guidance. Legal and procurement obligations depend on product,
jurisdiction, customer, and date. Look them up from current primary sources.

Do not assume:

- that WCAG conformance satisfies every law or procurement standard;
- that a design brief proves implementation conformance;
- that a newer WCAG version has automatically entered a referenced regulation;
- that passing an automated scanner covers keyboard, screen-reader, cognitive, or
  usability needs.

When a legal mapping matters, record the jurisdiction, product category, source,
version, and date checked.

## Design requirements that need explicit decisions

Cover the criteria relevant to the scoped interface:

| Area | Brief must settle |
| --- | --- |
| Text contrast | Rendered foreground and background pairs, including states |
| Non-text contrast | Boundaries, focus, controls, and meaningful graphics |
| Color use | A second cue for status, validation, and data |
| Text resize and reflow | Behavior at 200% text or zoom and narrow widths |
| Keyboard | Reachability, order, activation, escape, and no traps |
| Focus | Visible treatment, restoration, and protection from sticky overlays |
| Target size | Product and platform target, spacing, and justified exceptions |
| Forms | Labels, instructions, errors, suggestions, and preserved input |
| Authentication | Password-manager and paste support; accessible alternatives |
| Motion | Pause or stop behavior and reduced-motion alternative |
| Time | Warning, extension, recovery, and saved progress |
| Drag or gesture | A simple pointer and keyboard alternative |

Use the exact normative wording only when needed and cite the current standard.
The brief should explain product behavior in plain language.

## Contrast

Use the skill's bundled scripts/contrast.py, resolved against the skill directory, for
opaque sRGB hexadecimal values under the WCAG 2.x
relative-luminance method. APCA may be recorded as supplementary research when a
team uses it, but it does not replace the approved WCAG 2.x conformance method.

Check the rendered pairs the product actually uses:

- primary, secondary, placeholder, and disabled text on each surface;
- labels on action and semantic fills;
- links in surrounding text;
- input boundaries, selected states, and focus rings;
- icons and meaningful graphics;
- light, dark, and high-contrast themes in scope.

Alpha colors must first be composited against the real surface. Gradients and
images need worst-case rendered checks, not a single estimated pair.

## Keyboard and focus

For each key flow, specify:

- entry focus and logical sequence;
- activation keys for custom interactions;
- escape and cancellation behavior;
- focus containment only where required;
- focus return after a temporary layer closes;
- behavior after deletion, filtering, pagination, and route changes;
- skip links and landmark order for web products.

Prefer native elements. For a custom widget, reference the current platform or
ARIA Authoring Practices pattern and state its role, properties, keyboard
behavior, and announcements.

Do not add global shortcuts without checking conflicts with browser, operating
system, assistive technology, localization, and editable fields.

## Status and recovery

Define what assistive technology receives for:

- loading and completion;
- validation and blocking errors;
- background success;
- stale or offline data;
- destructive changes and undo;
- session expiry;
- partial or duplicate submission.

Use assertive announcements only for information that needs immediate attention.
Keep visible messages available long enough to read and navigate.

## Localization and bidirectional layout

When multiple locales are in scope, specify:

- approved language and terminology owner;
- content expansion and truncation behavior;
- locale-aware dates, time, currency, units, names, and numbers;
- plural and grammatical variation;
- left-to-right and right-to-left layout using logical properties;
- navigation and directional icon mirroring, including exceptions;
- mixed-direction content such as phone numbers, identifiers, and map labels;
- font fallback and script shaping;
- screen-reader language changes.

Do not treat RTL as a final visual flip. Reading order, focus order, gestures,
charts, maps, and directional meaning need separate decisions.

## Verification matrix

The brief should name the checks that implementation must pass:

| Check | Method | Evidence |
| --- | --- | --- |
| Semantic structure | Code inspection and accessibility tree | Recorded result |
| Keyboard and focus | Manual traversal of key flows | Steps and result |
| Screen reader | At least one supported browser and reader pair | Script and result |
| Zoom and reflow | Required zoom, text scale, and narrow width | Screens or notes |
| Contrast | Helper plus rendered-state inspection | Pair list and ratios |
| Touch and alternate input | Real or representative device | Steps and result |
| Reduced motion | Platform preference enabled | Result |
| Localization and RTL | Representative long locale and RTL locale | Screens and issues |
| Automated scan | Project-approved scanner | Report with manual follow-up |

Mark each item required, passed, failed, blocked, or not applicable. A design
brief normally leaves implementation checks required, not passed.
