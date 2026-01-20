"""Configuration management for Gemma Translator CLI."""

from pathlib import Path
from typing import Any
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GEMMA_", extra="ignore")
    
    model_name: str = Field(default="translategemma:12b", description="Ollama model name")
    api_base: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    source_lang: str = "English"
    source_code: str = "en"
    target_lang: str = "Spanish"
    target_code: str = "es"
    chunk_size: int = 1000
    chunk_overlap: int = 0

def load_config(config_path: Path, cli_overrides: dict[str, Any] | None = None) -> Settings:
    """Load and merge configuration from YAML, Env, and CLI."""
    yaml_config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f) or {}
    
    overrides = {k: v for k, v in (cli_overrides or {}).items() if v is not None}
    return Settings(**{**yaml_config, **overrides})