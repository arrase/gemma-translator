# Gemma Translator CLI

A robust CLI tool for translating large text documents using local LLM models through Ollama. Optimized for models like `translategemma:12b` or `gemma:7b`, it employs a smart chunking strategy to handle documents of any length while preserving context and structure.

## Features

- **Divide and Conquer Strategy**: Automatically splits large documents into manageable chunks using intelligent separators (paragraphs, sentences) to maintain context.
- **Resumable & Safe**: 
    - **Partial Saving**: If you interrupt the process (Ctrl+C), it automatically saves the chunks translated so far.
    - **Robust Error Handling**: Graceful error messages for connection issues or empty files.
- **Flexible Configuration**: Configure via:
    1. CLI Arguments (Highest priority)
    2. YAML Config File
    3. Environment Variables
    4. Smart Defaults
- **Rich User Experience**: Visual progress bars, spinners, and colored output using `rich`.

## Prerequisites

1.  **Ollama**: Ensure [Ollama](https://ollama.com/) is installed and running.
    ```bash
    ollama serve
    ```

2.  **Model**: Pull the default translation model (or your preferred model):
    ```bash
    ollama pull translategemma:12b
    ```

## Installation

### User Installation (Recommended)

Install using `pipx` to keep dependencies isolated:

```bash
pipx install git+https://github.com/arrase/gemma-translator.git
```

### Development Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/arrase/gemma-translator.git
cd gemma-translator
pip install -e .
```

## Usage

### Basic Translation

Translate a file using default settings (English -> Spanish):

```bash
gemma-translator input.txt
```
*Output will be saved to `input_es.txt` by default.*

### Custom Output & Language

```bash
# Specify output file
gemma-translator input.txt -o my_translation.txt

# Specify source and target languages
gemma-translator input.txt --source-lang English --target-lang French --target-code fr
```

### Changing the Model

```bash
gemma-translator input.txt --model translategemma:4b
```

## Configuration

The application looks for a configuration file at `~/.gemma-translator.yaml`.

### YAML Configuration

Create `~/.gemma-translator.yaml` to set your persistent preferences:

```yaml
model_name: "translategemma:12b"
api_base: "http://localhost:11434"
source_lang: "English"
source_code: "en"
target_lang: "Spanish"
target_code: "es"
chunk_size: 1000
chunk_overlap: 0
```

### Environment Variables

You can also use environment variables (prefixed with `GEMMA_`). These are useful for containerized environments or temporary overrides.

| Variable | Config Option |
|----------|---------------|
| `GEMMA_MODEL_NAME` | `model_name` |
| `GEMMA_API_BASE` | `api_base` |
| `GEMMA_SOURCE_LANG` | `source_lang` |
| `GEMMA_TARGET_LANG` | `target_lang` |
| `GEMMA_CHUNK_SIZE` | `chunk_size` |

### CLI Options Reference

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output file path | `{stem}_{lang_code}{suffix}` |
| `--config` | `-c` | Config file path | `~/.gemma-translator.yaml` |
| `--model` | `-m` | Ollama model name | `translategemma:12b` |
| `--api-base` | | Ollama API URL | `http://localhost:11434` |
| `--source-lang` | `-s` | Source language name | `English` |
| `--source-code` | | Source ISO code | `en` |
| `--target-lang` | `-t` | Target language name | `Spanish` |
| `--target-code` | | Target ISO code | `es` |
| `--chunk-size` | | Characters per chunk | `1000` |
| `--chunk-overlap` | | Overlap chars | `0` |

## How It Works

1.  **Ingestion**: Reads the input text file.
2.  **Chunking**: Splits the text into chunks defined by `chunk_size` (default 1000 chars), respecting natural boundaries like newlines and sentences to avoid breaking context.
3.  **Translation**: Sends each chunk to the local Ollama LLM with a system prompt optimized for translation.
4.  **Assembly**: Combines translated chunks and saves the final result.
