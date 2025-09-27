# Bring-Up & Test Plan — 

## Setup
**S1. ESD precautions; connect board to bench PSU and GND mat.**
- Equipment: ESD strap, bench PSU

**S2. Connect DMM probes to common GND and designated test points.**
- Equipment: DMM, probes

## Visual Inspection
**V0. Check component orientation, solder bridges, missing parts.**
- Equipment: Loupe
- Expected: IPC-610 Class 2 acceptable

## Voltage Rail Checks
**V1. Measure rail 327+3V3**
- Equipment: DMM
- Expected: 3.00 V (allowed: 2.90–3.10 V)

**V2. Measure rail 327+5V**
- Equipment: DMM
- Expected: 5.00 V (allowed: 4.90–5.10 V)

## Oscillator Checks
**F1. Probe oscillator Y1**
- Equipment: Oscilloscope
- Expected: ~32.000 MHz (allowed: 31.900–32.100 MHz)

## Firmware Programming
**P1. Flash firmware and open serial console @115200 baud.**
- Equipment: Programmer, USB cable
- Expected: Device boots without faults

## Functional Tests
**T1. Test Point Verification: Run `check_test_points`**
- Equipment: PC serial console
- Expected: All test points accessible

**T2. Connector Interface Test: Run `test_connectors`**
- Equipment: PC serial console
- Expected: All connectors functional

**T3. Power-On Self Test: Run `post`**
- Equipment: PC serial console
- Expected: PASS

**T4. Communication Test: Run `comm_test`**
- Equipment: PC serial console
- Expected: All interfaces responsive

---
### Notes
Generated offline via deterministic template. Review tolerances and test point references before lab use.