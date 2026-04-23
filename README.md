# AI Model Launcher

A premium, menu-driven terminal tool for managing and launching local AI models through [Ollama](https://ollama.com/) + [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

Available in three editions:
- **Python TUI** (recommended) — Rich interactive interface with keyboard navigation
- **PowerShell** — Lightweight colored terminal version
- **Batch** — Smart launcher that auto-detects the best runtime

## Features

| Feature | Python TUI | PowerShell | Description |
|---------|:---------:|:----------:|-------------|
| Auto-detect models | ✅ | ✅ | Scans installed Ollama models automatically |
| Running status | ✅ | ✅ | Shows which model is loaded in VRAM |
| GPU/RAM monitor | ✅ | ✅ | Real-time resource usage display |
| Pull models | ✅ | ✅ | Download new models from the menu |
| Delete models | ✅ | ✅ | Remove models with confirmation |
| Update all | ✅ | ✅ | One-click update for all models |
| Quick launch | ✅ | ✅ | Press Enter to re-launch last model |
| Project selector | ✅ | ✅ | Switch working directories |
| Task profiles | ✅ | — | Pre-configured model + directory combos |
| Keyboard navigation | ✅ | — | Arrow keys + Enter selection |
| Auto-refresh stats | ✅ | — | GPU/RAM updates every 5 seconds |

## Python TUI Preview

```
╭─── AI Model Launcher ───────────────────────────────╮
│                                                      │
│  [*] Running: gemma4:latest                          │
│  [#] GPU: 4865/6144 MB (21%)                         │
│  [#] RAM: 2.4/15.6 GB free                           │
│  [>] Work dir: D:\Claude Code\                       │
│  [+] Last used: gemma4:latest                        │
│                                                      │
│  Installed Models                                    │
│  ─────────────────────────────────────────────────   │
│  > gemma4:e4b                (9.6 GB)                │
│    gemma4:latest             (9.6 GB) *RUNNING*      │
│    llama3.2:3b               (2.0 GB)                │
│    llama3.2:latest           (2.0 GB)                │
│    qwen2.5-coder:3b          (1.9 GB)                │
│    qwen2.5-coder:latest      (4.7 GB)                │
│                                                      │
╰──────────────────────────────────────────────────────╯
 P Pull  D Delete  U Update all  W Work dir  T Profiles  Q Quit
```

## Requirements

- **Windows 10/11**
- [Ollama](https://ollama.com/) installed and running
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
- **Python 3.10+** (for TUI version)
- NVIDIA GPU (optional, for GPU stats)

## Quick Start

1. Clone this repo:
   ```bash
   git clone https://github.com/george16886/Claude_Code.git
   cd Claude_Code
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch:
   ```bash
   # Auto-detect best runtime
   run_Claude.bat

   # Or launch directly
   python launcher.py          # Python TUI
   powershell launcher.ps1     # PowerShell version
   ```

## Task Profiles

Edit `profiles.json` to define your workflow presets:

```json
{
  "profiles": [
    {
      "name": "Coding",
      "icon": ">>",
      "model": "qwen2.5-coder:latest",
      "work_dir": "D:\\Projects",
      "description": "Code generation and review"
    }
  ]
}
```

Press `T` in the Python TUI to switch profiles. Each profile auto-sets the model and working directory.

## File Structure

```
Claude_Code/
├── launcher.py         # Python TUI (Textual + Rich)
├── launcher.ps1        # PowerShell version
├── run_Claude.bat      # Smart launcher (auto-detects runtime)
├── profiles.json       # Task profile configuration
├── requirements.txt    # Python dependencies
├── config.txt          # Auto-generated preferences (git-ignored)
├── CLAUDE.md           # Claude Code project instructions
└── bat/                # Legacy individual model scripts
    ├── gemma4.bat
    ├── llama3.2.bat
    └── qwen2.5-coder.bat
```

## Keyboard Shortcuts (Python TUI)

| Key | Action |
|-----|--------|
| `↑` `↓` | Navigate model list |
| `Enter` | Launch selected model |
| `P` | Pull a new model |
| `D` | Delete selected model |
| `U` | Update all models |
| `W` | Change working directory |
| `T` | Switch task profile |
| `R` | Refresh data |
| `Q` | Quit |

## License

MIT
