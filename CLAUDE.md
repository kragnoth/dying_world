# Dying World - notes for Claude

Read `PROGRESS.md` first: it is the pass log, the decision record and the regen order. Append a `## Pass X-Y` entry for every change.

- Owner: Kragnoth. Prefers efficient, direct answers; shell commands for him in fish syntax; don't launch the game headless unless asked.
- The datapack ships as the instance's `kubejs/data/` folder; `python3 tools/build.py` makes `dist/kubejs_data.zip`.
- `user_overrides/data/` = Kragnoth's hand edits; build copies them over `datapack/` first. Change those files there, never only in a generator.
- Generators that read `reference/*.zip` need those extractions locally (not in git; `tools/make_reference.py` rebuilds them from an instance).
- Keep `dying_world` and `gearwrights` namespaces separate. Run Python over untrusted extracted files with `-I`.
- Tell Kragnoth when a pass DELETES files (unzip-over-the-top would leave them behind).
- Commit each pass separately with a message naming the pass.
