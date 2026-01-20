"""Configuration management for Gemma Translator CLI.

Handles loading and merging configuration from YAML files, environment variables,
and CLI arguments with proper precedence.
"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with defaults and validation.
    
    Configuration precedence (highest to lowest):
    1. CLI arguments (passed as overrides)
    2. YAML configuration file
    3. Environment variables (prefixed with GEMMA_)
    4. Default values defined here
    """
    
    model_config = SettingsConfigDict(
        env_prefix="GEMMA_",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    model_name: str = Field(
        default="translategemma:12b",
        description="Ollama model name to use for translation"
    )
    api_base: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL"
    )
    source_lang: str = Field(
        default="English",
        description="Source language name"
    )
    source_code: str = Field(
        default="en",
        description="Source language ISO code"
    )
    target_lang: str = Field(
        default="Spanish",
        description="Target language name"
    )
    target_code: str = Field(
        default="es",
        description="Target language ISO code"
    )
    chunk_size: int = Field(
        default=1000,
        description="Number of characters per text chunk"
    )
    chunk_overlap: int = Field(
        default=0,
        description="Number of overlapping characters between chunks"
    )


def load_yaml_config(config_path: Path) -> dict[str, Any]:
    """Load configuration from a YAML file.
    
    Args:
        config_path: Path to the YAML configuration file.
        
    Returns:
        Dictionary with configuration values, empty dict if file doesn't exist.
    """
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config if config else {}
    except yaml.YAMLError:
        return {}


def load_config(config_path: Path, cli_overrides: dict[str, Any] | None = None) -> Settings:
    """Load and merge configuration from all sources.
    
    Priority (highest to lowest):
    1. CLI arguments (cli_overrides)
    2. YAML configuration file
    3. Environment variables
    4. Default values
    
    Args:
        config_path: Path to the YAML configuration file.
        cli_overrides: Dictionary of CLI argument overrides (None values are ignored).
        
    Returns:
        Merged Settings instance.
    """
    # Load YAML config
    yaml_config = load_yaml_config(config_path)
    
    # Filter out None values from CLI overrides
    if cli_overrides:
        cli_config = {k: v for k, v in cli_overrides.items() if v is not None}
    else:
        cli_config = {}
    
    # Merge: YAML values first, then CLI overrides take precedence
    merged_config = {**yaml_config, **cli_config}
    
    # Create settings with merged config
    return Settings(**merged_config)
