import os
import hashlib
import json
import ctypes
import threading
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from tkinter import Tk, Frame, Label, Button, Canvas, Scrollbar, VERTICAL, RIGHT, Y, BOTH, LEFT, StringVar
from tkinter import ttk

BALANCE_LEAD  = "Nilsix"
GITHUB_REPO   = "Bleach-Rebirth-of-Souls-Community-Patch"
GITHUB_BRANCH = "main"
FILES_TO_SKIP = set()   # Changed from {} to set() — {} is an empty dict, not a set

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = BASE_DIR / "updater.log"

API_BASE = "https://api.github.com"
RAW_BASE = f"https://raw.githubusercontent.com/{BALANCE_LEAD}/{GITHUB_REPO}/{GITHUB_BRANCH}"


def _gh_get(url: str) -> dict | list:
    """Fetch JSON from the GitHub API."""
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "BrosPatch-Updater/1.0",
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


_LFS_HEADER = b"version https://git-lfs.github.com/spec/v1"

def _download_raw(remote_path: str, local_path: Path, progress_cb=None):
    # Encode each path segment individually (preserve the '/' separators)
    encoded_path = "/".join(urllib.parse.quote(part, safe="") for part in remote_path.split("/"))
    url = f"{RAW_BASE}/{encoded_path}"

    req = urllib.request.Request(url, headers={"User-Agent": "BrosPatch-Updater/1.0"})
    local_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        resp_obj = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"HTTP {exc.code} {exc.reason}  →  {url}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}  →  {url}") from exc

    with resp_obj as resp:
        total      = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        chunk      = 65536
        buf        = bytearray()
        lfs_checked = False

        with open(local_path, "wb") as f:
            while True:
                data = resp.read(chunk)
                if not data:
                    break

                # Check the very first chunk for an LFS pointer signature
                if not lfs_checked:
                    lfs_checked = True
                    if data.lstrip().startswith(_LFS_HEADER):
                        # Abandon the write — don't corrupt the local file
                        raise ValueError(
                            f"LFS pointer returned (file is stored in Git LFS, "
                            f"not directly downloadable via raw CDN): {remote_path}"
                        )

                f.write(data)
                downloaded += len(data)
                if progress_cb and total:
                    progress_cb(downloaded / total)


def _get_repo_tree() -> list[dict]:
    url = (
        f"{API_BASE}/repos/{BALANCE_LEAD}/{GITHUB_REPO}"
        f"/git/trees/{GITHUB_BRANCH}?recursive=1"
    )
    data = _gh_get(url)
    if data.get("truncated"):
        raise RuntimeError(
            "Repository tree was truncated by GitHub. Contact the mod author."
        )
    return [item for item in data["tree"] if item["type"] == "blob"]

def _git_blob_sha(local_path: Path) -> str:
    data = local_path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()

def compute_update_plan(log_cb=None) -> dict:
    """
    Compare the remote tree (via a single GitHub API call) against local files
    using Git blob SHA comparison.

    Returns:
      {
        "to_add":    [(remote_path, local_path, remote_sha), ...],  # missing locally
        "to_update": [(remote_path, local_path, remote_sha), ...],  # SHA mismatch
        "skipped":   [remote_path, ...],                            # in FILES_TO_SKIP
        "up_to_date":[remote_path, ...],                            # SHA matches
      }

    API calls made: exactly 1  (the tree endpoint).
    """
    if log_cb:
        log_cb("Fetching remote file list…", 0.0)
    tree = _get_repo_tree()           # ← the only API call we need
    all_paths = [(item["path"], item["sha"]) for item in tree]
    skipped    = []
    to_add     = []
    to_update  = []
    up_to_date = []
    total = len(all_paths)
    for idx, (remote_path, remote_sha) in enumerate(all_paths):

        if log_cb:
            frac = (idx + 1) / total
            log_cb(f"Comparing ({idx + 1}/{total}): {remote_path}", frac)

        if remote_path in FILES_TO_SKIP:
            skipped.append(remote_path)
            continue
        local_path = BASE_DIR / Path(remote_path)

        if not local_path.exists():
            to_add.append((remote_path, local_path, remote_sha))
        else:
            local_sha = _git_blob_sha(local_path)
            if local_sha != remote_sha:
                to_update.append((remote_path, local_path, remote_sha))
            else:
                up_to_date.append(remote_path)

    return {
        "to_add":     to_add,
        "to_update":  to_update,
        "skipped":    skipped,
        "up_to_date": up_to_date,
    }


def apply_update_plan(plan: dict, log_cb=None) -> dict:
    """
    Download all files in to_add and to_update.
    """
    work   = plan["to_add"] + plan["to_update"]
    errors = []
    lfs    = []
    total  = len(work)

    for idx, (remote_path, local_path, _sha) in enumerate(work):
        if log_cb:
            log_cb(f"Downloading ({idx + 1}/{total}): {remote_path}", (idx + 1) / total)
        try:
            _download_raw(remote_path, local_path)
        except ValueError as exc:          # LFS pointer detected
            lfs.append(str(exc))
        except Exception as exc:
            errors.append(f"{remote_path}: {exc}")

    return {"errors": errors, "lfs": lfs}

BGCOLOR    = "#2D0A4E"
LABELCOLOR = "#EDE0FF"
BTNBG      = "#EDE0FF"
BTNFG      = "#2D0A4E"
FONT_TITLE = ("Arial", 22)
FONT_BODY  = ("Courier", 13)
FONT_LOG   = ("Courier", 11)


class UpdaterApp:
    def __init__(self, root: Tk):
        self.root = root
        root.title("reBalance Of Souls Updater")
        root.geometry("820x560")
        root.minsize(520, 380)
        root.config(bg=BGCOLOR)
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except Exception:
            pass

        ico = BASE_DIR / "ressources" / "pimplin.ico"
        if ico.exists():
            root.iconbitmap(str(ico))

        self._plan = None
        self._build_ui()

    def _build_ui(self):
        top = Frame(self.root, bg=BGCOLOR)
        top.pack(fill="x", padx=20, pady=(18, 4))
        Label(top, text="reBalance of Souls Updater",
              font=FONT_TITLE, bg=BGCOLOR, fg=LABELCOLOR).pack(anchor="w")
        Label(top, text="made by Bergen",
              font=FONT_BODY, bg=BGCOLOR, fg=LABELCOLOR).pack(anchor="w")

        self.status_var = StringVar(value="Ready. Press 'Check for Updates' to begin.")
        Label(self.root, textvariable=self.status_var,
              font=FONT_BODY, bg=BGCOLOR, fg=LABELCOLOR,
              wraplength=760, justify="left").pack(anchor="w", padx=20, pady=(8, 4))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Patch.Horizontal.TProgressbar",
                        troughcolor="#1A0030",
                        background="#C084FC",
                        thickness=18)
        self.progress = ttk.Progressbar(
            self.root, style="Patch.Horizontal.TProgressbar",
            orient="horizontal", mode="determinate", length=760
        )
        self.progress.pack(padx=20, pady=(0, 8))

        log_frame = Frame(self.root, bg="#1A0030", relief="sunken", bd=1)
        log_frame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 10))

        scrollbar = Scrollbar(log_frame, orient=VERTICAL, bg=BGCOLOR, troughcolor="#2E0E2A")
        scrollbar.pack(side=RIGHT, fill=Y)

        self.log_canvas = Canvas(log_frame, bg="#1A0030", highlightthickness=0,
                                 yscrollcommand=scrollbar.set)
        self.log_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.log_canvas.yview)

        self.log_inner  = Frame(self.log_canvas, bg="#1A0030")
        self.log_window = self.log_canvas.create_window(
            (0, 0), window=self.log_inner, anchor="nw"
        )

        self.log_inner.bind("<Configure>", self._on_log_resize)
        self.log_canvas.bind("<Configure>", self._on_canvas_resize)

        btn_frame = Frame(self.root, bg=BGCOLOR)
        btn_frame.pack(pady=(0, 16), padx=20, fill="x")

        self.check_btn = Button(
            btn_frame, text="Check for Updates",
            font=FONT_BODY, bg=BTNBG, fg=BTNFG,
            relief="flat", padx=12, pady=6,
            command=self._start_check
        )
        self.check_btn.pack(side=LEFT, padx=(0, 10))
        self._bind_hover(self.check_btn, normal_bg=BTNBG, hover_bg="#000000", normal_fg=BTNFG, hover_fg="#FFFFFF")

        self.apply_btn = Button(
            btn_frame, text="Apply Updates",
            font=FONT_BODY, bg=BTNBG, fg=BTNFG,
            relief="flat", padx=12, pady=6,
            state="disabled",
            command=self._start_apply
        )
        self.apply_btn.pack(side=LEFT, padx=(0, 10))
        self._bind_hover(self.apply_btn, normal_bg=BTNBG, hover_bg="#000000", normal_fg=BTNFG, hover_fg="#FFFFFF")

        self.close_btn = Button(
            btn_frame, text="Close",
            font=FONT_BODY, bg="#6B21A8", fg="#FFFFFF",
            relief="flat", padx=12, pady=6,
            command=self.root.destroy
        )
        self.close_btn.pack(side=RIGHT)
        self._bind_hover(self.close_btn, normal_bg="#6B21A8", hover_bg="#000000", normal_fg="#EDE0FF", hover_fg="#FFFFFF")

    def _bind_hover(self, btn: Button, normal_bg: str, hover_bg: str,
                    normal_fg: str, hover_fg: str):
        def on_enter(e):
            if btn["state"] != "disabled":
                btn.config(bg=hover_bg, fg=hover_fg)
        def on_leave(e):
            if btn["state"] != "disabled":
                btn.config(bg=normal_bg, fg=normal_fg)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _on_log_resize(self, event):
        self.log_canvas.configure(scrollregion=self.log_canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self.log_canvas.itemconfig(self.log_window, width=event.width)

    def _write_log_file(self, text: str):
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(text + "\n")
        except Exception:
            pass

    def _log(self, text: str, color: str = LABELCOLOR):
        label = Label(self.log_inner, text=text, font=FONT_LOG,
                      bg="#2E0E2A", fg=color, anchor="w", justify="left")
        label.pack(fill="x", padx=6, pady=1)
        self.root.update_idletasks()
        self.log_canvas.yview_moveto(1.0)
        self._write_log_file(text)

    def _clear_log(self):
        for widget in self.log_inner.winfo_children():
            widget.destroy()
        # Write a session separator to the file so runs don't blur together
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                from datetime import datetime
                f.write(f"\n{'─' * 70}\n")
                f.write(f"  Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'─' * 70}\n")
        except Exception:
            pass

    def _set_buttons(self, checking=False, applying=False, has_plan=False):
        self.check_btn.config(state="disabled" if (checking or applying) else "normal")
        self.apply_btn.config(
            state="normal" if (has_plan and not applying and not checking) else "disabled"
        )

    def _update_progress(self, value: float):
        self.progress["value"] = value * 100
        self.root.update_idletasks()

    def _update_status(self, msg: str):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def _start_check(self):
        self._clear_log()
        self._plan = None
        self._set_buttons(checking=True)
        self._update_progress(0)
        self._update_status("Connecting to GitHub…")
        threading.Thread(target=self._run_check, daemon=True).start()

    def _run_check(self):
        def log_cb(msg, frac):
            self.root.after(0, self._update_status, msg)
            self.root.after(0, self._update_progress, frac)
            self.root.after(0, self._log, msg)

        try:
            plan = compute_update_plan(log_cb=log_cb)
            self.root.after(0, self._check_done, plan, None)
        except Exception as exc:
            self.root.after(0, self._check_done, None, str(exc))

    def _check_done(self, plan, error):
        self._update_progress(1.0)
        if error:
            self._update_status(f"Error during check: {error}")
            self._log(f"✖ {error}", color="#FF6B6B")
            self._set_buttons()
            return

        self._plan = plan
        n_add    = len(plan["to_add"])
        n_update = len(plan["to_update"])
        n_skip   = len(plan["skipped"])
        n_ok     = len(plan["up_to_date"])

        self._log("─" * 70, color="#9333EA")
        self._log(f"  ✚ New files to install : {n_add}", color="#8FE8A0")
        for rp, _, _ in plan["to_add"]:
            self._log(f"      + {rp}", color="#6FCC80")
        if n_update:
            self._log(f"  ↑  Files to update      : {n_update}", color="#FFD580")
            for rp, _, _ in plan["to_update"]:
                self._log(f"      ↑ {rp}", color="#E8C55A")
        self._log(f"  ✔  Already up to date   : {n_ok}", color=LABELCOLOR)
        if n_skip:
            self._log(f"  ⊘  Skipped (protected)  : {n_skip}", color="#A0A0A0")
            for rp in plan["skipped"]:
                self._log(f"      ⊘ {rp}", color="#808080")
        self._log("─" * 70, color="#9333EA")

        if n_add + n_update == 0:
            self._update_status("Everything is already up to date.")
            self._set_buttons(has_plan=False)
        else:
            self._update_status(
                f"Found {n_add} new file(s) and {n_update} update(s). "
                "Press 'Apply Updates' to install."
            )
            self._set_buttons(has_plan=True)

    def _start_apply(self):
        self._set_buttons(applying=True)
        self._update_progress(0)
        self._update_status("Downloading files…")
        threading.Thread(target=self._run_apply, daemon=True).start()

    def _run_apply(self):
        def log_cb(msg, frac):
            self.root.after(0, self._update_status, msg)
            self.root.after(0, self._update_progress, frac)
            self.root.after(0, self._log, msg)

        result = apply_update_plan(self._plan, log_cb=log_cb)
        self.root.after(0, self._apply_done, result)

    def _apply_done(self, result):
        errors = result["errors"]
        lfs    = result["lfs"]
        self._update_progress(1.0)
        self._log("─" * 70, color="#9333EA")

        if lfs:
            self._log(f"  ⚠  Git LFS files (cannot download via raw CDN) : {len(lfs)}",
                      color="#FFD580")
            for msg in lfs:
                self._log(f"      ⚠ {msg}", color="#E8C55A")
            self._log(
                "      → These files are stored in Git LFS. Either migrate them out of LFS",
                color="#A0A0A0")
            self._log(
                "        or distribute them separately. They were NOT overwritten locally.",
                color="#A0A0A0")

        if errors:
            self._update_status(f"Done with {len(errors)} error(s). See log for details.")
            for e in errors:
                self._log(f"  ✖ {e}", color="#FF6B6B")
        elif not lfs:
            self._update_status("✔ All files updated successfully!")
            self._log("  ✔ Update complete. You can now close this window.", color="#8FE8A0")
        else:
            self._update_status(
                f"Done — {len(lfs)} LFS file(s) skipped, everything else updated."
            )
        self._set_buttons()

def run_update():
    """Entry point when called from the launcher."""
    root = Tk()
    UpdaterApp(root)
    root.mainloop()

def main():
    """Standalone entry point."""
    root = Tk()
    UpdaterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()