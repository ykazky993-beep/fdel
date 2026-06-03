# fdel - File Manager CLI Tool

**fdel** is a powerful, safety-protected command-line file manager that lets you search, delete, move, rename, and copy files with ease.

## Features

- 🎯 **Fuzzy Search** - Find files by name matching
- 🛡️ **Safety Layer** - Protects system files and sensitive data
- 📁 **Explore Mode** - Browse folder structure like `tree`
- 🧹 **Clean Empty** - Find and delete empty folders/files
- ↩️ **Undo Support** - Revert move/rename/copy operations
- 🔄 **Batch Operations** - Process multiple files at once
- 💻 **Cross-Platform** - Works on Linux, macOS, Windows, Termux
- 📃 **Full Explanation** - Full explaination for manual usage and "what for"
## Safety Features

| Level | Indicator | Description | Action Required |
|-------|-----------|-------------|-----------------|
| **CRITICAL** | 🔴 | System files (/etc, /bin, shadow, passwd) | Yes/No confirmation |
| **WARNING** | 🟡 | Sensitive files (configs, keys, .env) | Yes/No confirmation |
| **SAFE** | 🟢 | User files (Documents, Downloads) | Normal confirmation |

## Installation

```bash
# From source
git clone https://github.com/ykazky993-beep/fdel.git
cd fdel
pip install -e .

# From PyPI (after publishing)
pip install fdel
