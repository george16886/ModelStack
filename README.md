# AI Model Launcher

A lightweight, menu-driven command-line tool for managing and launching local AI models through [Ollama](https://ollama.com/) + [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Features

| Feature | Description |
|---------|-------------|
| **Auto-detect Models** | Automatically scans installed Ollama models — no manual config needed |
| **Running Status** | Shows which model is currently loaded in memory |
| **System Resources** | Displays real-time GPU VRAM and RAM usage |
| **Quick Launch** | Press Enter to instantly re-launch your last used model |
| **Pull Models** | Download new models directly from the menu |
| **Delete Models** | Remove unused models with confirmation prompt |
| **Update All** | One-click update for all installed models |
| **Project Selector** | Switch working directories — persisted across sessions |

## Menu Preview

```
========================================================
             AI Model Launcher
========================================================

 [*] Running: gemma4:latest
 [#] GPU: 4865 / 6144 MB  (21%)
 [#] RAM: 2.4 / 15.6 GB free
 [>] Work dir: D:\Claude Code\
 [+] Last used: gemma4:latest  (Press Enter to quick launch)

 Installed models:

  1. gemma4:e4b                (9.6 GB)
  2. gemma4:latest             (9.6 GB)  *RUNNING*
  3. llama3.2:3b               (2.0 GB)
  4. llama3.2:latest           (2.0 GB)
  5. qwen2.5-coder:3b          (1.9 GB)
  6. qwen2.5-coder:latest      (4.7 GB)

  P. Pull (download) a new model
  D. Delete a model
  U. Update all models
  W. Change working directory
  0. Exit

  Select (0-6/P/D/U/W) [Enter=gemma4:latest]:
```

## Requirements

- **Windows 10/11**
- [Ollama](https://ollama.com/) installed and running
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
- NVIDIA GPU (optional, for GPU stats display)

## Quick Start

1. Clone this repo:
   ```bash
   git clone https://github.com/george16886/Claude_Code.git
   ```
2. Double-click `run_Claude.bat`
3. Select a model number and start coding!

## File Structure

```
Claude_Code/
├── run_Claude.bat      # Main launcher script
├── config.txt          # Auto-generated user preferences (git-ignored)
├── CLAUDE.md           # Claude Code project instructions
└── bat/                # Legacy individual model scripts
    ├── gemma4.bat
    ├── llama3.2.bat
    └── qwen2.5-coder.bat
```

## Configuration

Settings are automatically saved to `config.txt` (git-ignored):

- `last_model` — Last launched model (for quick launch)
- `work_dir` — Preferred working directory

## License

MIT
