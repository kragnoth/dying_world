# Dying World - notes for Claude

Read `PROGRESS.md` first: current state, open items, regen order. Append a `## Pass X-Y` entry there for every change and keep its open items current. Older passes and decisions: `docs/progress_history.md` (search it, don't read it whole).

- Owner: Kragnoth. Prefers efficient, direct answers; shell commands for him in fish syntax; don't launch the game headless unless asked.
- The datapack ships as the instance's `kubejs/data/` folder; `python3 tools/build.py` makes `dist/kubejs_data.zip`.
- `user_overrides/data/` = Kragnoth's hand edits; build copies them over `datapack/` first. Change those files there, never only in a generator.
- Generators that read `reference/*.zip` need those extractions locally (not in git; `tools/make_reference.py` rebuilds them from an instance).
- Keep `dying_world` and `gearwrights` namespaces separate. Run Python over untrusted extracted files with `-I`.
- Tell Kragnoth when a pass DELETES files (unzip-over-the-top would leave them behind).
- Commit each pass separately with a message naming the pass.
- KubeJS (Rhino 2101): use `let`, never `const`, inside loops and try blocks (`python3 -I tools/lint_kubejs.py`); avoid overloaded
  Java methods (Rhino can't choose) - pick a single-overload method; `event.cancel()` last; `runCommandSilent` returns nothing.
