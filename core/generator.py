from __future__ import annotations
from typing import List
from core.models import ParsedEntities, TestPlan, TestStep

BASE_SETUP_STEPS = [
    TestStep(id="S1", section="Setup", description="ESD precautions; connect board to bench PSU and GND mat.", equipment="ESD strap, bench PSU"),
    TestStep(id="S2", section="Setup", description="Connect DMM probes to common GND and designated test points.", equipment="DMM, probes"),
]


def _voltage_steps(entities: ParsedEntities) -> List[TestStep]:
    steps: List[TestStep] = []
    for idx, r in enumerate(entities.rails, start=1):
        lo = r.voltage - r.tolerance_mv/1000
        hi = r.voltage + r.tolerance_mv/1000
        steps.append(TestStep(
            id=f"V{idx}",
            section="Voltage Rail Checks",
            description=f"Measure rail {r.name}",
            equipment="DMM",
            expected=f"{r.voltage:.2f} V (allowed: {lo:.2f}–{hi:.2f} V)",
        ))
    return steps


def _osc_steps(entities: ParsedEntities) -> List[TestStep]:
    steps: List[TestStep] = []
    for idx, o in enumerate(entities.oscillators, start=1):
        lo = o.frequency_hz - o.tolerance_hz
        hi = o.frequency_hz + o.tolerance_hz
        mhz = o.frequency_hz/1e6
        steps.append(TestStep(
            id=f"F{idx}",
            section="Oscillator Checks",
            description=f"Probe oscillator {o.ref}",
            equipment="Oscilloscope",
            expected=f"~{mhz:.3f} MHz (allowed: {lo/1e6:.3f}–{hi/1e6:.3f} MHz)",
        ))
    return steps


def _functional_steps(entities: ParsedEntities) -> List[TestStep]:
    steps: List[TestStep] = []
    for idx, t in enumerate(entities.functional_tests, start=1):
        expected = t.expected or "Return PASS or expected telemetry"
        cmd = (f"Run `{t.command}`" if t.command else f"Execute {t.name}")
        steps.append(TestStep(
            id=f"T{idx}",
            section="Functional Tests",
            description=f"{t.name}: {cmd}",
            equipment="PC serial console",
            expected=expected,
        ))
    return steps


def generate_plan_offline(entities: ParsedEntities) -> TestPlan:
    steps: List[TestStep] = []
    steps.extend(BASE_SETUP_STEPS)
    steps.append(TestStep(id="V0", section="Visual Inspection", description="Check component orientation, solder bridges, missing parts.", equipment="Loupe", expected="IPC-610 Class 2 acceptable"))
    steps.extend(_voltage_steps(entities))
    steps.extend(_osc_steps(entities))
    steps.append(TestStep(id="P1", section="Firmware Programming", description="Flash firmware and open serial console @115200 baud.", equipment="Programmer, USB cable", expected="Device boots without faults"))
    steps.extend(_functional_steps(entities))
    notes = "Generated offline via deterministic template. Review tolerances and test point references before lab use."
    return TestPlan(title=f"Bring-Up & Test Plan — {entities.title}", steps=steps, notes=notes)
