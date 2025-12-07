import sys
import argparse
from pathlib import Path
from git1file.analyzer import analyze_repository
from git1file.config import load_config
from git1file.git_service import process_source, cleanup_temp_repo
from git1file.formatters.plain_formatter import format_plain, format_plain_markdown
from git1file.formatters.xml_formatter import format_xml, format_xml_markdown
from git1file.formatters.json_formatter import format_json, format_json_markdown
from git1file.models.schemas import OutputFormat, ScanMode


def main():
    parser = argparse.ArgumentParser(
        description="Convert Git repos to single file",
        epilog="Default format is 'plain'. Markdown files are excluded by default to save tokens."
    )
    parser.add_argument("source", help="Local path or remote URL")
    parser.add_argument("--format", choices=["xml", "plain", "json"], default="plain",
                        help="Output format (default: plain)")
    parser.add_argument("--mode", choices=["full", "smart"], default="smart",
                        help="Scan mode: 'full' includes all files, 'smart' excludes service files")
    parser.add_argument("--output", "-o", help="Output file (stdout if not specified)")

    # NEW: Markdown options
    parser.add_argument("--include-markdown", action="store_true",
                        help="Include .md files in the main output (excluded by default)")
    parser.add_argument("--markdown-only", action="store_true",
                        help="Output only markdown files")
    parser.add_argument("--markdown-output", help="Separate output file for markdown files")

    args = parser.parse_args()

    try:
        repo_path, is_temp, _ = process_source(args.source)
        config = load_config(repo_path / ".git1file.yaml")
        config.output.format = OutputFormat(args.format)
        config.output.mode = ScanMode(args.mode)
        config.include.include_markdown = args.include_markdown

        analysis = analyze_repository(repo_path, config)

        # Handle markdown-only mode
        if args.markdown_only:
            if args.format == "xml":
                result = format_xml_markdown(analysis)
            elif args.format == "json":
                result = format_json_markdown(analysis)
            else:
                result = format_plain_markdown(analysis)
        else:
            # Normal output
            if args.format == "xml":
                result = format_xml(analysis)
            elif args.format == "json":
                result = format_json(analysis)
            else:
                result = format_plain(analysis)

        # Output main result
        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
            print(f"✅ Written to {args.output}")
        else:
            print(result)

        # Output markdown separately if requested
        if args.markdown_output and not args.markdown_only:
            if args.format == "xml":
                md_result = format_xml_markdown(analysis)
            elif args.format == "json":
                md_result = format_json_markdown(analysis)
            else:
                md_result = format_plain_markdown(analysis)

            Path(args.markdown_output).write_text(md_result, encoding="utf-8")
            print(f"📚 Markdown written to {args.markdown_output}")

        # Show stats
        if analysis.metadata.markdown_files > 0 and not args.include_markdown and not args.markdown_only:
            print(f"\n💡 {analysis.metadata.markdown_files} markdown files excluded "
                  f"({analysis.metadata.markdown_characters / 1024:.1f} KB)", file=sys.stderr)
            print(f"   Use --include-markdown to include them or --markdown-output to save separately",
                  file=sys.stderr)

        if is_temp:
            cleanup_temp_repo(repo_path, is_temp)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()