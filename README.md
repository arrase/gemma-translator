# Gemma Translator CLI

A CLI tool for translating large text documents using local LLM models through Ollama, specifically optimized for `translategemma:12b`.

## Features

- **Divide and Conquer Strategy**: Automatically splits large documents into chunks for translation
- **Flexible Configuration**: Support for YAML config files, environment variables, and CLI arguments
- **Rich Progress Bars**: Visual progress indication during translation
- **Robust Error Handling**: Graceful error messages and recovery

## Installation

```bash
pipx install git+https://github.com/arrase/gemma-translator.git
```

## Usage

### Basic Usage

```bash
# Translate a file (uses default configuration)
gemma-translator input.txt

# Specify output file
gemma-translator input.txt -o translated.txt

# Specify languages
gemma-translator input.txt --source-lang English --target-lang Spanish
```

### Configuration

Create a configuration file at `~/.gemma-translator.yaml`:

```yaml
model_name: "translategemma:12b"
api_base: "http://localhost:11434"
source_lang: "English"
source_code: "en"
target_lang: "Spanish"
target_code: "es-ES"
chunk_size: 1000
chunk_overlap: 0
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--output, -o` | Output file path | Input filename with language suffix |
| `--config, -c` | Configuration file path | `~/.gemma-translator.yaml` |
| `--model, -m` | Ollama model name | `translategemma:12b` |
| `--api-base` | Ollama API URL | `http://localhost:11434` |
| `--source-lang, -s` | Source language name | `English` |
| `--source-code` | Source language ISO code | `en` |
| `--target-lang, -t` | Target language name | `Spanish` |
| `--target-code` | Target language ISO code | `es-ES` |
| `--chunk-size` | Characters per chunk | `1000` |
| `--chunk-overlap` | Overlap between chunks | `0` |

## Requirements

- Python 3.10+
- Ollama running with the translation model
