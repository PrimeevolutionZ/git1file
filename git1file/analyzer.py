from pathlib import Path
from typing import List
import logging
from .models.schemas import (
    RepositoryAnalysis,
    RepositoryMetadata,
    LanguageStats,
    FileInfo,
    ConfigSchema
)
from .file_processor import scan_repository
from .git_service import get_repo_info

logger = logging.getLogger(__name__)


def analyze_repository(repo_path: Path, config: ConfigSchema) -> RepositoryAnalysis:
    logger.info(f"Starting analysis of {repo_path}")

    file_infos, markdown_files = scan_repository(
        repo_path, config.ignore, config.include, config.output.mode
    )

    # Если include_markdown=True, добавляем markdown к основным файлам
    if config.include.include_markdown:
        all_files = file_infos + markdown_files
        markdown_in_analysis = []
    else:
        all_files = file_infos
        markdown_in_analysis = markdown_files

    total_files = len(all_files)
    total_chars = sum(f.size for f in all_files)

    # Статистика markdown
    markdown_count = len(markdown_files)
    markdown_chars = sum(f.size for f in markdown_files)

    if total_files > 50000:
        logger.warning(f"Large repository: {total_files} files")

    lang_stats = {}
    for file_info in all_files:
        if file_info.language:
            lang = file_info.language
            lang_stats.setdefault(lang, {"files": 0, "chars": 0})
            lang_stats[lang]["files"] += 1
            lang_stats[lang]["chars"] += file_info.size

    languages = sorted(
        [
            LanguageStats(name=lang, files=stats["files"], characters=stats["chars"])
            for lang, stats in lang_stats.items()
        ],
        key=lambda x: x.files,
        reverse=True
    )

    branch, commit = get_repo_info(repo_path)

    metadata = RepositoryMetadata(
        name=repo_path.name,
        path=str(repo_path.resolve()),
        total_files=total_files,
        total_characters=total_chars,
        languages=languages,
        git_branch=branch,
        git_commit=commit,
        is_git_repo=branch is not None,
        markdown_files=markdown_count,
        markdown_characters=markdown_chars
    )

    logger.info(f"Analysis complete: {total_files} files, {markdown_count} markdown files")
    return RepositoryAnalysis(
        metadata=metadata,
        files=all_files,
        markdown_files=markdown_in_analysis
    )


def get_quick_stats(analysis: RepositoryAnalysis) -> dict:
    return {
        "name": analysis.metadata.name,
        "total_files": analysis.metadata.total_files,
        "total_characters": analysis.metadata.total_characters,
        "languages": [{"name": lang.name, "files": lang.files} for lang in analysis.metadata.languages],
        "git_branch": analysis.metadata.git_branch,
        "git_commit": analysis.metadata.git_commit,
        "markdown_files": analysis.metadata.markdown_files,
        "markdown_characters": analysis.metadata.markdown_characters
    }