from ..models.schemas import RepositoryAnalysis


def format_plain(analysis: RepositoryAnalysis) -> str:
    """
    Формат текста. удобненька.....
    """
    lines = []

    # Метаданные репозитория
    lines.append("=" * 80)
    lines.append(f"REPOSITORY: {analysis.metadata.name}")
    lines.append(f"PATH: {analysis.metadata.path}")
    lines.append(f"TOTAL FILES: {analysis.metadata.total_files}")
    lines.append(f"TOTAL CHARACTERS: {analysis.metadata.total_characters}")

    if analysis.metadata.is_git_repo:
        lines.append(f"GIT BRANCH: {analysis.metadata.git_branch}")
        lines.append(f"GIT COMMIT: {analysis.metadata.git_commit}")

    # Language statistics section
    if analysis.metadata.languages:
        lines.append("\nLANGUAGE STATISTICS:")
        lines.append("-" * 80)
        for lang in analysis.metadata.languages:
            lines.append(f"  {lang.name}: {lang.files} files, {lang.chars} chars")


    lines.append("\n" + "=" * 80)
    lines.append("FILE CONTENTS")
    lines.append("=" * 80 + "\n")

    # обработка
    for file_info in analysis.files:
        # Пропускаем если дичь
        if file_info.is_binary or file_info.content is None:
            lines.append(f"# BINARY/LARGE FILE: {file_info.path}")
            continue

        # метаданные
        lines.append("-" * 80)
        lines.append(f"FILE: {file_info.path}")
        if file_info.language:
            lines.append(f"LANGUAGE: {file_info.language}")
        lines.append(f"SIZE: {file_info.size} bytes")
        lines.append("-" * 40)

        # файл
        lines.append(file_info.content)
        lines.append("\n")

    return "\n".join(lines)


def format_compact(analysis: RepositoryAnalysis) -> str:
    """
    Великое единение
    """
    lines = []

    for file_info in analysis.files:
        if file_info.is_binary or file_info.content is None:
            continue

        lines.append(f"// FILE: {file_info.path}")
        lines.append(file_info.content)
        lines.append("\n")

    return "\n".join(lines)