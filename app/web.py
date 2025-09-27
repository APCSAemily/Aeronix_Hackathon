from __future__ import annotations
import json
import sys
from pathlib import Path
import streamlit as st

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.models import ParsedEntities
from core.generator import generate_plan_offline
from nlp.llm_client import generate_plan_llm
from rules.validator import validate_entities, annotate_plan
from ingest.netlist_parser import parse_netlist

st.set_page_config(page_title="Test Plan Generator", layout="wide")

st.title("🔧 Bring-Up / Test Plan Generator")

uploaded = st.file_uploader("Upload JSON entities or netlist file", type=["json", "txt", "net", "ipc"])
use_llm = st.toggle("Use LLM (if API key available)", value=False)

placeholder = {
    "title": "LoRa Car Radio",
    "rails": [
        {"name": "+5V", "voltage": 5.0, "tolerance_mv": 100},
        {"name": "+3V3", "voltage": 3.3, "tolerance_mv": 100}
    ],
    "oscillators": [
        {"ref": "Y1", "frequency_hz": 16_000_000, "tolerance_hz": 100_000}
    ],
    "functional_tests": [
        {"name": "LoRa BIT", "command": "bit.lora", "expected": "PASS"},
        {"name": "GPS BIT", "command": "bit.gps", "expected": "PASS"}
    ]
}

colA, colB = st.columns(2)
with colA:
    st.caption("Example entities JSON (editable)")
    sample_json = st.text_area("entities.json", value=json.dumps(placeholder, indent=2), height=350)

with colB:
    st.caption("Preview / Output")
    if st.button("Generate Plan"):
        try:
            if uploaded:
                # Check if it's a netlist file
                if uploaded.name.lower().endswith(('.txt', '.net', '.ipc')):
                    # Save uploaded file temporarily
                    temp_path = f"/tmp/{uploaded.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded.getbuffer())
                    
                    # Parse netlist
                    ent = parse_netlist(temp_path)
                    st.success(f"✅ Parsed netlist: {len(ent.rails)} rails, {len(ent.oscillators)} oscillators, {len(ent.functional_tests)} tests")
                else:
                    # Parse as JSON
                    data = json.loads(uploaded.read())
                    ent = ParsedEntities.model_validate(data)
            else:
                data = json.loads(sample_json)
                ent = ParsedEntities.model_validate(data)
            
            issues = validate_entities(ent)
            plan = generate_plan_llm(ent) if use_llm else generate_plan_offline(ent)
            plan = annotate_plan(plan, issues)
            md = plan.to_markdown() if plan.steps else (plan.notes or "")
            st.markdown(md)
        except Exception as e:
            st.error(f"Error: {e}")
