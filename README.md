# Text Reversal - Document Outline Converter

Converts technical documents (Word documents) into structured outlines using Claude AI.

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Install dependencies using uv:
```bash
uv pip install -r requirements.txt
```

Or create a virtual environment and install:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

2. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

1. Place your Word document as `input.docx` in the project directory
2. Run the script:
```bash
python main.py
```

The script will:
- Read paragraphs from `input.docx`
- Process them in batches of 3
- Generate a structured outline in `outline.md`

## Files

- `main.py` - Main script
- `prompts.py` - System prompts for the AI agent
- `requirements.txt` - Python dependencies
- `input.docx` - Input document (place your file here)
- `outline.md` - Generated outline (created automatically)

