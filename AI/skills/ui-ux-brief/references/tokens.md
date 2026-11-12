# Token decisions

Use this reference only when tokens are in scope. For an existing product, begin
with the approved semantic tokens and component behavior. Do not generate a new
palette or scale to make the brief look complete.

## Adoption first

Record:

- source file or design-system location;
- semantic token names and their consumers;
- light, dark, high-contrast, and platform variants in scope;
- values that are approved, observed, deprecated, or proposed;
- any divergence required by accessibility, brand, or product behavior.

Prefer an alias or semantic token over a copied raw value. Do not change generated
outputs when a source token file exists.

## Color

Design color by role:

- surfaces and borders;
- primary and secondary text;
- action and focus;
- success, warning, danger, and information;
- selection, disabled, hover, pressed, and visited states;
- chart or map data where relevant.

The user environment may constrain the system. Outdoor use favors stronger
contrast. Dense monitoring surfaces reserve color for meaning. Dark-first
products need a separately designed dark palette, not a mechanical inversion.
Safety and financial actions must not rely on color alone.

Every proposed color entry needs a semantic name, opaque sRGB value, intended use,
status, and verified rendered pair where contrast matters. Use the bundled helper
for WCAG 2.x ratios. If an interface color has alpha, composite it against the
actual surface before checking.

Do not create ramps the product will not use. Raw ramps are implementation
material; semantic roles are the contract.

## Typography

For an established product, preserve the approved family unless there is evidence
of a problem such as missing script coverage, unreadable dense text, licensing
risk, or platform mismatch.

When proposing a typeface, verify:

- required scripts and language shaping;
- legibility at the sizes actually used;
- number behavior for tables and metrics;
- available weights and variable-font support;
- delivery, privacy, performance, and license constraints;
- compatibility with platform text scaling.

Define each needed text style by purpose, size, line height, weight, and tracking.
Do not generate unused display levels. Test long translations, user text scaling,
and narrow layouts rather than treating the scale as fixed artwork.

## Spacing and layout

Adopt the existing scale where possible. Define semantic use for:

- space inside a component;
- space between related controls;
- space between sections;
- content width and page gutters;
- dense and comfortable variants, if the product supports both.

Responsive behavior should follow content pressure and task priority. Breakpoints
document where the layout changes; device names alone do not explain the change.

## Shape and elevation

Radius, borders, shadows, and surface lightness should express one coherent layer
model. Record which mechanism distinguishes:

- resting containers;
- raised menus or popovers;
- dialogs;
- dragged or selected elements.

Avoid combining heavy borders, large shadows, and surface changes without a
specific reason. Keep inherited values unless inconsistency is causing a known
problem.

## Motion

Specify motion by purpose:

- feedback after direct input;
- entry and exit of temporary surfaces;
- spatial continuity;
- progress or background activity.

State duration range, easing, interruption behavior, and the reduced-motion
alternative. Do not animate layout properties when transform or opacity can
communicate the same change. Avoid motion that blocks the next action.

## Icons and imagery

Name the approved icon or illustration source. Define filled or outlined style,
stroke weight, sizing, mirroring behavior, and accessible naming. Avoid emoji as
production icons unless the product explicitly uses them.

For user or stock imagery, cover aspect ratio, cropping, fallback, loading, and
content safety. Do not invent licensing permission.

## Output

For inherited systems, a short adoption table is enough:

| Area | Source | Decision | Status | Exception |
| --- | --- | --- | --- | --- |

For proposed tokens, include implementation-ready output in the format the
project already uses, such as CSS custom properties or the detected framework
theme format. Do not emit both unless both are maintained sources.
