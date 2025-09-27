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
from ingest.pdf_parser import extract_pdf_hints
from ingest.bom_parser import parse_bom
import re

def infer_entities_from_text(text: str, title: str = "Design") -> ParsedEntities:
    """Heuristically infer entities from text content"""
    T = text.upper()
    
    # Rails - look for voltage patterns
    rails = []
    voltage_patterns = [
        (r"\+?5V", 5.0), (r"\+?3V3", 3.3), (r"\+?3\.3V", 3.3),
        (r"VCC5", 5.0), (r"VCC3V3", 3.3), (r"PWR_JACK", 5.0)
    ]
    
    seen_voltages = set()
    for pattern, voltage in voltage_patterns:
        if re.search(pattern, T) and voltage not in seen_voltages:
            rails.append({"name": f"+{voltage:g}V" if voltage == 5.0 else f"+{voltage:g}V", 
                         "voltage": voltage, "tolerance_mv": 100})
            seen_voltages.add(voltage)
    
    # Oscillators - look for crystal references
    oscillators = []
    if "Y1" in T or "16MHZ" in T:
        oscillators.append({"ref": "Y1", "frequency_hz": 16000000, "tolerance_hz": 100000})
    if "Y2" in T or "32MHZ" in T:
        oscillators.append({"ref": "Y2", "frequency_hz": 32000000, "tolerance_hz": 100000})
    
    # Functional tests - infer from components
    functional_tests = []
    if "LORA" in T or "SX1276" in T:
        functional_tests.append({"name": "LoRa BIT", "command": "bit.lora", "expected": "PASS"})
    if "GPS" in T or "MAX-M10S" in T:
        functional_tests.append({"name": "GPS BIT", "command": "bit.gps", "expected": "PASS"})
    if "IMU" in T or "LSM6DSOX" in T:
        functional_tests.append({"name": "IMU BIT", "command": "bit.imu", "expected": "PASS"})
    if "I2C" in T:
        functional_tests.append({"name": "I2C BIT", "command": "bit.i2c", "expected": "PASS"})
    
    # Defaults if nothing found
    if not rails:
        rails = [{"name": "+5V", "voltage": 5.0, "tolerance_mv": 100},
                 {"name": "+3V3", "voltage": 3.3, "tolerance_mv": 100}]
    if not functional_tests:
        functional_tests.append({"name": "Full BIT", "command": "bit", "expected": "PASS"})
    
    return ParsedEntities.model_validate({
        "title": title,
        "rails": rails,
        "oscillators": oscillators,
        "functional_tests": functional_tests
    })

st.set_page_config(page_title="Test Plan Generator", layout="wide")

st.title("🔧 Bring-Up / Test Plan Generator")

uploaded = st.file_uploader("Upload design files (JSON, PDF, BOM, Altium, Netlist)", type=["json", "txt", "net", "ipc", "pdf", "xlsx", "xlsm", "csv", "schdoc", "pcbdoc", "prjpcb", "bomdoc"])

# Check if OpenAI API key is available
import os
api_key_available = bool(os.getenv("OPENAI_API_KEY"))
use_llm = st.toggle("Use LLM (if API key available)", value=api_key_available, disabled=not api_key_available)

if api_key_available:
    st.success("🤖 LLM enhancement available - OpenAI API key detected!")
else:
    st.info("💡 Set OPENAI_API_KEY environment variable to enable LLM enhancement")

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
                # Save uploaded file temporarily
                temp_path = f"/tmp/{uploaded.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                
                file_ext = uploaded.name.lower().split('.')[-1]
                
                if file_ext in ['txt', 'net', 'ipc']:
                    # Parse netlist
                    ent = parse_netlist(temp_path)
                    st.success(f"✅ Parsed netlist: {len(ent.rails)} rails, {len(ent.oscillators)} oscillators, {len(ent.functional_tests)} tests")
                
                elif file_ext == 'json':
                    # Parse as JSON
                    data = json.loads(Path(temp_path).read_text())
                    ent = ParsedEntities.model_validate(data)
                    st.success(f"✅ Loaded JSON entities: {len(ent.rails)} rails, {len(ent.oscillators)} oscillators, {len(ent.functional_tests)} tests")
                
                elif file_ext == 'pdf':
                    # Extract text from PDF
                    hints = extract_pdf_hints(temp_path)
                    text = "\n".join(hints)
                    ent = infer_entities_from_text(text, uploaded.name)
                    st.success(f"✅ Extracted from PDF: {len(ent.rails)} rails, {len(ent.oscillators)} oscillators, {len(ent.functional_tests)} tests")
                
                elif file_ext in ['xlsx', 'xlsm', 'csv']:
                    # Parse BOM
                    rows = parse_bom(temp_path)
                    text = "\n".join([f"{r} {v}" for r, v in rows])
                    ent = infer_entities_from_text(text, uploaded.name)
                    st.success(f"✅ Parsed BOM: {len(ent.rails)} rails, {len(ent.oscillators)} oscillators, {len(ent.functional_tests)} tests")
                
                elif file_ext in ['schdoc', 'pcbdoc', 'prjpcb', 'bomdoc']:
                    # Parse Altium files
                    try:
                        text = Path(temp_path).read_text(encoding="utf-8", errors="ignore")
                    except:
                        text = Path(temp_path).read_bytes().decode("latin-1", errors="ignore")
                    ent = infer_entities_from_text(text, uploaded.name)
                    st.success(f"✅ Parsed Altium file: {len(ent.rails)} rails, {len(ent.oscillators)} oscillators, {len(ent.functional_tests)} tests")
                
                else:
                    # Try to parse as JSON
                    data = json.loads(Path(temp_path).read_text())
                    ent = ParsedEntities.model_validate(data)
                    st.success(f"✅ Loaded as JSON: {len(ent.rails)} rails, {len(ent.oscillators)} oscillators, {len(ent.functional_tests)} tests")
            else:
                data = json.loads(sample_json)
                ent = ParsedEntities.model_validate(data)
            
            # Show extracted entities
            st.subheader("📋 Extracted Entities")
            st.json(ent.model_dump(), expanded=False)
            
            issues = validate_entities(ent)
            plan = generate_plan_llm(ent) if use_llm else generate_plan_offline(ent)
            plan = annotate_plan(plan, issues)
            md = plan.to_markdown() if plan.steps else (plan.notes or "")
            
            st.subheader("📝 Generated Test Plan")
            st.markdown(md)
            
            # Show LLM status badge
            if use_llm and os.getenv("OPENAI_API_KEY"):
                st.success("🤖 LLM: ON (enhanced by AI model)")
            else:
                st.info("⚙️ LLM: OFF (using deterministic template)")
                
        except Exception as e:
            st.error(f"Error: {e}")
            st.exception(e)
