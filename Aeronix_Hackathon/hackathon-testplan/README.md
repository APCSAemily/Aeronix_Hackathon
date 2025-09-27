# Hackathon Test Plan Generator (CLI + Streamlit)

Generate step-by-step **bring-up / test plans** (Markdown) from hardware docs or structured entities. Ships with CLI, minimal UI, parsers, and rule checks. Works fully **offline** with a deterministic template; can optionally use an LLM if `OPENAI_API_KEY` is set.

## Quickstart

```bash
# Setup environment
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# CLI demo (offline, using examples):
python -m app.cli examples/lora_entities.json --out out/lora_testplan.md

# Process netlist file:
python -m app.cli your_board.netlist --out out/board_testplan.md --offline

# Run demo script:
python demo.py

# Streamlit web UI:
streamlit run app/web.py
```

**Note**: Make sure to run commands from the project root directory (`hackathon-testplan/`).

## Using LLMs (optional)

Set `OPENAI_API_KEY` in environment (or create a `.env` file) to enable LLM enhancement of the plan.

## Inputs

* **Netlist files**: IPC-D-356A format netlists (`.net`, `.txt`, `.356`) - automatically extracts power rails, oscillators, and test points
* **JSON entities**: Recommended for MVP speed. Example JSON in `examples/`.
* **Zip/PDF**: Ingests documents and heuristically extracts rails, oscillators, and CLI tests.

## Outputs

* Markdown test plan (`.md`), copy-paste friendly and exportable to PDF via your editor.

## Tests

```bash
pytest -q
```

## License

MIT (adjust as needed).
