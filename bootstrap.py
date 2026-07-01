"""
Bleach Rebirth of Souls Community Patch - bundled launcher (bootstrap).

This is the file that gets frozen into the single-file executable. Everything
the patch needs (Python, Tkinter, pygame) is packed inside this binary, so the
user installs nothing. On every launch it:

    1. makes sure the patch is downloaded and up to date (via updater.py,
       which uses plain HTTPS - no git required), then
    2. runs the real launcher using this binary's bundled Python runtime.

Because the actual launcher code is downloaded (not frozen in), code changes
ship to players automatically on the next launch - the same "updates every
launch" behaviour the old git-based version had, minus the dependencies.
"""

import os
import runpy
import sys
import threading
import traceback

MAIN_FILE = "Bleach Rebirth of Souls Community Patch.py"


# --- where the downloaded patch lives (writable, per-user) ------------------
def app_dir():
    override = os.environ.get("BCP_HOME")
    if override:
        root = override
    elif sys.platform.startswith("win"):
        root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        root = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:
        root = os.environ.get("XDG_DATA_HOME") or \
            os.path.join(os.path.expanduser("~"), ".local", "share")
    d = os.path.join(root, "BleachCommunityPatch")
    os.makedirs(d, exist_ok=True)
    return d


def resource_dir():
    """Folder holding bundled resources (updater.py, icon). When frozen this is
    PyInstaller's temp extraction dir; otherwise it's this file's folder."""
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def payload_dir():
    # Running from a full source checkout (python bootstrap.py)? Update that
    # checkout in place instead of downloading a second copy. When frozen,
    # resource_dir() is a temp dir without the launcher, so we fall through.
    if os.environ.get("BCP_HOME") is None and not getattr(sys, "frozen", False):
        here = resource_dir()
        if os.path.isfile(os.path.join(here, MAIN_FILE)):
            return here
    return os.path.join(app_dir(), "patch")


PAYLOAD = payload_dir()
MAIN_PY = os.path.join(PAYLOAD, MAIN_FILE)


def _import_updater():
    # prefer the copy bundled with this binary (known-good, matches bootstrap)
    sys.path.insert(0, resource_dir())
    import updater
    return updater


# --- tiny progress UI (best-effort; falls back to stdout) -------------------
class Reporter:
    """Shows a small 'updating...' window if Tkinter is available, otherwise
    just prints. The actual update runs on a worker thread so the window stays
    responsive."""

    def __init__(self):
        self._tk = None
        self._label = None
        self._root = None

    def __enter__(self):
        try:
            import tkinter as tk
            from tkinter import ttk
            self._tk = tk
            self._root = tk.Tk()
            self._root.title("Bleach Community Patch")
            self._root.geometry("420x120")
            self._root.resizable(False, False)
            try:
                ico = os.path.join(resource_dir(), "ressources", "pimplin.ico")
                if os.path.isfile(ico):
                    self._root.iconbitmap(ico)
            except Exception:
                pass
            self._label = tk.Label(self._root, text="Checking for updates...",
                                   wraplength=400, justify="center")
            self._label.pack(expand=True, fill="both", padx=12, pady=(16, 4))
            bar = ttk.Progressbar(self._root, mode="indeterminate", length=380)
            bar.pack(pady=(0, 14))
            bar.start(12)
        except Exception:
            self._root = None       # headless / no Tk -> stdout fallback
        return self

    def set(self, msg):
        if self._root is not None:
            try:
                self._label.config(text=msg)
            except Exception:
                pass
        else:
            print(msg, flush=True)

    # run `func` on a worker while pumping the Tk event loop
    def run(self, func):
        if self._root is None:
            return func(self.set)        # headless: just run it
        result = {}
        def worker():
            try:
                result["value"] = func(self.set)
            except Exception as e:      # noqa: BLE001
                result["error"] = e
            finally:
                try:
                    self._root.after(0, self._root.quit)
                except Exception:
                    pass
        threading.Thread(target=worker, daemon=True).start()
        self._root.mainloop()
        if "error" in result:
            raise result["error"]
        return result.get("value")

    def __exit__(self, *exc):
        if self._root is not None:
            try:
                self._root.destroy()
            except Exception:
                pass
        return False


def _fatal(msg):
    try:
        import tkinter as tk
        from tkinter import messagebox
        r = tk.Tk(); r.withdraw()
        messagebox.showerror("Bleach Community Patch", msg)
        r.destroy()
    except Exception:
        print("ERROR:", msg, file=sys.stderr)


def main():
    updater = None
    try:
        updater = _import_updater()
    except Exception:
        pass  # we can still launch an existing copy if the import fails

    if updater is not None:
        try:
            with Reporter() as rep:
                rep.run(lambda p: updater.update(PAYLOAD, progress=p))
        except Exception as e:                  # noqa: BLE001
            # An update failure is only fatal if we have nothing to run.
            if not os.path.isfile(MAIN_PY):
                _fatal("Couldn't download the patch. Check your internet "
                       f"connection and try again.\n\n{e}")
                return
            # otherwise: stay offline and launch the copy we already have
            print("Update skipped (offline?):", e, file=sys.stderr)

    if not os.path.isfile(MAIN_PY):
        _fatal("The patch isn't installed yet and it couldn't be downloaded.")
        return

    # Hand off to the real launcher, using THIS binary's bundled runtime.
    # Running it from PAYLOAD keeps its __file__-relative paths working and
    # makes `import updater` resolve to the (also-updated) payload copy.
    sys.path.insert(0, PAYLOAD)
    os.chdir(PAYLOAD)
    runpy.run_path(MAIN_PY, run_name="__main__")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        _fatal("The launcher hit an unexpected error:\n\n" + traceback.format_exc())
