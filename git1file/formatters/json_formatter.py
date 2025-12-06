import json
from typing import Any, Dict
from git1file.models.schemas import RepositoryAnalysis


def format_json(analysis: RepositoryAnalysis) -> str:
    """
    форматируем репо под JSON....
    """
    output: Dict[str, Any] = {
        "name": analysis.metadata.name,
        "path": str(analysis.metadata.path),
        "metadata": {
            "total_files": analysis.metadata.total_files,
            "total_characters": analysis.metadata.total_characters,
            "is_git_repo": analysis.metadata.is_git_repo,
            "languages": [
                {
                    "name": lang.name,
                    "files": lang.files,
                    "chars": lang.chars
                }
                for lang in analysis.metadata.languages
            ]
        },
        "files": []
    }

    #добавляем метаданные
    if analysis.metadata.is_git_repo:
        output["metadata"]["git_branch"] = analysis.metadata.git_branch
        output["metadata"]["git_commit"] = analysis.metadata.git_commit

    # Файлики
    for file_info in analysis.files:
        file_data = {
            "path": file_info.path,
            "size": file_info.size,
            "is_binary": file_info.is_binary,
            "language": file_info.language
        }

        # медиа нам нахой не нада.
        if file_info.content and not file_info.is_binary:
            file_data["content"] = file_info.content

        output["files"].append(file_data)

    return json.dumps(output, indent=2, ensure_ascii=False)


def format_json_compact(analysis: RepositoryAnalysis) -> str:
    """
   в правильную структуру
    """
    output = {
        "files": [
            {
                "path": file_info.path,
                "content": file_info.content
            }
            for file_info in analysis.files
            if file_info.content and not file_info.is_binary
        ]
    }

    return json.dumps(output, separators=(',', ':'), ensure_ascii=False)


def format_json_lines(analysis: RepositoryAnalysis) -> str:
    """
   в единый джсончик
    """
    lines = []


    meta_line = {
        "type": "metadata",
        "name": analysis.metadata.name,
        "total_files": analysis.metadata.total_files
    }
    lines.append(json.dumps(meta_line, ensure_ascii=False))


    for file_info in analysis.files:
        if file_info.content and not file_info.is_binary:
            file_line = {
                "type": "file",
                "path": file_info.path,
                "content": file_info.content
            }
            lines.append(json.dumps(file_line, ensure_ascii=False))

    return "\n".join(lines)