import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from typing import Dict, Any
from ..models.schemas import RepositoryAnalysis, LanguageStats, FileInfo


def format_xml(analysis: RepositoryAnalysis) -> str:
    """Safe XML format with proper CDATA handling.
    """
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<repository name="{escape(analysis.metadata.name)}" path="{escape(str(analysis.metadata.path))}">',
        '  <metadata>',
        f'    <total_files>{analysis.metadata.total_files}</total_files>',
        f'    <total_characters>{analysis.metadata.total_characters}</total_characters>',
    ]

    if analysis.metadata.is_git_repo:
        lines.extend([
            f'    <git_branch>{escape(analysis.metadata.git_branch or "")}</git_branch>',
            f'    <git_commit>{escape(analysis.metadata.git_commit or "")}</git_commit>',
            '    <is_git_repo>true</is_git_repo>'
        ])
    else:
        lines.append('    <is_git_repo>false</is_git_repo>')

    if analysis.metadata.languages:
        lines.append('    <languages>')
        for lang in analysis.metadata.languages:
            lines.append(
                f'      <language name="{escape(lang.name)}" '
                f'files="{lang.files}" chars="{lang.characters}"/>'
            )
        lines.append('    </languages>')

    lines.append('  </metadata>')
    lines.append('  <files>')

    for file_info in analysis.files:
        attrs = f'path="{escape(file_info.path)}" size="{file_info.size}"'
        if file_info.language:
            attrs += f' language="{escape(file_info.language)}"'
        attrs += f' is_binary="{str(file_info.is_binary).lower()}"'

        lines.append(f'    <file {attrs}>')

        if file_info.content and not file_info.is_binary:
            safe_content = file_info.content.replace(']]>', ']]]]><![CDATA[>')
            lines.append(f'      <content><![CDATA[{safe_content}]]></content>')

        lines.append('    </file>')

    lines.append('  </files>')
    lines.append('</repository>')

    return '\n'.join(lines)


def format_xml_markdown(analysis: RepositoryAnalysis) -> str:
    """XML формат для markdown файлов"""
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


def validate_xml_output(xml_string: str) -> bool:
    """Validate that generated XML is well-formed.

    Returns True if valid, False otherwise.
    Use this in tests to ensure CDATA escaping works correctly.
    """
    try:
        ET.fromstring(xml_string)
        return True
    except ET.ParseError:
        return False