# Hackathon Test Plan Generator

A complete hardware bring-up/test plan generator with CLI and web interface.

## Features
- CLI interface for batch processing
- Streamlit web UI for interactive use
- Netlist parser (IPC-D-356A format)
- JSON entity support
- Offline deterministic templates
- Optional LLM enhancement
- Professional test plan generation

## Quick Start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.cli examples/lora_entities.json --out out/testplan.md
streamlit run app/web.py
```

## License
MIT
