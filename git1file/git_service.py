import tempfile
import shutil
from pathlib import Path
from typing import Union, Optional, Tuple
import re
from git import Repo, InvalidGitRepositoryError


def is_local_path(source: str) -> bool:
    url_patterns = [r'^https?://', r'^git@', r'^ssh://', r'^git://']
    for pattern in url_patterns:
        if re.match(pattern, source):
            return False
    return True


def is_git_repo_path(path: Path) -> bool:
    try:
        Repo(path, search_parent_directories=True)
        return True
    except InvalidGitRepositoryError:
        return False


def get_repo_info(repo_path: Path) -> Tuple[Optional[str], Optional[str]]:
    try:
        repo = Repo(repo_path, search_parent_directories=True)
        branch = repo.active_branch.name if repo.active_branch else None
        commit = repo.head.commit.hexsha[:8] if repo.head else None
        return branch, commit
    except:
        return None, None


def clone_remote_repo(repo_url: str, temp_dir: Path) -> Path:
    try:
        repo_name = re.split(r'[:/]', repo_url.rstrip('/').replace('.git', ''))[-1]
        clone_path = temp_dir / repo_name
        Repo.clone_from(repo_url, clone_path)
        return clone_path
    except Exception as e:
        raise RuntimeError(f"Failed to clone repository {repo_url}: {str(e)}")


def process_source(source: str) -> Tuple[Path, bool, Optional[str]]:
    if is_local_path(source):
        repo_path = Path(source).resolve()
        if not repo_path.exists():
            raise ValueError(f"Path does not exist: {source}")
        return repo_path, False, None
    else:
        temp_dir = Path(tempfile.mkdtemp(prefix="git1file_"))
        try:
            repo_path = clone_remote_repo(source, temp_dir)
            return repo_path, True, source
        except Exception:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise


def cleanup_temp_repo(repo_path: Path, is_temp: bool):
    """проверяем префикс временной директории"""
    if is_temp and repo_path.exists() and "git1file_" in str(repo_path.parent):
        shutil.rmtree(repo_path.parent, ignore_errors=True)


def detect_repo_type(source: str) -> str:
    if is_local_path(source):
        path = Path(source).resolve()
        if is_git_repo_path(path):
            return "local_git"
        else:
            return "local_directory"
    else:
        if source.startswith('https://github.com'):
            return 'github'
        elif source.startswith('git@github.com'):
            return 'github_ssh'
        elif source.startswith('https://gitlab.com'):
            return 'gitlab'
        elif source.startswith('git@gitlab.com'):
            return 'gitlab_ssh'
        else:
            return 'generic_git'