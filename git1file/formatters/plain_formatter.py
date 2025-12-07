# plain_formatter.py
from ..models.schemas import RepositoryAnalysis


def format_plain(analysis: RepositoryAnalysis) -> str:
    """Формат текста без markdown файлов"""
    lines = []

    lines.append("=" * 80)
    lines.append(f"REPOSITORY: {analysis.metadata.name}")
    lines.append(f"PATH: {analysis.metadata.path}")
    lines.append(f"TOTAL FILES: {analysis.metadata.total_files}")
    lines.append(f"TOTAL CHARACTERS: {analysis.metadata.total_characters}")

    if analysis.metadata.markdown_files > 0:
        lines.append(
            f"MARKDOWN FILES (EXCLUDED): {analysis.metadata.markdown_files} files, {analysis.metadata.markdown_characters} chars")

    if analysis.metadata.is_git_repo:
        lines.append(f"GIT BRANCH: {analysis.metadata.git_branch}")
        lines.append(f"GIT COMMIT: {analysis.metadata.git_commit}")

    if analysis.metadata.languages:
        lines.append("\nLANGUAGE STATISTICS:")
        lines.append("-" * 80)
        for lang in analysis.metadata.languages:
            lines.append(f"  {lang.name}: {lang.files} files, {lang.characters} chars")

    lines.append("\n" + "=" * 80)
    lines.append("FILE CONTENTS")
    lines.append("=" * 80 + "\n")

    for file_info in analysis.files:
        if file_info.is_binary or file_info.content is None:
            lines.append(f"# BINARY/LARGE FILE: {file_info.path}")
            continue

        lines.append("-" * 80)
        lines.append(f"FILE: {file_info.path}")
        if file_info.language:
            lines.append(f"LANGUAGE: {file_info.language}")
        lines.append(f"SIZE: {file_info.size} bytes")
        lines.append("-" * 40)
        lines.append(file_info.content)
        lines.append("\n")

    return "\n".join(lines)


def format_plain_markdown(analysis: RepositoryAnalysis) -> str:
    """Формат только для markdown файлов"""
    lines = []

    lines.append("=" * 80)
    lines.append(f"MARKDOWN DOCUMENTATION: {analysis.metadata.name}")
    lines.append(f"TOTAL MARKDOWN FILES: {len(analysis.markdown_files)}")
    lines.append("=" * 80 + "\n")

    for file_info in analysis.markdown_files:
        if file_info.content:
            lines.append("-" * 80)
            lines.append(f"FILE: {file_info.path}")
            lines.append(f"SIZE: {file_info.size} bytes")
            lines.append("-" * 40)
            lines.append(file_info.content)
            lines.append("\n")

    return "\n".join(lines)


# Добавить аналогичные функции в xml_formatter.py и json_formatter.py
# xml_formatter.py
def format_xml_markdown(analysis: RepositoryAnalysis) -> str:
    """XML формат для markdown файлов"""
    from xml.sax.saxutils import escape

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<markdown_documentation name="{escape(analysis.metadata.name)}">',
        f'  <total_files>{len(analysis.markdown_files)}</total_files>',
        '  <files>'
    ]

    for file_info in analysis.markdown_files:
        if file_info.content:
            safe_content = file_info.content.replace(']]>', ']]]]><![CDATA[>')
            lines.append(f'    <file path="{escape(file_info.path)}" size="{file_info.size}">')
            lines.append(f'      <content><![CDATA[{safe_content}]]></content>')
            lines.append('    </file>')

    lines.append('  </files>')
    lines.append('</markdown_documentation>')

    return '\n'.join(lines)


# json_formatter.py
def format_json_markdown(analysis: RepositoryAnalysis) -> str:
    """JSON формат для markdown файлов"""
    import json

    output = {
        "name": analysis.metadata.name,
        "total_markdown_files": len(analysis.markdown_files),
        "files": [
            {
                "path": f.path,
                "size": f.size,
                "content": f.content
            }
            for f in analysis.markdown_files
            if f.content
        ]
    }

    return json.dumps(output, indent=2, ensure_ascii=False)