"""CLI entry point for Gemma Translator.

Provides a Typer-based command-line interface with Rich progress bars
and comprehensive error handling.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from .config import Settings, load_config
from .translator import Translator

# Initialize Typer app and Rich console
app = typer.Typer(
    name="gemma-translator",
    help="Translate large text documents using local LLM models through Ollama.",
    add_completion=False,
)
console = Console()


def generate_output_path(input_file: Path, target_code: str) -> Path:
    """Generate output file path based on input file and target language.
    
    Args:
        input_file: Path to the input file.
        target_code: Target language ISO code.
        
    Returns:
        Generated output path with language suffix.
    """
    stem = input_file.stem
    suffix = input_file.suffix
    return input_file.parent / f"{stem}_{target_code}{suffix}"


@app.command()
def main(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Path to the input text file to translate.",
            exists=True,
        ),
    ],
    output_file: Annotated[
        Optional[Path],
        typer.Option(
            "--output", "-o",
            help="Output file path. If not specified, uses input filename with language suffix.",
        ),
    ] = None,
    config_file: Annotated[
        Path,
        typer.Option(
            "--config", "-c",
            help="Path to YAML configuration file.",
        ),
    ] = Path.home() / ".gemma-translator.yaml",
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model", "-m",
            help="Ollama model name (overrides config).",
        ),
    ] = None,
    api_base: Annotated[
        Optional[str],
        typer.Option(
            "--api-base",
            help="Ollama API base URL (overrides config).",
        ),
    ] = None,
    source_lang: Annotated[
        Optional[str],
        typer.Option(
            "--source-lang", "-s",
            help="Source language name (overrides config).",
        ),
    ] = None,
    source_code: Annotated[
        Optional[str],
        typer.Option(
            "--source-code",
            help="Source language ISO code (overrides config).",
        ),
    ] = None,
    target_lang: Annotated[
        Optional[str],
        typer.Option(
            "--target-lang", "-t",
            help="Target language name (overrides config).",
        ),
    ] = None,
    target_code: Annotated[
        Optional[str],
        typer.Option(
            "--target-code",
            help="Target language ISO code (overrides config).",
        ),
    ] = None,
    chunk_size: Annotated[
        Optional[int],
        typer.Option(
            "--chunk-size",
            help="Characters per text chunk (overrides config).",
        ),
    ] = None,
    chunk_overlap: Annotated[
        Optional[int],
        typer.Option(
            "--chunk-overlap",
            help="Overlap characters between chunks (overrides config).",
        ),
    ] = None,
) -> None:
    """Translate a text document using local LLM models.
    
    Reads the input file, splits it into chunks, translates each chunk
    using the configured Ollama model, and writes the result to the output file.
    """
    # Build CLI overrides dictionary
    cli_overrides = {
        "model_name": model,
        "api_base": api_base,
        "source_lang": source_lang,
        "source_code": source_code,
        "target_lang": target_lang,
        "target_code": target_code,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
    }
    
    # Load configuration
    try:
        settings = load_config(config_file, cli_overrides)
    except Exception as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        raise typer.Exit(1)
    
    # Determine output file path
    if output_file is None:
        output_file = generate_output_path(input_file, settings.target_code)
    
    # Display configuration summary
    console.print(f"\n[bold blue]Gemma Translator[/bold blue]")
    console.print(f"  Model: [cyan]{settings.model_name}[/cyan]")
    console.print(f"  API: [cyan]{settings.api_base}[/cyan]")
    console.print(f"  Translation: [cyan]{settings.source_lang} → {settings.target_lang}[/cyan]")
    console.print(f"  Chunk size: [cyan]{settings.chunk_size}[/cyan] chars")
    console.print(f"  Input: [green]{input_file}[/green]")
    console.print(f"  Output: [green]{output_file}[/green]\n")
    
    # Read input file
    try:
        text = input_file.read_text(encoding="utf-8")
    except Exception as e:
        console.print(f"[red]Error reading input file:[/red] {e}")
        raise typer.Exit(1)
    
    if not text.strip():
        console.print("[yellow]Warning:[/yellow] Input file is empty.")
        raise typer.Exit(0)
    
    # Initialize translator
    translator = Translator(settings)
    chunks = translator.split_text(text)
    total_chunks = len(chunks)
    
    console.print(f"Document split into [bold]{total_chunks}[/bold] chunk(s).\n")
    
    # Translate with progress bar
    translated_chunks: list[str] = []
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Translating...", total=total_chunks)
            
            for i, total, translated in translator.translate_document(text):
                translated_chunks.append(translated)
                progress.update(task, advance=1, description=f"Chunk {i + 1}/{total}")
    
    except ConnectionError as e:
        console.print(f"\n[red]Connection error:[/red] {e}")
        console.print("[yellow]Hint:[/yellow] Make sure Ollama is running with the command: [cyan]ollama serve[/cyan]")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Translation cancelled by user.[/yellow]")
        if translated_chunks:
            try:
                console.print("[yellow]Saving partial translation...[/yellow]")
                output_text = "\n\n".join(translated_chunks)
                output_file.write_text(output_text, encoding="utf-8")
                console.print(f"  Partial output saved to: [green]{output_file}[/green]")
            except Exception as e:
                console.print(f"[red]Error writing partial output file:[/red] {e}")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Translation error:[/red] {e}")
        raise typer.Exit(1)
    
    # Write output file
    try:
        output_text = "\n\n".join(translated_chunks)
        output_file.write_text(output_text, encoding="utf-8")
    except Exception as e:
        console.print(f"[red]Error writing output file:[/red] {e}")
        raise typer.Exit(1)
    
    console.print(f"\n[bold green]✓[/bold green] Translation complete!")
    console.print(f"  Output saved to: [green]{output_file}[/green]")


if __name__ == "__main__":
    app()
