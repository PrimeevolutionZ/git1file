# git1file/config.py
import yaml
from pathlib import Path
from typing import Optional
from .models.schemas import ConfigSchema, ScanMode

SMART_IGNORE_PATTERNS = [
    "*.exe", "*.dll", "*.so", "*.dylib", "*.bin", "*.dmg", "*.iso", "*.img",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.ico", "*.bmp", "*.webp",
    "*.mp4", "*.avi", "*.mov", "*.wmv", "*.flv", "*.mkv",
    "*.mp3", "*.wav", "*.flac", "*.aac", "*.ogg",
    "*.pdf", "*.doc", "*.docx", "*.xls", "*.xlsx", "*.ppt", "*.pptx", "*.odt",
    "*.zip", "*.tar", "*.gz", "*.rar", "*.7z", "*.bz2", "*.xz", "*.tgz",
    "*.pyc", "*.class", "*.o", "*.obj", "*.pyd", "*.pyo",
    "node_modules/", "__pycache__/", ".git/", ".venv/", "venv/",
    ".idea/", ".vscode/", "*.swp", "*.swo", "*~", ".DS_Store", "Thumbs.db",
    "*.log", "*.cache", "*.tmp", "*.temp", "*.pid", "*.seed", "*.lock",
    "package-lock.json", "yarn.lock", "poetry.lock", "Pipfile.lock",
    "*.map", "*.min.js", "*.min.css", "*.bak", "*.backup",
]

FULL_IGNORE_PATTERNS = [
    "*.exe", "*.dll", "*.zip", "*.tar", "*.gz", "*.rar",
    ".git1file-output.*", "git1file-output.*",
]


def load_config(config_path: Optional[Path] = None) -> ConfigSchema:
    """Load configuration with plain format as default."""
    if config_path is None:
        config_path = Path(".git1file.yaml")

    # 🔧 FIX: Changed default format from "xml" to "plain"
    config_dict = {
        "output": {"format": "plain", "compress": True, "mode": "smart"},
        "ignore": {
            "patterns": SMART_IGNORE_PATTERNS,
            "use_gitignore": True,
            "use_default_patterns": True
        },
        "include": {
            "max_file_size": "5MB",  # 🔧 FIX: Consistent with actual usage
            "max_total_files": 50000,
            "max_total_chars": 500000000,
            "binary_detection": True
        }
    }

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            loaded_config = yaml.safe_load(f) or {}

        def merge_dicts(base, update):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dicts(base[key], value)
                else:
                    base[key] = value

        merge_dicts(config_dict, loaded_config)

    return ConfigSchema(**config_dict)


def get_config_for_repo(repo_path: Path) -> ConfigSchema:
    """Get config for repository, searching parent directories."""
    current = repo_path.resolve()
    for parent in [current] + list(current.parents):
        config_path = parent / ".git1file.yaml"
        if config_path.exists():
            return load_config(config_path)
    return load_config()