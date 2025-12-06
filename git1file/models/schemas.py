from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
from pathlib import Path


class OutputFormat(str, Enum):
    XML = "xml"
    PLAIN = "plain"
    JSON = "json"


class ScanMode(str, Enum):
    FULL = "full"
    SMART = "smart"


class LanguageStats(BaseModel):
    name: str
    files: int = 0
    characters: int = 0


class FileInfo(BaseModel):
    path: str
    content: Optional[str] = None
    size: int
    language: Optional[str] = None
    is_binary: bool = False
    is_ignored: bool = False


class RepositoryMetadata(BaseModel):
    name: str
    path: str
    total_files: int = 0
    total_characters: int = 0
    languages: List[LanguageStats] = Field(default_factory=list)
    git_branch: Optional[str] = None
    git_commit: Optional[str] = None
    is_git_repo: bool = False


class RepositoryAnalysis(BaseModel):
    metadata: RepositoryMetadata
    files: List[FileInfo]


class IgnoreConfig(BaseModel):
    patterns: List[str] = Field(default_factory=list)
    use_gitignore: bool = True
    use_default_patterns: bool = True


class IncludeConfig(BaseModel):
    max_file_size: str = "1MB"
    max_total_files: int = 50000
    max_total_chars: int = 500_000_000
    binary_detection: bool = True


class OutputConfig(BaseModel):
    format: OutputFormat = OutputFormat.XML
    compress: bool = True
    mode: ScanMode = ScanMode.SMART


class ConfigSchema(BaseModel):
    output: OutputConfig = Field(default_factory=OutputConfig)
    ignore: IgnoreConfig = Field(default_factory=IgnoreConfig)
    include: IncludeConfig = Field(default_factory=IncludeConfig)