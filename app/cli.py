from __future__ import annotations
import json
import sys
import argparse
from pathlib import Path
from rich import print

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.models import ParsedEntities
from core.generator import generate_plan_offline
from nlp.llm_client import generate_plan_llm
from rules.validator import validate_entities, annotate_plan
from ingest.netlist_parser import parse_netlist


def main():
    parser = argparse.ArgumentParser(description="Hardware bring-up/test plan generator")
    parser.add_argument("input", help="Path to JSON entities or netlist file")
    parser.add_argument("--out", default="out/testplan.md", help="Output markdown path")
    parser.add_argument("--offline", action="store_true", help="Force offline deterministic plan")
    parser.add_argument("--netlist", action="store_true", help="Input is a netlist file (IPC-D-356A format)")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[red]Error: File {input_path} does not exist[/red]")
        sys.exit(1)
    
    # Parse input based on type
    if args.netlist or input_path.suffix.lower() in ['.net', '.txt', '.356']:
        print(f"[blue]Parsing netlist file: {input_path}[/blue]")
        try:
            ent = parse_netlist(str(input_path))
            print(f"[green]Extracted: {len(ent.rails)} rails, {len(ent.oscillators)} oscillators, {len(ent.functional_tests)} tests[/green]")
        except Exception as e:
            print(f"[red]Error parsing netlist: {e}[/red]")
            sys.exit(1)
    else:
        # Assume JSON format
        data = json.loads(input_path.read_text())
        ent = ParsedEntities.model_validate(data)

    issues = validate_entities(ent)
    plan = generate_plan_offline(ent) if args.offline else generate_plan_llm(ent)
    plan = annotate_plan(plan, issues)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    md = plan.to_markdown() if plan.steps else (plan.notes or "")
    out_path.write_text(md)
    print(f"[green]Wrote {out_path}[/green]")


if __name__ == "__main__":
    main()
