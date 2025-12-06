import sys
import argparse
from pathlib import Path
from git1file.analyzer import analyze_repository
from git1file.config import load_config
from git1file.git_service import process_source
from git1file.formatters.plain_formatter import format_plain
from git1file.formatters.xml_formatter import format_xml
from git1file.formatters.json_formatter import format_json
from git1file.models.schemas import OutputFormat


def main():
    parser = argparse.ArgumentParser(description="Convert Git repos to single file")
    parser.add_argument("source", help="Local path or remote URL")
    parser.add_argument("--format", choices=["xml", "plain", "json"], default="xml")
    parser.add_argument("--output", "-o", help="Output file (stdout if not specified)")

    args = parser.parse_args()

    try:
        repo_path, is_temp, _ = process_source(args.source)
        config = load_config(repo_path / ".git1file.yaml")
        config.output.format = OutputFormat(args.format)

        analysis = analyze_repository(repo_path, config)

        if args.format == "xml":
            result = format_xml(analysis)
        elif args.format == "json":
            result = format_json(analysis)
        else:
            result = format_plain(analysis)

        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
        else:
            print(result)

        # Очистка
        if is_temp:
            from git1file.git_service import cleanup_temp_repo
            cleanup_temp_repo(repo_path, is_temp)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()