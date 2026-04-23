# 🚀 ModelStack: The Ultimate AI Model Launcher

ModelStack is a high-performance, aesthetically pleasing terminal user interface (TUI) designed to streamline your LLM workflow. It provides a centralized hub for managing [Ollama](https://ollama.com/) models and seamlessly integrates with tools like **Claude Code**.

![ModelStack Interface](https://raw.githubusercontent.com/george16886/ModelStack/master/screenshot.png) *(Placeholder for your screenshot)*

## ✨ Key Features

- **💎 Premium TUI**: Built with Python's Textual framework for a smooth, interactive experience.
- **📊 Real-time Monitoring**: Live tracking of GPU memory (VRAM), RAM usage, and system statistics.
- **🔍 Intelligent Search**: Instantly filter through your model library as you type.
- **📁 Context Awareness**: Manage working directories with built-in **Bookmarks**.
- **🎯 Task Profiles**: Switch between specialized model configurations for different workflows (Coding, Creative, Logic).
- **🔄 Auto-Sync**: Automatically synchronizes your `settings.json` and `statusline.sh` to your Claude environment on startup.
- **⚡ Dual Mode**: Use the feature-rich **Python TUI** for the best experience, or the **Lightweight PowerShell** version for quick access with zero dependencies.

---

## 🛠️ Requirements

- **Ollama**: [Download here](https://ollama.com/)
- **Python 3.10+** (Required for the TUI version)
- **PowerShell 5.1+** (For the lightweight version)

---

## 📥 Installation

```bash
# Clone the repository
git clone https://github.com/george16886/ModelStack.git
cd ModelStack

# Install dependencies for the Python TUI
pip install -r requirements.txt
```

---

## 🚀 Getting Started

### Python TUI Version (Recommended)
Experience the full power of ModelStack with live updates and mouse support.
```bash
python launcher.py
```

### PowerShell Version
A fast, one-file alternative for systems without Python.
```powershell
.\launcher.ps1
```

---

## ⌨️ Keyboard Shortcuts (Python TUI)

| Key | Action | Description |
|:---:|:---|:---|
| `P` | **Pull** | Download a new model from Ollama Hub |
| `D` | **Delete** | Remove a selected model from local storage |
| `U` | **Update** | Sync all local models with latest versions |
| `W` | **WorkDir** | Set the current execution directory |
| `B` | **Bookmarks** | Access saved project paths |
| `T` | **Profiles** | Switch between task-specific model profiles |
| `R` | **Sync** | Refresh system stats and sync Claude configs |
| `X` | **Stop** | Instantly stop the currently running model |
| `Q` | **Quit** | Exit the launcher |

---

## 📂 Configuration

- `profiles.json`: Define your custom task profiles and their associated models.
- `config.txt`: Stores your application state, recently used models, and bookmarks.
- `statusline.sh`: Customizable status line for your terminal environment.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue for any bugs or feature requests.

## 📄 License

MIT License - feel free to use and modify for your own projects.
