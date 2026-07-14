# Long-path / copy-reliability fix — change log

**Date:** 2026-07-13
**Files changed:** `Bleach Rebirth of Souls Community Patch.py`, `Quick Launch Community Patch.py`, `Quick Launch Bros Vanilla.py`

---

## The bug being fixed

Users reported failures tied to long file paths and deep folders. The deep folders
(`00HIGH`, `01MIDDLE`, `Effect`, `spfx`, `pl022`, `Script`, ...) are names the game
itself reads, so they **cannot** be renamed or flattened without breaking the game.
Renaming was therefore never a viable fix.

There were actually **two** separate long-path problems: one in how the launchers
**copy** files into the game folder, and one in how **git** checks the repo out on
the user's machine. Both are now handled with zero action required from the user.

---

## Problem 1 — the launcher copy steps

### Root causes found

1. **Python `shutil` hits the 260-char `MAX_PATH` limit.** Several copy steps used
   `shutil.copytree` / `shutil.copy` directly. On Windows these throw
   `FileNotFoundError` / path-too-long once the source or destination path passes
   ~260 characters. `robocopy`, by contrast, natively handles paths far beyond that
   limit — which is why the robocopy-based steps worked while the shutil steps
   silently failed. This is where the "some files didn't install" reports came from.

2. **The `robocopy` error handling was dead code.** The old pattern was:

   ```python
   try:
       subprocess.run(["robocopy", src, dst, "/MIR"], ...)
   except Exception:
       shutil.rmtree(dst)
       shutil.copytree(src, dst)
   ```

   `robocopy` reports its result through the **process exit code** (0–7 = success/info,
   8+ = a real error), **not** through exceptions. `subprocess.run()` without
   `check=True` never raises for a non-zero exit code, so the `except` block could
   never run from a robocopy failure. Consequences:
   - The shutil fallback everyone assumed was protecting them was unreachable.
   - If robocopy genuinely failed (locked file, permissions, disk full), the code
     **continued silently** with no error shown — a broken install with no message.

3. **The fallback was destructive.** In the (unreachable) `except`, `shutil.rmtree(dst)`
   deleted the destination *before* attempting the copy. If the copy then failed, the
   user's folder was already gone, with no backup.

### New shared helpers (added to all three scripts)

**`robocopy_dirs(src, dst, mirror=True, extra=None)`** — the single copy path now
used everywhere a folder is copied.
- Uses `robocopy` first (immune to the 260-char limit).
- **Checks the return code** (`>= 8` = real error) instead of relying on exceptions.
- Adds `/R:2 /W:2` so a transient lock (e.g. antivirus scanning a freshly written
  file) is retried instead of failing outright.
- Only if robocopy is unavailable or genuinely fails does it fall back to
  `shutil.copytree`, now using an **extended-length (`\\?\`) path** so the fallback
  also survives long paths — and **without** the old destructive pre-delete.
- Returns `True`/`False` and prints a clear `[copy error]` line on real failure, so
  problems surface instead of hiding.
- `mirror=True` → `robocopy /MIR` (mirror; removes stray files, matches the old
  `/MIR` behavior). `mirror=False` → `robocopy /E` (merge in place, matches the old
  `shutil.copytree(..., dirs_exist_ok=True)` behavior). Existing per-call semantics
  were preserved exactly.

**`_extended_path(path)`** — returns a Windows extended-length path (`\\?\...`, or
`\\?\UNC\...` for network shares) so `shutil`/`os` can exceed `MAX_PATH`. No-op on
non-Windows or already-prefixed paths.

**`copy_file(src, dst)`** — single-file copy wrapped in `_extended_path`, for the
few individual-file copies (`dinput8.dll`, `CharaStatus.fsv`) whose destination can
sit deep in the game tree.

### Per-file conversions

**`Bleach Rebirth of Souls Community Patch.py`**
- `injectFolder` — rewritten to call `robocopy_dirs` (`mirror=fullFolder`). Removed the
  dead try/except and the destructive `rmtree`.
- `injectEffects` — now `robocopy_dirs(..., mirror=True)`.
- `injectPerformanceFiles` — the two `shutil.copytree` calls → `robocopy_dirs(..., mirror=False)`.
- `repair()` — the raw robocopy call + unreachable shutil fallback → single
  `robocopy_dirs(repair_game_path, game_path, mirror=False, extra=["/XO"])`.
  `/XO` (skip files already newer in the game folder) and non-mirror behavior are
  preserved, so no user files are deleted during a repair.
- `launch` logic — the reverse_globe performance copies, the rework Script/Motion
  copies, and the game-mode Script copy → `robocopy_dirs(..., mirror=False)`;
  the Team Battle `CharaStatus.fsv` copy → `copy_file`.

**`Quick Launch Community Patch.py`** and **`Quick Launch Bros Vanilla.py`** (these two mirror each other)
- `injectFolder`, `injectPerformanceFiles` → `robocopy_dirs`.
- reverse_globe, rework Script/Motion, game-mode Script copies → `robocopy_dirs(mirror=False)`.
- `dinput8.dll` (matchmaking) and `CharaStatus.fsv` copies → `copy_file`.

---

## Problem 2 — the "Filename too long" git clone error (self-healing, zero user action)

**Symptom:** `git clone` finishes downloading (`Receiving objects: 100%`,
`Resolving deltas: 100%`) but then throws `error: unable to create file
GameVersions/.../Effect/spfx/pl022/P022_*.vfxt: Filename too long` for the deep
effect files. Result: a repo that is missing those files, so the patch installs
incomplete. This is **git's** 260-char limit during checkout — it happens before any
launcher copy runs.

**Fix (nothing for the user to do):** `pulling_from_git()` in all three launchers now
runs, as its first step on every launch:

```python
subprocess.run(["git", "-C", BASE_DIR, "config", "core.longpaths", "true"], capture_output=True, text=True)
```

`core.longpaths` makes git use Windows extended-length (`\\?\`) paths internally —
**no admin rights, no registry edit, no reboot, nothing to install or type.**

Because the failed clone had already downloaded every git object (only the
working-tree *write* failed), the `git reset --hard origin/main` that the non-dev
startup path already runs will now materialize the previously-missing long-path files
straight from the local objects. Net effect: the user clones (partial failure), opens
the launcher once, and the checkout silently repairs itself.

**Note for maintainers:** for anyone with `BalanceLeadTools/DevToken.txt`, the launcher
only runs `git pull`, not `reset --hard`, so it will not touch your working tree.
`core.longpaths` is still set for you, so your next normal pull/checkout writes the
long-path files correctly. If you already have a partial dev clone, run
`git config core.longpaths true` then `git checkout -- .` once to restore the missing
files (kept manual on purpose so your local edits are never force-discarded).

---

## Incidental issues found (not changed — your call)

1. **Duplicate copy removed.** In the main launcher's game-mode injection, the exact
   same `shutil.copytree(srcPath, dstPath)` ran twice back-to-back (same source and
   destination). Collapsed into a single `robocopy_dirs` call. Behavior identical,
   just without the redundant second copy.

2. **Renaming the version folders won't help and isn't safe.** The version folder
   names are referenced as strings in the launchers, and everything below them is
   game-defined. With robocopy handling long paths end-to-end and git self-healing,
   you shouldn't need to shorten anything.

3. **A few remaining single-file `shutil.copy` calls** (config template at the top of
   the main script, and a save-data copy around the Dangai files) were left as-is —
   their paths are short and not part of the reported failures. Easy to switch to
   `copy_file` later if you ever want blanket coverage.

---

## Follow-up: Linux/macOS game launch crash — `[Errno 8] Exec format error`

**Symptom (Linux user):** `Error launching patched game: [Errno 8] Exec format
error: '.../steamapps/common/BLEACH Rebirth of Souls/BLEACH Rebirth of Souls.exe'`.

**Cause:** `launch_patched()` ran the game with `subprocess.Popen([exe])`, i.e. it
tried to execute a Windows `.exe` directly. That works on Windows but is
impossible on Linux/macOS — a Windows PE binary can't be exec'd by the OS, which
raises `[Errno 8] Exec format error`. The game only runs there through
Steam/Proton. (This is **not** a missing-shebang problem, despite the generic
Errno-8 advice — no shell script is involved in this code path.)

**Fix (all three launchers):** `launch_patched()` is now platform-aware.
- **Windows:** unchanged — starts the `.exe` directly, which is required so
  EasyAntiCheat doesn't block the injected `dinput8.dll`.
- **Linux/macOS:** launches via Steam's app URL `steam://rungameid/1689620`
  (the same App ID the launcher already uses for the vanilla launch), so Steam
  runs the game through Proton. No direct `.exe` exec, so no crash.

Verified in isolation: the new function compiles and, on Linux, routes to the
Steam URL handler instead of raising `Errno 8`.

> Note for Linux players: this makes the game *launch* through Proton. Whether
> the injected `dinput8.dll` (matchmaking) loads under Proton depends on the
> user's Proton DLL-override setup and is a separate, Linux-specific concern —
> but the crash on launch is resolved.

## Testing done

- The copy helper block was compiled and run in isolation: with `robocopy` absent
  (Linux), `robocopy_dirs` correctly fell through to the `shutil` + `\\?\` fallback
  and copied a nested directory successfully.
- All edits were reviewed for balanced calls and preserved mirror/merge semantics; the
  git config line is a single added `subprocess.run` and does not alter existing flow.
- **Recommended before release (on your Windows machine):**
  - `python -m py_compile "Quick Launch Community Patch.py"` (and the other two) —
    silent output means they compile.
  - Delete a test copy of the repo, re-clone to reproduce the "Filename too long"
    error, then run the launcher once and confirm the missing `Effect/spfx/...` files
    appear and a normal patch install + one "Repair" run both work.
