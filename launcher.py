"""AI Model Launcher — Ultimate Stability Version."""

import json
import os
import subprocess
import threading
from pathlib import Path

from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / "config.txt"
PROFILES_FILE = SCRIPT_DIR / "profiles.json"

LOGO = r"""
    _    ___   __  __           _      _
   / \  |_ _| |  \/  | ___   __| | ___| |
  / _ \  | |  | |\/| |/ _ \ / _` |/ _ \ |
 / ___ \ | |  | |  | | (_) | (_| |  __/ |
/_/   \_\___| |_|  |_|\___/ \__,_|\___|_|
"""

# ---------------------------------------------------------------------------
# Robust Command Runner
# ---------------------------------------------------------------------------
def run_cmd(cmd: str, timeout: int | None = 10) -> str:
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        return result.stdout.strip()
    except Exception:
        return ""

def get_models() -> list[dict]:
    raw = run_cmd("ollama list", timeout=10)
    models = []
    if not raw or "NAME" not in raw: return []
    lines = [l for l in raw.splitlines() if l.strip()]
    if len(lines) <= 1: return []
    for line in lines[1:]:
        p = line.split()
        if len(p) >= 3:
            name = p[0]
            # Size is usually the 3rd column, but let's be flexible
            for i in range(1, len(p)):
                try:
                    val = p[i]
                    fval = float(val)
                    unit = p[i+1] if i+1 < len(p) else "GB"
                    # Avoid accidentally picking up the ID as size
                    if unit in ["GB", "MB", "KB", "B"]:
                        models.append({"name": name, "size": fval, "unit": unit})
                        break
                except: continue
    models.sort(key=lambda x: x["name"])
    return models

def get_running_info() -> str | None:
    # Use 'ollama ps' to check running models
    raw = run_cmd("ollama ps", timeout=5)
    if not raw or "NAME" not in raw: return None
    lines = [l for l in raw.splitlines() if l.strip()]
    if len(lines) <= 1: return None
    # Usually the first entry is the most relevant
    p = lines[1].split()
    return p[0] if p else None

def get_gpu_info() -> str:
    raw = run_cmd("nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits", timeout=5)
    if not raw: return "GPU: N/A"
    p = [x.strip() for x in raw.split(",")]
    if len(p) >= 3: return f"GPU: {p[0]}/{p[1]} MB ({p[2]}%)"
    return "GPU: N/A"

def get_ram_info() -> str:
    # Try multiple methods for RAM
    try:
        raw = run_cmd('powershell -NoProfile -c "$o=Get-CimInstance Win32_OperatingSystem; [math]::Round($o.FreePhysicalMemory/1MB,1).ToString() + \'/\' + [math]::Round($o.TotalVisibleMemorySize/1MB,1).ToString()"', timeout=8)
        if raw and "/" in raw: return f"RAM: {raw.strip()} GB free"
    except: pass
    return "RAM: N/A"

def get_model_details(name):
    raw = run_cmd(f"ollama show {name}", timeout=5)
    d = {"arch": "", "params": "", "ctx": "", "quant": "", "caps": []}
    if not raw: return d
    sec = ""
    for line in raw.splitlines():
        s = line.strip()
        if not s: continue
        if s in ["Model", "Parameters", "Capabilities", "System"]: sec = s.lower(); continue
        if sec == "model":
            parts = s.split()
            if len(parts) >= 2:
                k, v = parts[0], " ".join(parts[1:])
                if k == "architecture": d["arch"] = v
                elif k == "parameters": d["params"] = v
                elif k == "context": d["ctx"] = parts[-1]
                elif k == "quantization": d["quant"] = v
        elif sec == "capabilities" and s: d["caps"].append(s)
    return d

# ---------------------------------------------------------------------------
# Modal Screens
# ---------------------------------------------------------------------------
class InputModal(ModalScreen[str]):
    DEFAULT_CSS = "InputModal { align: center middle; } #m-cont { width: 60; border: thick $accent; background: $surface; padding: 1; } #m-title { text-style: bold; margin-bottom: 1; }"
    def __init__(self, t, p=""): super().__init__(); self.t, self.p = t, p
    def compose(self) -> ComposeResult:
        with Vertical(id="m-cont"):
            yield Label(self.t, id="m-title")
            yield Input(placeholder=self.p, id="m-input")
    def on_input_submitted(self, e): self.dismiss(e.value)
    def key_escape(self): self.dismiss("")

class ConfirmModal(ModalScreen[bool]):
    DEFAULT_CSS = "ConfirmModal { align: center middle; } #c-cont { width: 40; border: thick $warning; background: $surface; padding: 1; }"
    def __init__(self, m): super().__init__(); self.m = m
    def compose(self) -> ComposeResult:
        with Vertical(id="c-cont"):
            yield Label(self.m); yield Label("Y: Yes | N/Esc: No", variant="dim")
    def key_y(self): self.dismiss(True)
    def key_n(self): self.dismiss(False)
    def key_escape(self): self.dismiss(False)

class ListModal(ModalScreen[dict]):
    DEFAULT_CSS = "ListModal { align: center middle; } #l-cont { width: 60; max-height: 20; border: thick $primary; background: $surface; padding: 1; }"
    def __init__(self, t, i): super().__init__(); self.t, self.i = t, i
    def compose(self) -> ComposeResult:
        with Vertical(id="l-cont"):
            yield Label(self.t, variant="bold")
            yield ListView(*[ListItem(Label(x)) for x in self.i], id="l-list")
            yield Label("Enter: Select | Del: Remove | Esc: Cancel", variant="dim")
    def on_list_view_selected(self, e): self.dismiss({"act": "select", "idx": e.list_view.index})
    def key_delete(self):
        idx = self.query_one("#l-list", ListView).index
        if idx is not None: self.dismiss({"act": "delete", "idx": idx})
    def key_escape(self): self.dismiss({"act": "cancel", "idx": -1})

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
class ModelStack(App):
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        Binding("p", "pull", "Pull"),
        Binding("d", "del", "Delete"),
        Binding("u", "upd", "Update"),
        Binding("w", "dir", "WorkDir"),
        Binding("b", "bm", "Bookmarks"),
        Binding("t", "prof", "Profiles"),
        Binding("r", "sync", "Sync"),
        Binding("s", "sh", "Shortcut"),
        Binding("x", "stop", "Stop"),
        Binding("q", "quit", "Quit")
    ]
    DEFAULT_CSS = """
    Screen { background: $surface; }
    Header { 
        background: $primary; 
        color: $text; 
        text-style: bold;
        dock: top;
        height: 1;
    }
    Footer { 
        background: $accent; 
        color: $text; 
        dock: bottom;
        height: 1;
        text-style: bold;
    }
    #logo { height: auto; color: $accent; margin: 0 1; }
    #stats { height: auto; min-height: 5; border: double $accent; padding: 0 1; margin: 0 1; background: $panel; }
    #models { border: round $accent; margin: 1 1; height: 1fr; background: $surface; }
    #s-in { display: none; margin: 0 1; border: tall $primary; background: $panel; color: $text; height: 3; }
    #details { display: none; height: auto; min-height: 2; border: round $success; margin: 0 1; padding: 0 1; color: $success; }
    #logs { height: auto; min-height: 3; border: round $warning; margin: 0 1; padding: 0 1; color: $warning; }
    #main-body { height: 1fr; }
    .group { color: $text-disabled; text-style: bold italic; padding: 0 1; }
    .item { padding: 0 1; }
    ListItem:focus { background: $primary; color: $text; text-style: bold; }
    Footer { 
        background: $primary; 
        color: $text; 
        dock: bottom;
        height: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self._m, self._fm, self._run = [], [], None
        self._cfg = self._load_cfg()
        self._profs = self._load_profs()
        self._bms = self._cfg.get("bookmarks", "").split("|") if self._cfg.get("bookmarks") else []
        self._bms = [x for x in self._bms if x]
        self._wdir = self._cfg.get("work_dir", "D:\\")
        self._last = self._cfg.get("last_model", "")
        self._launch, self._query = None, ""

    def _load_cfg(self):
        d = {}
        if CONFIG_FILE.exists():
            for l in CONFIG_FILE.read_text("utf-8").splitlines():
                if "=" in l: k, v = l.split("=", 1); d[k.strip()] = v.strip()
        return d

    def _save_cfg(self):
        self._cfg["bookmarks"] = "|".join(self._bms)
        CONFIG_FILE.write_text("\n".join([f"{k}={v}" for k, v in self._cfg.items()]), "utf-8")

    def _load_profs(self):
        if PROFILES_FILE.exists():
            try: return json.loads(PROFILES_FILE.read_text("utf-8")).get("profiles", [])
            except: pass
        return []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Vertical(id="main-body"):
            yield Static(LOGO, id="logo")
            yield Input(placeholder="  Search models...", id="s-in")
            with Vertical(id="stats"):
                yield Static("Initializing...", id="s-run")
                yield Static("", id="s-gpu")
                yield Static("", id="s-ram")
                yield Static("", id="s-dir")
                yield Static("", id="s-last")
            with Vertical(id="models"):
                yield Label(" ❯ INSTALLED MODELS", variant="bold")
                yield ListView(id="m-list")
            yield Static("", id="details")
            yield Static("Ready", id="logs")

    def on_mount(self):
        self.query_one("#s-in").display = False
        self.sync_data()
        self.set_interval(6, self.sync_stats)
        self.query_one("#m-list").focus()
        self.refresh()

    @work(thread=True)
    def sync_data(self):
        try:
            self.call_from_thread(self._log, "Listing models...")
            models = get_models()
            self._m = models
            
            self.call_from_thread(self._log, "Ollama check...")
            self._run = get_running_info()
            
            self.call_from_thread(self._log, "System check...")
            gpu, ram = get_gpu_info(), get_ram_info()
            
            self.call_from_thread(self._log, "Finalizing UI...")
            self.call_from_thread(self._upd_ui, gpu, ram)
            self.call_from_thread(self._log, "Ready.")
        except Exception as e: self.call_from_thread(self._log, f"Error: {e}")

    @work(thread=True)
    def sync_stats(self):
        try:
            r = get_running_info()
            g, rm = get_gpu_info(), get_ram_info()
            self.call_from_thread(self._upd_stats, r, g, rm)
        except: pass

    def _upd_ui(self, g, rm):
        self._upd_stats(self._run, g, rm)
        self._rebuild()

    def _upd_stats(self, r, g, rm):
        try:
            self._run = r
            self.query_one("#s-run", Static).update(Text(f" ⦿ Running: {r or '(none)'}", style="bold green" if r else "white"))
            self.query_one("#s-gpu", Static).update(Text(f" ⚛ {g}", style="yellow"))
            self.query_one("#s-ram", Static).update(Text(f" ⚙ {rm}", style="yellow"))
            self.query_one("#s-dir", Static).update(Text(f" ➔ Dir: {self._wdir}", style="blue"))
            l = f" ♥ Preferred: {self._last}" if self._last else ""
            self.query_one("#s-last", Static).update(Text(l, style="cyan"))
        except: pass

    def _rebuild(self):
        try:
            lv = self.query_one("#m-list", ListView)
            curr_idx = lv.index
            lv.clear()
            fm = [x for x in self._m if self._query.lower() in x["name"].lower()] if self._query else self._m[:]
            groups = {}
            for m in fm:
                b = m["name"].split(":")[0] if ":" in m["name"] else m["name"]
                groups.setdefault(b, []).append(m)
            for gn in sorted(groups.keys()):
                lv.append(ListItem(Label(f"── {gn} ──"), classes="group"))
                for m in groups[gn]:
                    n, s, u = m["name"], m["size"], m["unit"]
                    t = n.split(":")[-1] if ":" in n else n
                    txt = Text(f"  {t:<20} ({s} {u})")
                    if n == self._run: txt.stylize("bold green")
                    elif n == self._last: txt.stylize("bold cyan")
                    if n == self._run: txt.append(" *RUNNING*", style="bold green")
                    lv.append(ListItem(Label(txt), classes="item"))
            if curr_idx is not None and curr_idx < len(lv.children):
                lv.index = curr_idx
        except: pass

    def _log(self, m):
        try: self.query_one("#logs", Static).update(Text(m))
        except: pass

    def on_list_view_highlighted(self, e):
        m = self._get_m(e.list_view.index)
        det = self.query_one("#details", Static)
        if m: 
            det.display = True
            self._show_det(m["name"])
        else: 
            det.display = False
            det.update("")

    @work(thread=True)
    def _show_det(self, n):
        d = get_model_details(n)
        self.call_from_thread(self.query_one("#details", Static).update, Text(f"{n} | {d['params']} | {d['quant']} | {d['ctx']}"))

    def _get_m(self, i):
        if i is None or i < 0: return None
        fm = [x for x in self._m if self._query.lower() in x["name"].lower()] if self._query else self._m[:]
        groups = {}
        for m in fm:
            b = m["name"].split(":")[0] if ":" in m["name"] else m["name"]
            groups.setdefault(b, []).append(m)
        idx = 0
        for gn in sorted(groups.keys()):
            if idx == i: return None # Group header
            idx += 1
            for m in groups[gn]:
                if idx == i: return m
                idx += 1
        return None

    def on_key(self, event):
        # Prevent input box from losing focus when typing / or f
        pass

    def on_input_changed(self, e):
        if e.input.id == "s-in": self._query = e.value; self._rebuild()

    def on_list_view_selected(self, e):
        m = self._get_m(e.list_view.index)
        if m: self._launch_m(m["name"])

    def _launch_m(self, n):
        self._launch = n
        self._cfg["last_model"] = n
        self._cfg["work_dir"] = self._wdir
        self._save_cfg(); self.exit()

    def action_pull(self): self.push_screen(InputModal("Pull", "phi3"), callback=self._do_pull)
    @work(thread=True)
    def _do_pull(self, n):
        if n: self._log(f"Pulling {n}..."); run_cmd(f"ollama pull {n}", None); self.sync_data()
    
    def action_del(self):
        m = self._get_m(self.query_one("#m-list").index)
        if m: self.push_screen(ConfirmModal(f"Delete {m['name']}?"), callback=lambda y: self._do_del(m["name"]) if y else None)
    @work(thread=True)
    def _do_del(self, n): run_cmd(f"ollama rm {n}"); self.sync_data()

    def action_upd(self): 
        if self._m: self.push_screen(ConfirmModal("Update all models?"), callback=lambda y: self._do_upd() if y else None)
    @work(thread=True)
    def _do_upd(self):
        for m in self._m: 
            name = m["name"]
            self.call_from_thread(self._log, f"Updating {name}...")
            run_cmd(f'ollama pull "{name}"', None)
        self.sync_data()

    def action_stop(self):
        if self._run: self.push_screen(ConfirmModal(f"Stop {self._run}?"), callback=lambda y: self._do_stop(self._run) if y else None)
    @work(thread=True)
    def _do_stop(self, n): run_cmd(f"ollama stop {n}"); self.sync_data()

    def action_dir(self): self.push_screen(InputModal("Work Dir", self._wdir), callback=self._do_dir)
    def _do_dir(self, p):
        if p and os.path.isdir(p): self._wdir = p; self._cfg["work_dir"] = p; self._save_cfg(); self.sync_data()

    def action_bm(self): self.push_screen(ListModal("Bookmarks", self._bms + ["+ Add Current"]), callback=self._handle_bm)
    def _handle_bm(self, r):
        idx, act = r.get("idx", -1), r.get("act")
        self.query_one("#m-list").focus()
        if idx == -1 or act == "cancel": return
        if act == "delete":
            if 0 <= idx < len(self._bms): self._bms.pop(idx); self._save_cfg(); self.set_timer(0.2, self.action_bm)
            return
        if idx == len(self._bms):
            if self._wdir not in self._bms: self._bms.append(self._wdir); self._save_cfg(); self.sync_data()
        else: self._wdir = self._bms[idx]; self._cfg["work_dir"] = self._wdir; self._save_cfg(); self.sync_data()

    def action_prof(self):
        if self._profs: self.push_screen(ListModal("Profiles", [f"{x['name']} ({x['model']})" for x in self._profs]), callback=self._handle_prof)
    def _handle_prof(self, r):
        idx = r.get("idx", -1)
        self.query_one("#m-list", ListView).focus()
        if idx == -1: return
        p = self._profs[idx]
        mod = p.get("model", "")
        if mod: self._last = mod; self._cfg["last_model"] = mod
        wd = p.get("work_dir", "")
        if wd and os.path.isdir(wd): 
            self._wdir = wd; self._cfg["work_dir"] = wd
        elif wd:
            self._log(f"Warning: Directory not found: {wd}")
        self._save_cfg()
        self.sync_data()
        self._log(f"Profile: {p['name']} set.")

    @work(thread=True)
    def action_sh(self):
        try:
            d = run_cmd("powershell -c '[Environment]::GetFolderPath(\"Desktop\")'")
            if not d: d = str(Path.home() / "Desktop")
            sh = Path(d) / "AI Launcher.lnk"
            # Using double quotes and properly escaping for PowerShell inside CMD
            cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut(\'{sh}\'); $s.TargetPath = \'python.exe\'; $s.Arguments = \'{SCRIPT_DIR / "launcher.py"}\'; $s.WorkingDirectory = \'{SCRIPT_DIR}\'; $s.Save()"'
            run_cmd(cmd)
            self._log("Shortcut created.")
        except: pass

    def action_sync(self): self.sync_data()

def main():
    while True:
        try:
            app = ModelStack()
            app.run()
            
            # If a model was chosen to be launched
            if app._launch:
                target_dir = app._wdir
                if not os.path.isdir(target_dir):
                    print(f"\n [!] Warning: Directory not found: {target_dir}")
                    print(" [➔] Falling back to default: D:\\")
                    target_dir = "D:\\"
                    if not os.path.isdir(target_dir):
                        # Final fallback to script root if D: is missing
                        target_dir = str(SCRIPT_DIR)
                
                os.chdir(target_dir)
                print(f"\n  ⦿ Launching {app._launch} in {target_dir} ...\n")
                
                # Use a more robust subprocess call with quotes
                cmd = f'ollama launch claude --model "{app._launch}"'
                ret = subprocess.run(cmd, shell=True)
                
                if ret.returncode != 0:
                    print(f"\n [!] Error: Command failed with exit code {ret.returncode}")
                    print(f" [?] Attempting fallback launch: ollama run \"{app._launch}\"")
                    subprocess.run(f'ollama run "{app._launch}"', shell=True)
                
                print("\n  ➔ Session ended. Returning to launcher...")
                input("  Press Enter to continue...")
            else:
                # User quit normally
                break
        except Exception as e:
            print(f"\n [!!!] CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            input("\n Press Enter to exit...")
            break

if __name__ == "__main__":
    main()
