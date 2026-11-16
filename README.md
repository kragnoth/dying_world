# Dying World

Worldgen datapack for the Gearwright's Hollow modpack (NeoForge 1.21.1, namespace `dying_world`). It disables the natural
structures and replaces them with a curated set of decayed, tar-and-spirits-themed ones: survivor and abandoned villages,
landmarks, research gates and stations, the Nether foundry, the proving grounds, the sculk dig camp, and the lore trail
that ties them together.

The whole pack ships as **one folder**: the contents of `kubejs/data/` in the instance.

## Get the build

```fish
git pull
python3 tools/build.py          # validates, then writes dist/kubejs_data.zip (+ the split zips)
```

Install: replace the instance's `kubejs/data/` with the `data/` folder from `dist/kubejs_data.zip`
(or unzip over the top when a pass says it only adds/changes files), then `/reload` or restart.
New structures and placement changes only show in newly generated chunks.

## Layout

| Path | What it is |
| --- | --- |
| `PROGRESS.md` | The pass log and source of truth: every decision, the regen order, what's unverified in game |
| `datapack/data/` | Our generated datapack (`dying_world`, `gearwrights` overrides, `minecraft`/`neoforge` overrides) |
| `user_overrides/data/` | Hand edits that always win: copied over `datapack/` by `build.py` before validation |
| `datapack_imported/data/` | Structure files imported from the original kubejs data that are still referenced |
| `kubejs_base/data/` | The pack's non-structure kubejs data (recipes, tags, mobrules, loot, lithostitched modifiers...) |
| `tools/` | Generators (`gen_pass*.py`), `build.py`, `validate.py`, audits, NBT helpers (`nbtw.py`, `nbtrw.py`) |
| `docs/` | Audits, inventories, design notes, walkthrough |
| `reference/` | Small indexes (blocks, block-state props, NBT index) |
| `reference_custom/` | The user's own source NBTs (Create mills) |

Not in git: `dist/` (build output) and the large reference extractions (`reference/*.zip`: vanilla + mod data pulled
from the jars by `tools/make_reference.py`). The generators that read those zips need them locally; `build.py` does not.

## Rules

- Hand-edited files go in `user_overrides/data/` (same path as in `datapack/data/`); never edit only the generated copy.
- Regenerating: run the generators in the REGEN ORDER written at the end of `PROGRESS.md`, then `tools/build.py`.
- When a structure is renamed or removed, grep `config/ftbquests` in the modpack for its id/tag.
