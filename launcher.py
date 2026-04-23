"""AI Model Launcher — Interactive TUI built with Textual + Rich."""

import json
import os
import subprocess
import sys
from pathlib import Path

from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def run_cmd(cmd: str) -> str:
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_models() -> list[dict]:
    """Return list of installed models with name and size."""
    raw = run_cmd("ollama list")
    models = []
    for line in raw.splitlines()[1:]:  # skip header
        parts = line.split()
        if len(parts) >= 3:
            name = parts[0]
            # Find size: look for a number followed by GB/MB
            for i, p in enumerate(parts):
                try:
                    size = float(p)
                    unit = parts[i + 1] if i + 1 < len(parts) else "GB"
                    models.append({"name": name, "size": size, "unit": unit})
                    break
                except (ValueError, IndexError):
                    continue
    models.sort(key=lambda m: m["name"])
    return models


def get_running() -> str | None:
    """Return the name of the currently running model, or None."""
    raw = run_cmd("ollama ps")
    for line in raw.splitlines()[1:]:
        parts = line.split()
        if parts:
            return parts[0]
    return None


def get_gpu_info() -> str:
    """Return GPU usage string."""
    raw = run_cmd(
        "nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu "
        "--format=csv,noheader,nounits"
    )
    if not raw:
        return "GPU: N/A"
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) >= 3:
        return f"GPU: {parts[0]}/{parts[1]} MB ({parts[2]}%)"
    return "GPU: N/A"


def get_ram_info() -> str:
    """Return RAM usage string."""
    raw = run_cmd(
        'powershell -NoProfile -c "'
        "$os=Get-CimInstance Win32_OperatingSystem;"
        "$free=[math]::Round($os.FreePhysicalMemory/1MB,1);"
        "$total=[math]::Round($os.TotalVisibleMemorySize/1MB,1);"
        'Write-Host \\"$free/$total\\""'
    )
    if "/" in raw:
        free, total = raw.split("/")
        return f"RAM: {free}/{total} GB free"
    return "RAM: N/A"


def load_config() -> dict:
    """Load config.txt key=value pairs."""
    cfg = {}
    if CONFIG_FILE.exists():
        for line in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    return cfg


def save_config(cfg: dict) -> None:
    """Save config.txt."""
    lines = [f"{k}={v}" for k, v in cfg.items()]
    CONFIG_FILE.write_text("\n".join(lines), encoding="utf-8")


def load_profiles() -> list[dict]:
    """Load profiles.json."""
    if PROFILES_FILE.exists():
        try:
            data = json.loads(PROFILES_FILE.read_text(encoding="utf-8"))
            return data.get("profiles", [])
        except Exception:
            return []
    return []


# ---------------------------------------------------------------------------
# Modal screens
# ---------------------------------------------------------------------------
class InputModal(ModalScreen[str]):
    """Simple modal with a text input."""

    CSS = """
    InputModal {
        align: center middle;
    }
    #modal-container {
        width: 60;
        height: auto;
        max-height: 12;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    #modal-title {
        text-style: bold;
        margin-bottom: 1;
    }
    """

    def __init__(self, title: str, placeholder: str = "") -> None:
        super().__init__()
        self._title = title
        self._placeholder = placeholder

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-container"):
            yield Label(self._title, id="modal-title")
            yield Input(placeholder=self._placeholder, id="modal-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def key_escape(self) -> None:
        self.dismiss("")


class ConfirmModal(ModalScreen[bool]):
    """Yes/No confirmation modal."""

    CSS = """
    ConfirmModal {
        align: center middle;
    }
    #confirm-container {
        width: 50;
        height: auto;
        max-height: 10;
        border: thick $warning;
        background: $surface;
        padding: 1 2;
    }
    #confirm-msg {
        margin-bottom: 1;
    }
    #confirm-hint {
        color: $text-muted;
    }
    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-container"):
            yield Label(self._message, id="confirm-msg")
            yield Label("Press Y to confirm, N or Esc to cancel", id="confirm-hint")

    def key_y(self) -> None:
        self.dismiss(True)

    def key_n(self) -> None:
        self.dismiss(False)

    def key_escape(self) -> None:
        self.dismiss(False)


class ProfileModal(ModalScreen[dict | None]):
    """Profile selection modal."""

    CSS = """
    ProfileModal {
        align: center middle;
    }
    #profile-container {
        width: 60;
        height: auto;
        max-height: 20;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    #profile-title {
        text-style: bold;
        margin-bottom: 1;
    }
    .profile-item {
        padding: 0 1;
    }
    """

    def __init__(self, profiles: list[dict]) -> None:
        super().__init__()
        self._profiles = profiles

    def compose(self) -> ComposeResult:
        with Vertical(id="profile-container"):
            yield Label("Task Profiles", id="profile-title")
            items = []
            for p in self._profiles:
                icon = p.get("icon", "--")
                name = p.get("name", "?")
                desc = p.get("description", "")
                model = p.get("model", "")
                label = f"[bold]{icon}[/bold] {name}  [dim]{desc}[/dim]  [{model}]"
                items.append(ListItem(Label(label), classes="profile-item"))
            yield ListView(*items, id="profile-list")
            yield Label("[dim]Press Esc to cancel[/dim]")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        idx = event.list_view.index
        if 0 <= idx < len(self._profiles):
            self.dismiss(self._profiles[idx])

    def key_escape(self) -> None:
        self.dismiss(None)


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------
class LauncherApp(App):
    """AI Model Launcher TUI."""

    TITLE = "AI Model Launcher"

    CSS = """
    Screen {
        background: $surface;
    }
    #main-container {
        height: 1fr;
    }
    #status-panel {
        height: auto;
        max-height: 8;
        border: round $primary;
        padding: 0 1;
        margin: 0 1;
    }
    .status-line {
        height: 1;
    }
    #model-panel {
        border: round $accent;
        margin: 0 1;
        height: 1fr;
    }
    #model-title {
        text-style: bold;
        padding: 0 1;
    }
    .model-item {
        padding: 0 1;
    }
    #log-panel {
        height: auto;
        max-height: 5;
        border: round $warning;
        margin: 0 1;
        padding: 0 1;
        overflow-y: auto;
    }
    """

    BINDINGS = [
        Binding("p", "pull_model", "Pull model"),
        Binding("d", "delete_model", "Delete model"),
        Binding("u", "update_all", "Update all"),
        Binding("w", "change_dir", "Work dir"),
        Binding("t", "switch_profile", "Profiles"),
        Binding("r", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
        Binding("enter", "launch_selected", "Launch", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._models: list[dict] = []
        self._running: str | None = None
        self._config = load_config()
        self._profiles = load_profiles()
        self._work_dir = self._config.get("work_dir", str(SCRIPT_DIR))
        self._last_model = self._config.get("last_model", "")
        self._launch_model: str | None = None  # Set when we want to launch

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="main-container"):
            with Vertical(id="status-panel"):
                yield Static("", id="stat-running", classes="status-line")
                yield Static("", id="stat-gpu", classes="status-line")
                yield Static("", id="stat-ram", classes="status-line")
                yield Static("", id="stat-workdir", classes="status-line")
                yield Static("", id="stat-last", classes="status-line")
            with Vertical(id="model-panel"):
                yield Label("Installed Models", id="model-title")
                yield ListView(id="model-list")
            yield Static("", id="log-panel")
        yield Footer()

    def on_mount(self) -> None:
        """Initial data load."""
        self.refresh_data()
        self.set_interval(5, self.refresh_stats)

    @work(thread=True)
    def refresh_data(self) -> None:
        """Reload models and stats."""
        self._models = get_models()
        self._running = get_running()
        gpu = get_gpu_info()
        ram = get_ram_info()
        self.app.call_from_thread(self._update_ui, gpu, ram)

    @work(thread=True)
    def refresh_stats(self) -> None:
        """Refresh only system stats (GPU/RAM)."""
        self._running = get_running()
        gpu = get_gpu_info()
        ram = get_ram_info()
        self.app.call_from_thread(self._update_stats_ui, gpu, ram)

    def _update_ui(self, gpu: str, ram: str) -> None:
        """Update full UI including model list."""
        self._update_stats_ui(gpu, ram)

        # Update model list
        lv = self.query_one("#model-list", ListView)
        lv.clear()
        for m in self._models:
            name = m["name"]
            size = m["size"]
            unit = m["unit"]

            label_parts = []
            if name == self._running:
                label_parts.append(f"[bold green]{name:<25}[/bold green]")
                label_parts.append(f"({size} {unit})")
                label_parts.append("[bold green] *RUNNING*[/bold green]")
            elif name == self._last_model:
                label_parts.append(f"[bold cyan]{name:<25}[/bold cyan]")
                label_parts.append(f"({size} {unit})")
                label_parts.append("[cyan] (last used)[/cyan]")
            else:
                label_parts.append(f"{name:<25}")
                label_parts.append(f"({size} {unit})")

            item_label = Label(" ".join(label_parts), markup=True)
            lv.append(ListItem(item_label, classes="model-item"))

    def _update_stats_ui(self, gpu: str, ram: str) -> None:
        """Update status panel."""
        running_text = self._running or "(none)"
        color = "green" if self._running else "dim"
        self.query_one("#stat-running", Static).update(
            Text.from_markup(f"[{color}][*] Running: {running_text}[/{color}]")
        )
        self.query_one("#stat-gpu", Static).update(
            Text.from_markup(f"[yellow][#] {gpu}[/yellow]")
        )
        self.query_one("#stat-ram", Static).update(
            Text.from_markup(f"[yellow][#] {ram}[/yellow]")
        )
        self.query_one("#stat-workdir", Static).update(
            Text.from_markup(f"[blue][>] Work dir: {self._work_dir}[/blue]")
        )
        if self._last_model:
            self.query_one("#stat-last", Static).update(
                Text.from_markup(
                    f"[cyan][+] Last used: {self._last_model}  "
                    f"(Select & Enter to launch)[/cyan]"
                )
            )
        else:
            self.query_one("#stat-last", Static).update("")

    def _log(self, msg: str) -> None:
        """Show a log message."""
        self.query_one("#log-panel", Static).update(
            Text.from_markup(f"[dim]{msg}[/dim]")
        )

    # --- Actions ---

    def action_launch_selected(self) -> None:
        """Launch the selected model."""
        lv = self.query_one("#model-list", ListView)
        idx = lv.index
        if idx is not None and 0 <= idx < len(self._models):
            model_name = self._models[idx]["name"]
            self._launch_model = model_name
            self._last_model = model_name
            self._config["last_model"] = model_name
            self._config["work_dir"] = self._work_dir
            save_config(self._config)
            self.exit()

    def action_pull_model(self) -> None:
        """Pull a new model."""
        def on_result(name: str) -> None:
            if name:
                self._do_pull(name)

        self.push_screen(
            InputModal("Pull Model", "e.g. phi3, mistral, deepseek-r1"),
            callback=on_result,
        )

    @work(thread=True)
    def _do_pull(self, name: str) -> None:
        self.app.call_from_thread(self._log, f"Downloading {name} ...")
        run_cmd(f"ollama pull {name}")
        self.app.call_from_thread(self._log, f"Done: {name}")
        self.refresh_data()

    def action_delete_model(self) -> None:
        """Delete the selected model."""
        lv = self.query_one("#model-list", ListView)
        idx = lv.index
        if idx is not None and 0 <= idx < len(self._models):
            model_name = self._models[idx]["name"]

            def on_confirm(yes: bool) -> None:
                if yes:
                    self._do_delete(model_name)

            self.push_screen(
                ConfirmModal(f"Delete {model_name}?"), callback=on_confirm
            )

    @work(thread=True)
    def _do_delete(self, name: str) -> None:
        self.app.call_from_thread(self._log, f"Deleting {name} ...")
        run_cmd(f"ollama rm {name}")
        self.app.call_from_thread(self._log, f"Deleted: {name}")
        self.refresh_data()

    def action_update_all(self) -> None:
        """Update all models."""
        self._do_update_all()

    @work(thread=True)
    def _do_update_all(self) -> None:
        models = self._models[:]
        total = len(models)
        for i, m in enumerate(models, 1):
            name = m["name"]
            self.app.call_from_thread(
                self._log, f"Updating [{i}/{total}] {name} ..."
            )
            run_cmd(f"ollama pull {name}")
        self.app.call_from_thread(self._log, f"All {total} models updated.")
        self.refresh_data()

    def action_change_dir(self) -> None:
        """Change working directory."""
        def on_result(path: str) -> None:
            if path:
                if os.path.isdir(path):
                    self._work_dir = path
                    self._config["work_dir"] = path
                    save_config(self._config)
                    self.refresh_data()
                else:
                    self._log(f"Not a valid directory: {path}")

        self.push_screen(
            InputModal("Working Directory", self._work_dir), callback=on_result
        )

    def action_switch_profile(self) -> None:
        """Switch task profile."""
        if not self._profiles:
            self._log("No profiles found. Edit profiles.json to add some.")
            return

        def on_result(profile: dict | None) -> None:
            if profile:
                model = profile.get("model", "")
                work_dir = profile.get("work_dir", "")
                name = profile.get("name", "")

                if model:
                    self._last_model = model
                    self._config["last_model"] = model
                if work_dir and os.path.isdir(work_dir):
                    self._work_dir = work_dir
                    self._config["work_dir"] = work_dir

                save_config(self._config)
                self._log(f"Profile: {name} | Model: {model} | Dir: {work_dir}")
                self.refresh_data()

        self.push_screen(ProfileModal(self._profiles), callback=on_result)

    def action_refresh(self) -> None:
        """Manual refresh."""
        self._log("Refreshing...")
        self.refresh_data()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the launcher. Supports re-launch loop."""
    while True:
        app = LauncherApp()
        app.run()

        model = app._launch_model
        work_dir = app._work_dir

        if model:
            # Exit TUI, launch model, then loop back
            os.chdir(work_dir)
            print(f"\n  Launching {model} in {work_dir} ...\n")
            subprocess.run(f"ollama launch claude --model {model}", shell=True)
            print("\n  Session ended. Restarting launcher...\n")
            input("  Press Enter to continue...")
        else:
            break


if __name__ == "__main__":
    main()
