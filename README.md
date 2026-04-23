# AI Model Launcher (ModelStack)

A powerful and aesthetic TUI for managing and launching Ollama models with integrations like Claude Code.

## Features

- **Model Management**: List, pull, update, and delete Ollama models.
- **Search**: Fast search and filtering (Python version only).
- **Bookmarks**: Save and switch between working directories.
- **Profiles**: Pre-configured task profiles for different workflows.
- **Stats**: Real-time GPU and RAM monitoring.
- **Shortcut**: Easily create a desktop shortcut to start the launcher.

## Requirements

- [Ollama](https://ollama.com/) (latest version recommended)
- Python 3.10+ (for TUI version)
- PowerShell 5.1+ (for lightweight version)

## Installation

```bash
pip install textual rich
```

## Running the Launcher

### Python TUI Version (Recommended)
```bash
python launcher.py
```

### PowerShell Version
```powershell
.\launcher.ps1
```

## Shortcuts (Python TUI)
- `/` or `F`: Search
- `P`: Pull Model
- `D`: Delete Model
- `U`: Update All
- `W`: Set Working Directory
- `B`: Bookmarks
- `T`: Task Profiles
- `S`: Create Desktop Shortcut
- `X`: Stop Model
- `Q`: Quit
