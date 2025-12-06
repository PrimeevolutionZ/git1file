from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import tempfile
import shutil
import yaml
import logging

from .models.schemas import OutputFormat
from .analyzer import analyze_repository, get_quick_stats
from .git_service import process_source, cleanup_temp_repo
from .config import load_config, ConfigSchema
from .formatters.plain_formatter import format_plain
from .formatters.xml_formatter import format_xml
from .formatters.json_formatter import format_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Git1File API",
    description="Convert Git repositories into single files for LLMs",
    version="0.1.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="git1file/ui/static"), name="static")
templates = Jinja2Templates(directory="git1file/ui/templates")

MAX_TOTAL_FILES = 50000
MAX_TOTAL_CHARS = 500_000_000


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "0.1.0"}


@app.post("/api/v1/ingest")
async def ingest_repository(
        background_tasks: BackgroundTasks,
        source: str = Query(..., description="Local path or git URL"),
        format: OutputFormat = Query(OutputFormat.PLAIN, description="Output format"),
        compress: bool = Query(True, description="Include compression hints")
):
    try:
        logger.info(f"Processing source: {source}")
        repo_path, is_temp, remote_url = process_source(source)

        if is_temp:
            background_tasks.add_task(cleanup_temp_repo, repo_path, is_temp)

        config = load_config(repo_path / ".git1file.yaml")
        config.output.format = format
        config.output.compress = compress

        analysis = analyze_repository(repo_path, config)

        # Validate limits
        if analysis.metadata.total_files > MAX_TOTAL_FILES:
            raise HTTPException(status_code=413, detail=f"Too many files: {analysis.metadata.total_files} > {MAX_TOTAL_FILES}")
        if analysis.metadata.total_characters > MAX_TOTAL_CHARS:
            raise HTTPException(status_code=413, detail="Repository too large")

        if format == OutputFormat.XML:
            content = format_xml(analysis)
            media_type = "application/xml"
        elif format == OutputFormat.JSON:
            content = format_json(analysis)
            media_type = "application/json"
        else:
            content = format_plain(analysis)
            media_type = "text/plain"

        return Response(content=content, media_type=media_type)

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/stats")
async def get_stats(
        background_tasks: BackgroundTasks,
        source: str = Query(..., description="Local path or git URL")
):
    try:
        repo_path, is_temp, _ = process_source(source)
        if is_temp:
            background_tasks.add_task(cleanup_temp_repo, repo_path, is_temp)

        config = load_config(repo_path / ".git1file.yaml")
        analysis = analyze_repository(repo_path, config)
        return get_quick_stats(analysis)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/config/template")
def get_config_template():
    template_config = ConfigSchema()
    return yaml.safe_dump(template_config.dict(), default_flow_style=False)


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})