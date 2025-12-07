# 🗜️ Git1File

> **Convert any Git repository into a single AI-friendly file**

Transform entire codebases into structured formats optimized for Large Language Models. Perfect for code analysis, documentation generation, and AI-assisted development.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

- 📦 **Multiple Output Formats** - Plain text, XML, JSON
- 🚫 **Smart Filtering** - Automatically excludes binaries, dependencies, and service files
- 📝 **Markdown Handling** - Separate markdown files to save tokens (optional inclusion)
- ⚡ **Fast Processing** - Parallel file scanning and analysis
- 🌐 **Web Interface** - Beautiful UI for easy repository conversion
- 🔌 **REST API** - Programmatic access for automation
- 🔒 **Private Repos** - Works with local paths and remote URLs
- 📊 **Statistics** - Language breakdown, file counts, and size estimates

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/git1file.git
cd git1file

# Install dependencies
pip install -e .
```

### Command Line Usage

```bash
# Analyze a local repository
python -m git1file.cli /path/to/repo

# Analyze a remote repository
python -m git1file.cli https://github.com/user/repo

# Specify output format
python -m git1file.cli /path/to/repo --format xml

# Save to file
python -m git1file.cli /path/to/repo --output result.txt

# Include markdown files
python -m git1file.cli /path/to/repo --include-markdown

# Save markdown separately
python -m git1file.cli /path/to/repo --markdown-output docs.txt
```

### Web Interface

```bash
# Start the server
uvicorn git1file.main:app --reload --port 8000

# Open your browser
# Navigate to: http://localhost:8000
```

The web interface provides:
- 🎯 Simple form to enter repository URL or path
- 📊 Real-time statistics preview
- 💾 One-click download of results
- 📋 Copy to clipboard functionality
- 🎨 Beautiful dark theme optimized for developers

---

## 📖 Usage Examples

### CLI Examples

```bash
# Smart mode (default) - excludes common service files
python -m git1file.cli ./myproject --mode smart

# Full mode - includes everything except binaries
python -m git1file.cli ./myproject --mode full

# Export only markdown files
python -m git1file.cli ./myproject --markdown-only

# JSON output for programmatic processing
python -m git1file.cli ./myproject --format json --output data.json
```

### API Examples

**Get repository analysis:**

```bash
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "/path/to/repo",
    "format": "plain",
    "mode": "smart",
    "include_markdown": false
  }'
```

**Get markdown files only:**

```bash
curl -X POST "http://localhost:8000/api/v1/ingest/markdown" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "https://github.com/user/repo",
    "format": "plain"
  }'
```

**Get repository statistics:**

```bash
curl "http://localhost:8000/api/v1/stats?source=/path/to/repo&mode=smart"
```

---

## ⚙️ Configuration

Create a `.git1file.yaml` in your repository root to customize behavior:

```yaml
output:
  format: plain          # plain, xml, or json
  compress: true         # Enable compression
  mode: smart           # smart or full

ignore:
  patterns:
    - "*.log"
    - "temp/"
  use_gitignore: true
  use_default_patterns: true

include:
  max_file_size: "5MB"
  max_total_files: 50000
  max_total_chars: 500000000
  binary_detection: true
  include_markdown: false
```

### Default Ignore Patterns (Smart Mode)

Smart mode automatically excludes:
- **Binaries**: `*.exe`, `*.dll`, `*.so`, `*.dylib`
- **Images**: `*.png`, `*.jpg`, `*.gif`, `*.svg`
- **Media**: `*.mp4`, `*.mp3`, `*.wav`
- **Documents**: `*.pdf`, `*.doc`, `*.xls`
- **Archives**: `*.zip`, `*.tar`, `*.gz`
- **Compiled**: `*.pyc`, `*.class`, `*.o`
- **Dependencies**: `node_modules/`, `__pycache__/`, `.venv/`
- **IDE**: `.idea/`, `.vscode/`
- **Lock files**: `package-lock.json`, `yarn.lock`, `poetry.lock`

---

## 📊 Output Formats

### Plain Text (Recommended)

```
================================================================================
REPOSITORY: git1file
PATH: /path/to/git1file
TOTAL FILES: 17
TOTAL CHARACTERS: 61695
...

--------------------------------------------------------------------------------
FILE: cli.py
LANGUAGE: python
SIZE: 4104 bytes
----------------------------------------
import sys
import argparse
...
```

**Benefits**: 16%+ fewer tokens than XML, easy to read

### XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<repository name="git1file" path="/path/to/git1file">
  <metadata>
    <total_files>17</total_files>
    ...
  </metadata>
  <files>
    <file path="cli.py" language="python">
      <content><![CDATA[...]]></content>
    </file>
  </files>
</repository>
```

**Benefits**: Structured, easy to parse programmatically

### JSON

```json
{
  "name": "git1file",
  "metadata": {
    "total_files": 17,
    "languages": [...]
  },
  "files": [
    {
      "path": "cli.py",
      "language": "python",
      "content": "..."
    }
  ]
}
```

**Benefits**: Native JavaScript support, API-friendly

---

## 🎯 Use Cases

- **AI Code Review** - Feed entire codebases to Claude or GPT
- **Documentation** - Generate comprehensive project docs
- **Code Analysis** - Analyze patterns across multiple files
- **Migration Planning** - Understand legacy code structure
- **Learning** - Study how projects are organized
- **Backup** - Create readable snapshots of your code

---

## 🛠️ API Reference

### Endpoints

| Endpoint                  | Method | Description                       |
|---------------------------|--------|-----------------------------------|
| `/api/v1/ingest`          | POST   | Convert repository to single file |
| `/api/v1/ingest/markdown` | POST   | Get only markdown files           |
| `/api/v1/stats`           | GET    | Get repository statistics         |
| `/api/v1/config/template` | GET    | Get configuration template        |
| `/health`                 | GET    | Health check                      |

### Request Schema

```typescript
{
  source: string;           // Local path or Git URL
  format: "plain" | "xml" | "json";
  mode: "smart" | "full";
  compress: boolean;
  include_markdown: boolean;
}
```

---

## 📝 CLI Options

```
usage: python -m git1file.cli [-h] [--format {xml,plain,json}] 
                               [--mode {full,smart}] [--output OUTPUT]
                               [--include-markdown] [--markdown-only]
                               [--markdown-output MARKDOWN_OUTPUT]
                               source

positional arguments:
  source                Local path or remote URL

optional arguments:
  --format              Output format (default: plain)
  --mode                Scan mode (default: smart)
  --output, -o          Output file
  --include-markdown    Include .md files in main output
  --markdown-only       Output only markdown files
  --markdown-output     Separate file for markdown
```
---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- Uses [GitPython](https://gitpython.readthedocs.io/) for Git operations
- Inspired by the need to feed codebases to LLMs efficiently

---



<div align="center">

**Made with Stupid me for developers working**

⭐ Star us on GitHub if this project helped you!

</div>