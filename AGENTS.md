# Working on 夜潮事务所

Read `docs/NEXT_AGENT_HANDOFF.md` first. It gives the current stage, remaining work, evidence limits, and reproducible commands. Older handoffs and lower README sections are historical.

- The sole design authority is `game/data/final_design/design_manifest.json` and its `release_baseline.json`. Do not rewrite the frozen design to fit implementation.
- Continue the existing Godot project. Current stage: P4 product alignment and acceptance, not a completed final release. Begin with handoff section 5, P4-018-01.
- Acquisition, progression, relationships and gameplay must work together in production state. Tests, asset counts and synthetic fixtures alone do not establish player experience or design alignment.
- Use `tools/check_product018.py` and `tools/build_windows_product018.py`; older similarly named scripts are historical. Fresh clones use the default history check. It reports the explicit retirements in `docs/product018-history-retirements.json`; `--allow-missing-history` can only permit unrecorded excluded old ZIP/AVI files. Never claim absent paths were verified.
- Keep source changes, local checks, exported builds, Windows-native evidence and human acceptance distinct. The user reported verifying the previous Windows package; record further checks by build and do not request a remote Windows connection as a prerequisite.
- Do not expose browser profiles, credentials, local engine/cache files or local build archives in Git. Preserve retained historical evidence and receipts; see `docs/product018-cleanup.md` for the authorized deletions. Do not occupy the user's primary display without an applicable instruction; use the documented hidden rendering route when no external screen is available.
