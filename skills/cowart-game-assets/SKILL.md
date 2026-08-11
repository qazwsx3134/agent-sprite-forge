---
name: cowart-game-assets
description: Route Cowart canvas requests for production-ready 2D game maps, sprite sheets, animated units, props, tiles, and FX through Agent Sprite Forge generation, deterministic post-processing, QC, and engine-export workflows, then place selected previews or final bitmap artifacts back onto Cowart. Use when a Cowart AI image holder or Cowart canvas prompt asks for a game asset rather than a standalone illustration.
---

# Cowart Game Assets

Use Cowart as the visual brief and delivery surface. Keep Agent Sprite Forge as the production pipeline and the user's project as the source of truth for the complete output bundle.

## Required capabilities

Require the Cowart MCP tools `get_cowart_selection` and `insert_cowart_image`. Use `render_cowart_canvas_widget` when the user asks to open Cowart or when no saved canvas exists. Pass the active user workspace as `projectDir`, never the Cowart plugin directory.

If Cowart tools are unavailable, explain that Cowart must be installed or upgraded and that a new Codex conversation may be required. Still offer to generate the project-local asset bundle without canvas insertion.

## Route the request

- Apply the sibling `generate2dmap` skill for maps, levels, arenas, battle backgrounds, parallax scenes, tilesets, collision, zones, or engine-native map data. Its plugin-qualified name is `$agent-sprite-forge:generate2dmap`; its standalone name is `$generate2dmap`.
- Apply the sibling `generate2dsprite` skill for characters, enemies, animated props, sprite sheets, attacks, projectiles, impacts, FX, or transparent prop assets. Its plugin-qualified name is `$agent-sprite-forge:generate2dsprite`; its standalone name is `$generate2dsprite`.
- Apply both workflows when a map bundle also needs reusable transparent environmental props. Keep actor art in the sprite workflow.
- Do not route Cowart requests through `video2dsprite` in Codex. That workflow requires Grok Build's `image_to_video`; use `generate2dsprite` for a crisp image-generation-first sheet instead.

The specialized map or sprite skill owns all production rules. This skill only adds Cowart selection, sizing, placement, and canvas verification.

## Workflow

### 1. Read the Cowart target

Call `get_cowart_selection` with `projectDir`. When exactly one selected shape is an AI image holder, record:

- `holderShapeId`
- `pageId`
- `targetWidth` from `props.w`
- `targetHeight` from `props.h`
- `targetAspectRatio = targetWidth / targetHeight`

Recognize both `isAiImageHolder: true` and `meta.cowartAiImageHolder: true`. If no holder is selected, continue without asking for one and use standalone insertion on the current page.

### 2. Plan a production bundle

Create the complete bundle in the user's project, outside `canvas/pages/.../assets/`, under a stable path such as:

```text
artifacts/agent-sprite-forge/<asset-slug>/
```

The Cowart MCP copies chosen bitmap artifacts into page-local storage. Do not use the Cowart page asset copy as the only copy of runtime sheets, frames, manifests, collision, or engine files.

Use holder dimensions as a composition hint, not permission to weaken the selected production contract:

- For a baked map or map preview, match the holder ratio when it does not conflict with the game camera or engine target.
- For a layered or playable map, keep the foundation, objects, collision, zones, and engine data separate even if Cowart only displays a flattened QA preview.
- For a sprite sheet, the requested rows, columns, square-cell geometry, stable anchors, and transparent export take priority over the holder ratio. Never stretch or crop a runtime sheet to fill an incompatible holder.

### 3. Generate, process, and validate

Follow the routed skill completely:

- Generate visual art with the host's built-in image generation.
- Save prompt provenance beside generated art.
- Run the deterministic local processors.
- Inspect the processed bitmap visually.
- Pass the relevant strict QC and parse generated manifests before Cowart insertion.

Do not insert the raw generation into Cowart as the final result when the workflow requires chroma cleanup, extraction, alignment, transparency, layered composition, or other processing.

### 4. Choose canvas artifacts

Insert a small, useful presentation set rather than every file in the bundle.

| Workflow | Primary Cowart artifact | Useful secondary artifacts |
| --- | --- | --- |
| baked map | final map PNG | none unless requested |
| layered or scene map | layered preview PNG | foundation-only base, dressed reference, prop pack |
| side-scroll map | stage preview PNG | representative parallax plate, stage reference, platform library |
| tile/grid map | flattened QA preview PNG | tileset or atlas PNG |
| sprite | transparent runtime sheet PNG | animation contact-sheet PNG, accepted master frame, FX sheet |
| prop/FX bundle | transparent sheet or contact sheet PNG | selected individual transparent PNGs |

Treat map previews as QA artifacts, not runtime map files. Keep collision, scene hooks, placements, frames, JSON, Godot, Unity, Tiled, or LDtk files in the project bundle and report their paths separately.

### 5. Preserve aspect ratio

For a selected holder, replace it only when the primary artifact is intentionally composed for the holder ratio. A difference within two percent is compatible.

If a runtime sprite sheet or other canonical artifact has an incompatible ratio:

1. Keep the canonical bitmap unchanged.
2. Insert it beside the holder with `matchAnchor: false`, explicit proportional `displayWidth` and `displayHeight`, and `replaceAiImageHolder: false`.
3. Leave the holder intact and explain that replacing it would distort the engine artifact. The user may resize the holder and retry.

Do not create a stretched duplicate merely to consume the holder.

### 6. Insert through Cowart MCP

Prefer `insert_cowart_image`; do not hand-write tldraw records or fractional indexes while the tool is available.

Use PNG for reliable canvas handoff. Do not rely on GIF insertion unless the active Cowart tool version explicitly confirms support; keep animation GIFs in the project bundle and insert a PNG contact sheet or representative frame instead.

Before each real insertion, call the same payload with `dryRun: true`. Confirm the target page, anchor, dimensions, placement, and whether the holder would be replaced, then repeat without `dryRun` only when the plan is correct.

Compatible holder replacement:

```json
{
  "imagePath": "/absolute/path/to/primary-preview.png",
  "projectDir": "/absolute/path/to/user-project",
  "anchorShapeId": "<holder-shape-id>",
  "replaceAiImageHolder": true,
  "altText": "Agent Sprite Forge map preview",
  "shapeMeta": {
    "agentSpriteForge": true,
    "agentSpriteForgeWorkflow": "generate2dmap",
    "agentSpriteForgeArtifactRole": "qa-preview",
    "agentSpriteForgeBundlePath": "artifacts/agent-sprite-forge/<asset-slug>"
  }
}
```

Standalone or ratio-safe insertion beside an anchor:

```json
{
  "imagePath": "/absolute/path/to/sheet-transparent.png",
  "projectDir": "/absolute/path/to/user-project",
  "anchorShapeId": "<holder-or-primary-shape-id>",
  "placement": "right",
  "margin": 40,
  "matchAnchor": false,
  "replaceAiImageHolder": false,
  "displayWidth": 512,
  "displayHeight": 341,
  "shapeMeta": {
    "agentSpriteForge": true,
    "agentSpriteForgeWorkflow": "generate2dsprite",
    "agentSpriteForgeArtifactRole": "runtime-sheet"
  }
}
```

Use the returned primary `shapeId` as the anchor for secondary artifacts. Prefer `right` for a short comparison row and `below` for a new artifact group. Keep about 40 canvas units between items.

### 7. Verify the handoff

Confirm all of the following before reporting completion:

- Cowart returned `assetId`, `shapeId`, `pageId`, `assetFile`, `bounds`, and a valid tldraw fractional `index`.
- A compatible AI holder was replaced, or an incompatible holder was intentionally preserved.
- Inserted images are the accepted processed outputs, not stale or raw generations.
- Each insertion passed a Cowart `dryRun` before the canvas was mutated.
- No inserted runtime sheet is stretched or cropped.
- The complete project-local bundle and its machine-readable metadata still exist outside Cowart page assets.
- The canvas shows a useful preview while the reported runtime paths point to the real production artifacts.

## Guardrails

- Do not flatten a playable map into a single runtime image because Cowart displays bitmaps.
- Do not skip sprite cleanup or QC because the raw generation already looks acceptable on the canvas.
- Do not delete, move, or replace unrelated Cowart shapes.
- Do not make Cowart page-local assets the canonical runtime bundle.
- Do not claim engine readiness based only on the Cowart preview.
