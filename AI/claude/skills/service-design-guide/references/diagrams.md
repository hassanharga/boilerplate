# Diagrams

Last verified: 2026-08-23. The internal renderer hosts below change without notice; if a URL
returns an error, re-derive it from a diagram already embedded in a live guide rather than
assuming the diagram source is wrong.

Read this reference only when diagrams are part of the requested change. Preserve existing layouts
and sources where they remain accurate.

Design Guides use two established diagram families:

| Kind | Source | Typical renderer | Guide sections |
| --- | --- | --- | --- |
| C4 container and component | Structurizr workspace/DSL | `structurizr.yplatform.dev` | 1.1 and 1.2 |
| Class, state, and sequence | PlantUML | `plant-uml.yplatform.dev` | domain model/events and flows |

These are internal services, but sending encoded source to a renderer still discloses the diagram to
that service. Confirm the material is appropriate for the renderer. Do not send secrets, credentials,
personal data, or restricted details. Rendering or uploading an artifact outside the local workspace
requires the user's authorization when it is not already implied by an approved Notion update.

## PlantUML

The established URL shape is:

```text
https://plant-uml.yplatform.dev/svg/<encoded-source>
```

Use the skill's bundled `scripts/plantuml_url.py` to encode source or recover source from an
existing URL. `<skill-dir>` is the directory containing the skill's `SKILL.md`, not the
repository you are working in — resolve it once and use the absolute path:

```bash
python3 <skill-dir>/scripts/plantuml_url.py encode domain-model.puml
python3 <skill-dir>/scripts/plantuml_url.py decode 'https://plant-uml.yplatform.dev/svg/<encoded-source>'
```

SVG is the established default; PNG and text output are available when needed. When updating a
diagram, decode the existing URL, compare its source with current evidence, and make the smallest
change that restores accuracy. This preserves intentional layout decisions.

Keep the `.puml` source with the rendered artifact only when the user has authorized that storage
location. Never add diagram source to a repository or attach it to Notion merely because the renderer
can decode it.

### Verification

HTTP 200 alone is insufficient because PlantUML may return an error image. Verify:

1. the source encodes and decodes successfully;
2. the renderer responds when external rendering is authorized;
3. the response does not contain a syntax/error banner;
4. the rendered labels, relationships, boundaries, and direction match the intended model;
5. an important or dense diagram receives visual inspection.

If rendering is unavailable, deliver verified source and state that visual/render verification was
not performed.

### Domain model conventions

Follow the live guide's visual style. Dispatch currently demonstrates this pattern:

```plantuml
top to bottom direction

<style>
  class {
    MaximumWidth 350
  }
</style>

skinparam shadowing<<Aggregate Root>> true
skinparam class {
  BackgroundColor<<Aggregate Root>> #Lavender
  BackgroundColor<<Domain Event>>   #cfe8e5
  BackgroundColor<<Value Object>>   #eeeeee
  BackgroundColor<<enum>>           #yellow
  BackgroundColor<<interface>>      #lightblue
  StereotypeFontColor Brown
}

package "<Service> Bounded Context" {
  class <AggregateRoot> <<Aggregate Root>> {
  }
}
```

- Show the bounded-context boundary.
- Use stereotypes and established colors where they clarify aggregate roots, entities, value
  objects, domain events, enums, and interfaces.
- Use the names and relationships found in current code and domain guidance.
- Split a dense diagram into readable views rather than shrinking everything into one image.
- Keep source comments that help the next editor navigate the model.

Do not add a stereotype merely to color an element when its domain role is unverified.

### Sequence diagrams

Use sequence diagrams when ordering, boundaries, retries, or asynchronous handoffs are materially
easier to understand visually. Tie every participant and message to current or explicitly planned
evidence. A diagram should complement the row's short flow description, not replace the contract.

## Structurizr and C4

The live guides use stable rendered URLs similar to:

```text
https://structurizr.yplatform.dev/share/1/<workspace-id>/images/<service>-container.png
https://structurizr.yplatform.dev/share/1/<workspace-id>/images/<service>-component.png
```

The URL points to an artifact in a workspace; it does not encode the model. Never fabricate a
workspace or image URL.

Use this order:

1. For an existing service, preserve its URL. If the architecture changed, prepare the smallest DSL
   change and use the authorized Structurizr workflow; the rendered URL can remain stable.
2. For a new service, produce evidence-backed DSL and identify the authorized workspace publication
   step. Until that happens, leave an honest TODO rather than a broken image.
3. When the workspace cannot be accessed, provide source/diff and state that publication and visual
   verification remain pending.

### Modeling rules

- A container is an application or data store, not a deployment pod, library, or source folder.
- A component is a meaningful responsibility or implementation grouping with a clear interface; do
  not mirror top-level directories mechanically.
- Label relationships with the real interaction and transport when known: HTTP operation, gRPC
  service, database access, topic, queue, or event name.
- Treat a relationship as evidence of interaction, not automatically as an integration event.
- Distinguish current relationships from planned ones. Prefer an explicit `[Planned]` label or the
  workspace's established planned-relationship tag/style; otherwise state the status immediately
  beside the diagram. Never rely on color alone.
- Include only diagram levels that help the audience. Context and container views are often enough;
  add a component view when it explains important internal responsibilities.

Minimal DSL sketch:

```text
workspace {
  model {
    actor = person "<Actor>"
    system = softwareSystem "Mobility" {
      service = container "<Service>" "<responsibility>" "<technology>"
      other = container "<Other Service>"
    }
    actor -> service "<interaction>"
    service -> other "<verified protocol, topic, or operation>"
  }
  views {
    container system "<service>-container" { include * autolayout }
    component service "<service>-component" { include * autolayout }
  }
}
```

Derive the model from repositories, deployed configuration, schemas, and the reconciled Scope Guide.
Do not draw the architecture the service ought to have and present it as current.
