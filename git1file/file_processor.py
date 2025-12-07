import mimetypes
from pathlib import Path
from typing import List, Optional, Set, Tuple
import fnmatch

from .models.schemas import FileInfo, IncludeConfig, IgnoreConfig, ScanMode
from .config import SMART_IGNORE_PATTERNS, FULL_IGNORE_PATTERNS


def is_binary_file(file_path: Path) -> bool:
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and not mime_type.startswith('text/'):
        return True
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            chunk.decode('utf-8')
            return False
    except UnicodeDecodeError:
        return True


def should_ignore_path(
        path: Path,
        ignore_config: IgnoreConfig,
        scan_mode: ScanMode,
        gitignore_patterns: Optional[Set[str]] = None
) -> bool:
    path_name = path.name
    relative_path_str = path.as_posix()
    path_parts = set(path.parts[:-1])

    def check_pattern(pattern: str) -> bool:
        if pattern.endswith('/'):
            dir_name = pattern.rstrip('/')
            if dir_name in path_parts:
                return True
            if '*' in dir_name or '?' in dir_name:
                for part in path_parts:
                    if fnmatch.fnmatch(part, dir_name):
                        return True
            return False

        if fnmatch.fnmatch(path_name, pattern):
            return True
        if fnmatch.fnmatch(relative_path_str, pattern):
            return True
        return False

    if ignore_config.use_default_patterns:
        patterns = SMART_IGNORE_PATTERNS if scan_mode == ScanMode.SMART else FULL_IGNORE_PATTERNS
        for pattern in patterns:
            if check_pattern(pattern):
                return True

    for pattern in ignore_config.patterns:
        if check_pattern(pattern):
            return True

    if gitignore_patterns and ignore_config.use_gitignore:
        for pattern in gitignore_patterns:
            if check_pattern(pattern):
                return True

    return False


def load_gitignore_patterns(repo_path: Path) -> Set[str]:
    gitignore_path = repo_path / ".gitignore"
    patterns = set()
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.add(line)
    return patterns


def get_file_language(file_path: Path) -> Optional[str]:
    ext_to_lang = {
        '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
        '.jsx': 'jsx', '.tsx': 'tsx', '.java': 'java', '.cpp': 'cpp',
        '.c': 'c', '.h': 'c', '.hpp': 'cpp', '.cs': 'csharp',
        '.go': 'go', '.rs': 'rust', '.rb': 'ruby', '.php': 'php',
        '.swift': 'swift', '.kt': 'kotlin', '.scala': 'scala',
        '.html': 'html', '.css': 'css', '.scss': 'scss', '.sass': 'sass',
        '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml', '.xml': 'xml',
        '.md': 'markdown', '.sql': 'sql', '.sh': 'bash', '.bash': 'bash',
        '.zsh': 'zsh', '.fish': 'fish', '.ps1': 'powershell',
        '.dockerfile': 'dockerfile', '.toml': 'toml', '.ini': 'ini',
        '.cfg': 'config', '.conf': 'config', '.log': 'log', '.txt': 'text'
    }
    return ext_to_lang.get(file_path.suffix.lower())


def read_file_content(file_path: Path, max_size_bytes: int) -> Optional[str]:
    try:
        if file_path.stat().st_size > max_size_bytes:
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def parse_size_string(size_str: str) -> int:
    multipliers = {
        'GB': 1024 ** 3, 'MB': 1024 ** 2, 'KB': 1024, 'B': 1
    }
    size_str = size_str.upper().strip()
    for suffix in ['GB', 'MB', 'KB', 'B']:
        if size_str.endswith(suffix):
            try:
                number = int(size_str[:-len(suffix)])
                return number * multipliers[suffix]
            except ValueError:
                continue
    return 1024 * 1024


def scan_repository(
        repo_path: Path,
        ignore_config: IgnoreConfig,
        include_config: IncludeConfig,
        scan_mode: ScanMode
) -> Tuple[List[FileInfo], List[FileInfo]]:
    """
    Сканирует репозиторий и возвращает два списка:
    - Обычные файлы
    - Markdown файлы (отдельно)
    """
    max_size = parse_size_string(include_config.max_file_size)
    gitignore_patterns = load_gitignore_patterns(repo_path) if ignore_config.use_gitignore else None
    file_infos = []
    markdown_files = []

    for path in repo_path.rglob('*'):
        if path.is_file():
            try:
                relative_path = path.relative_to(repo_path)
            except ValueError:
                continue

            if should_ignore_path(relative_path, ignore_config, scan_mode, gitignore_patterns):
                continue

            is_binary = is_binary_file(path) if include_config.binary_detection else False
            content = None if is_binary else read_file_content(path, max_size)
            language = get_file_language(path)

            file_info = FileInfo(
                path=relative_path.as_posix(),
                content=content,
                size=path.stat().st_size,
                language=language,
                is_binary=is_binary,
                is_ignored=False
            )

            # Разделяем markdown и остальные файлы
            if language == 'markdown':
                markdown_files.append(file_info)
            else:
                file_infos.append(file_info)

    return file_infos, markdown_files