import yaml
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from .models.schemas import ConfigSchema

DEFAULT_IGNORE_PATTERNS = [
    "*.exe", "*.dll", "*.so", "*.dylib",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg",
    "*.pdf", "*.doc", "*.docx",
    "*.zip", "*.tar", "*.gz", "*.rar",
    "*.pyc", "*.class",
    "node_modules/", "__pycache__/", ".git/", ".venv/",
]


def load_config(config_path: Optional[Path] = None) -> ConfigSchema:
    if config_path is None:
        config_path = Path(".git1file.yaml")

    config_dict = {
        "output": {"format": "xml", "compress": True},
        "ignore": {
            "patterns": DEFAULT_IGNORE_PATTERNS,
            "use_gitignore": True,
            "use_default_patterns": True
        },
        "include": {
            "max_file_size": "5MB",
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
    current = repo_path.resolve()
    for parent in [current] + list(current.parents):
        config_path = parent / ".git1file.yaml"
        if config_path.exists():
            return load_config(config_path)
    return load_config()