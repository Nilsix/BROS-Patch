"""
Dependency-free auto-updater for the Bleach Rebirth of Souls Community Patch.

Uses ONLY the Python standard library - no git, no pip, nothing for the user
to install. It keeps a local copy of the patch in sync with the GitHub repo:

    * first run / no local copy  -> download the whole repo once (zipball)
    * every run after that       -> fetch only the files that changed
                                    (GitHub "compare" API + raw file download)

This module is shared by:
    * bootstrap.py        (the bundled launcher, runs it on every start)
    * the in-app launcher (Launch / Refresh buttons)

All network endpoints can be overridden with environment variables, which is
how the test-suite points it at a local mock server.
"""

import json
import os
import shutil
import ssl
import tempfile
import urllib.parse
import urllib.request

# --- repository coordinates (override via env for testing) ------------------
OWNER  = os.environ.get("BCP_OWNER",  "Nilsix")
REPO   = os.environ.get("BCP_REPO",   "Bleach-Rebirth-of-Souls-Community-Patch")
BRANCH = os.environ.get("BCP_BRANCH", "main")

API_BASE      = os.environ.get("BCP_API_BASE",      "https://api.github.com")
RAW_BASE      = os.environ.get("BCP_RAW_BASE",      "https://raw.githubusercontent.com")
CODELOAD_BASE = os.environ.get("BCP_CODELOAD_BASE", "https://codeload.github.com")

# --- constants --------------------------------------------------------------
MAIN_FILE       = "Bleach Rebirth of Souls Community Patch.py"
VERSION_FILE    = ".bcp_version"          # stores the commit sha we are synced to
MAX_DELTA_FILES = 300                     # GitHub caps the compare file list ~300
# user-owned files we must never overwrite or delete during an update
PRESERVE = {os.path.normpath("Json/config.json")}

_UA = {"User-Agent": "BleachCommunityPatchLauncher"}


# --- low level HTTP helpers -------------------------------------------------
def _ctx():
    return ssl.create_default_context()


def _open(url, headers=None, timeout=60):
    h = dict(_UA)
    if headers:
        h.update(headers)
    return urllib.request.urlopen(
        urllib.request.Request(url, headers=h), timeout=timeout, context=_ctx()
    )


def _get_bytes(url, headers=None, timeout=60):
    with _open(url, headers, timeout) as r:
        return r.read()


def _get_json(url, timeout=60):
    raw = _get_bytes(url, {"Accept": "application/vnd.github+json"}, timeout)
    return json.loads(raw.decode("utf-8"))


def _download_to(url, dst, progress=None, label="Downloading"):
    """Stream a URL to a file, reporting MB / percentage as it goes."""
    with _open(url, {"Accept": "application/octet-stream"}, timeout=300) as r:
        total = int(r.headers.get("Content-Length") or 0)
        done = 0
        with open(dst, "wb") as f:
            while True:
                chunk = r.read(262144)        # 256 KiB
                if not chunk:
                    break
                f.write(chunk)
                done += len(chunk)
                if progress:
                    if total:
                        progress(f"{label}... {done * 100 // total}%  "
                                 f"({done // 1048576}/{total // 1048576} MB)")
                    else:
                        progress(f"{label}... {done // 1048576} MB")


# --- version bookkeeping ----------------------------------------------------
def read_local_sha(base):
    try:
        with open(os.path.join(base, VERSION_FILE), "r", encoding="utf-8") as f:
            return (f.read().strip() or None)
    except OSError:
        return None


def write_local_sha(base, sha):
    with open(os.path.join(base, VERSION_FILE), "w", encoding="utf-8") as f:
        f.write((sha or "").strip())


def get_remote_sha():
    """Latest commit sha of the tracked branch (one tiny request)."""
    url = f"{API_BASE}/repos/{OWNER}/{REPO}/commits/{BRANCH}"
    return _get_bytes(url, {"Accept": "application/vnd.github.sha"}).decode("utf-8").strip()


# --- path safety ------------------------------------------------------------
def _safe_dst(base, rel_path):
    """Resolve base/rel_path and refuse anything escaping base (zip-slip)."""
    base_real = os.path.realpath(base)
    dst = os.path.realpath(os.path.join(base, *rel_path.split("/")))
    if os.path.commonpath([base_real, dst]) != base_real:
        raise ValueError(f"unsafe path rejected: {rel_path!r}")
    return dst


def _delete(base, rel_path):
    try:
        os.remove(_safe_dst(base, rel_path))
    except (OSError, ValueError):
        pass


def _download_file(base, rel_path, sha):
    quoted = urllib.parse.quote(rel_path, safe="/")
    data = _get_bytes(f"{RAW_BASE}/{OWNER}/{REPO}/{sha}/{quoted}", timeout=300)
    dst = _safe_dst(base, rel_path)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as f:
        f.write(data)


# --- full download (first install / fallback) -------------------------------
def full_download(base, branch=None, progress=None):
    """Download the entire repo zipball and lay it down at `base`, keeping the
    user's Json/config.json intact."""
    branch = branch or BRANCH
    os.makedirs(base, exist_ok=True)

    # preserve user config across a full (re)install
    saved_cfg = None
    cfg = os.path.join(base, "Json", "config.json")
    if os.path.isfile(cfg):
        with open(cfg, "rb") as f:
            saved_cfg = f.read()

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, "patch.zip")
        _download_to(f"{CODELOAD_BASE}/{OWNER}/{REPO}/zip/refs/heads/{branch}",
                     zip_path, progress, "Downloading the full patch (first time)")
        if progress:
            progress("Extracting...")
        import zipfile
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(tmp)
        # the archive contains a single top folder: <repo>-<branch>/
        roots = [d for d in os.listdir(tmp)
                 if os.path.isdir(os.path.join(tmp, d)) and d != "patch.zip"]
        if not roots:
            raise RuntimeError("downloaded archive looked empty")
        src = os.path.join(tmp, roots[0])
        if progress:
            progress("Installing files...")
        shutil.copytree(src, base, dirs_exist_ok=True)

    if saved_cfg is not None:
        os.makedirs(os.path.dirname(cfg), exist_ok=True)
        with open(cfg, "wb") as f:
            f.write(saved_cfg)


# --- the one call everything else uses --------------------------------------
def update(base, progress=None):
    """Bring `base` in sync with the remote branch.

    Returns one of: 'up_to_date', 'installed', 'updated'.
    Raises on network errors when there is no usable local copy; callers that
    already have a copy should treat exceptions as 'stay offline, launch as-is'.
    """
    remote = get_remote_sha()
    local = read_local_sha(base)
    have_main = os.path.isfile(os.path.join(base, MAIN_FILE))

    if local and local == remote and have_main:
        if progress:
            progress("Already up to date.")
        return "up_to_date"

    # no local copy (or it's incomplete / sha unknown) -> full download
    if not local or not have_main:
        full_download(base, progress=progress)
        write_local_sha(base, remote)
        return "installed"

    # delta update via the compare API
    cmp = _get_json(f"{API_BASE}/repos/{OWNER}/{REPO}/compare/{local}...{remote}")
    files = cmp.get("files", []) or []
    # if histories diverged or there are too many files for the compare API to
    # list reliably, just re-download everything.
    if cmp.get("status") == "diverged" or len(files) >= MAX_DELTA_FILES:
        full_download(base, progress=progress)
        write_local_sha(base, remote)
        return "installed"

    n = len(files)
    for i, f in enumerate(files, 1):
        path = f["filename"]
        status = f["status"]
        if progress:
            progress(f"Updating files... {i}/{n}")
        if os.path.normpath(path) in PRESERVE:
            continue
        if status == "removed":
            _delete(base, path)
        elif status == "renamed":
            prev = f.get("previous_filename")
            if prev and os.path.normpath(prev) not in PRESERVE:
                _delete(base, prev)
            _download_file(base, path, remote)
        else:  # added / modified / changed
            _download_file(base, path, remote)

    write_local_sha(base, remote)
    return "updated"
