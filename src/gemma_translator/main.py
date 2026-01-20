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

from .config import load_config
from .translator import Translator

app = typer.Typer(
    help="Translate large text documents using local LLM models through Ollama.",
    add_completion=False,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console()

@app.command(no_args_is_help=True)
def main(
    input_file: Annotated[Path, typer.Argument(help="Input text file", exists=True)],
    output_file: Annotated[Optional[Path], typer.Option("--output", "-o", help="Output file path")] = None,
    config_file: Annotated[Path, typer.Option("--config", "-c", help="Config file")] = Path.home() / ".gemma-translator.yaml",
    model: Annotated[Optional[str], typer.Option("--model", "-m")] = None,
    api_base: Annotated[Optional[str], typer.Option("--api-base")] = None,
    source_lang: Annotated[Optional[str], typer.Option("--source-lang", "-s")] = None,
    source_code: Annotated[Optional[str], typer.Option("--source-code")] = None,
    target_lang: Annotated[Optional[str], typer.Option("--target-lang", "-t")] = None,
    target_code: Annotated[Optional[str], typer.Option("--target-code")] = None,
    chunk_size: Annotated[Optional[int], typer.Option("--chunk-size")] = None,
    chunk_overlap: Annotated[Optional[int], typer.Option("--chunk-overlap")] = None,
) -> None:
    """Translate a text document using local LLM models."""
    cli_overrides = {
        "model_name": model, "api_base": api_base, "source_lang": source_lang,
        "source_code": source_code, "target_lang": target_lang,
        "target_code": target_code, "chunk_size": chunk_size, "chunk_overlap": chunk_overlap,
    }
    
    try:
        settings = load_config(config_file, cli_overrides)
        out = output_file or input_file.parent / f"{input_file.stem}_{settings.target_code}{input_file.suffix}"
        
        console.print(f"\n[bold blue]Gemma Translator[/bold blue]\n" 
                      f"  Model: [cyan]{settings.model_name}[/cyan] | API: [cyan]{settings.api_base}[/cyan]\n" 
                      f"  Translation: [cyan]{settings.source_lang} → {settings.target_lang}[/cyan]\n" 
                      f"  Input: [green]{input_file}[/green] | Output: [green]{out}[/green]\n")

        text = input_file.read_text(encoding="utf-8")
        if not text.strip(): return
        
        translator = Translator(settings)
        chunks = translator.split_text(text)
        translated_chunks = []
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(),
                      TaskProgressColumn(), TimeElapsedColumn(), console=console) as progress:
            task = progress.add_task("Translating...", total=len(chunks))
            for i, total, translated in translator.translate_document(text):
                translated_chunks.append(translated)
                progress.update(task, advance=1, description=f"Chunk {i+1}/{total}")

        out.write_text("\n\n".join(translated_chunks), encoding="utf-8")
        console.print(f"\n[bold green]✓[/bold green] Translation complete!")

    except ConnectionError as e:
        console.print(f"\n[red]Connection error:[/red] {e}\n[yellow]Hint:[/yellow] Run: [cyan]ollama serve[/cyan]")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled. Saving partial translation...[/yellow]")
        if translated_chunks: out.write_text("\n\n".join(translated_chunks), encoding="utf-8")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()