# Patch-only online + region unlock + patch marker — repo changes

## What the launcher now does
When you pick a **patch** version it: installs the in-game loader `dinput8.dll`,
writes `patch_ranked.txt` (a match code from build + version), and launches the
game **directly** (EAC off — required for the DLL). When you pick **"Bleach
Rebirth of Souls" (vanilla)** it removes `dinput8.dll` and launches via **Steam**
(EAC on). So patch = modded + segregated + region-free online; vanilla = clean
stock game.

## What dinput8.dll does inside the game (all handled by one file)
1. **Patch-only matchmaking** — rewrites the Steam lobby `issuer` key on both the
   search filter and the host tag, so patched players only match players with the
   same match code. This is global: it covers **Ranked, Free Battle, and Room
   Match** (they all go through the same Steam lobby calls). A join-guard also
   refuses to join any lobby whose code doesn't match (backstop vs desync).
2. **Region unlock** — the game never sets a Steam distance filter, so Steam
   defaults to region-limited matching (the reason people swap
   steam_download_region). The loader forces **worldwide** on every search, so
   region no longer matters for Ranked / Free / Room Match.
3. **Patch marker** — renames the title-screen "Ver.<x>" to **"ReBalance <x>"** so
   you can tell at a glance you're on the patch. (The prefix is limited to ~11
   characters of in-place space, so the full "ReBalance Patch 1.1" doesn't fit;
   "ReBalance " is the clean fit. Only shows while the loader is active.)

## Match code = per version + per build
Derived from `git snapshot + version name`, so different patch versions and older
builds are separate pools (prevents cross-version desyncs); vanilla (no loader,
issuer 256) is excluded automatically.

## Deploy
Commit `Files/Matchmaking/dinput8.dll` (+ `dinput8_proxy.c`), the edited launcher,
and `.gitattributes` (has `*.dll binary`). Push to `origin/main`.

## Online works without EAC
Verified in the game binary: no EAC anti-cheat networking; online is pure Steam
P2P (`SteamNetworking` / `SteamMatchMaking009`). EAC here is only the launch
wrapper, so launching directly does not break online. (Steam must be running.)

## Test
Both players launch the SAME patch version from the launcher, confirm
`patch_ranked.log` shows `HOOKS INSTALLED ... region=worldwide` and
`VERSION: title renamed`, then verify: you match each other, you can't match a
vanilla player, cross-region works, and a full match has no desync.

## Matchmaking is locked to the build, automatically
The match code is derived from the current **GitHub commit SHA**
(`get_snapshot()`) + the selected game version, run through crc32. Every push =
new SHA = a fresh pool, with no manual step. Players on a different build, a
different game version, or vanilla will not match you. Because the launcher
`git reset --hard` + `pull`s on every launch, everyone converges to the latest
build (and pool) automatically. (`patch_version.txt` is no longer used for
matchmaking; leave it or delete it.)

## Spectator mode / more players per lobby — not feasible
The game is 1v1 and has **no spectator/observer code** (no such strings exist in
the binary). A DLL can raise the Steam lobby member limit, but the game has no
logic to place a 3rd participant or render a match for observers, so extra
joiners do nothing. Adding this would require game features that don't exist and
can't be created by manipulating Steam lobby data.
