# Bring-Up & Test Plan — LoRa Car Radio

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
**V1. Measure rail +5V**
- Equipment: DMM
- Expected: 5.00 V (allowed: 4.90–5.10 V)

**V2. Measure rail +3V3**
- Equipment: DMM
- Expected: 3.30 V (allowed: 3.20–3.40 V)

## Oscillator Checks
**F1. Probe oscillator Y1**
- Equipment: Oscilloscope
- Expected: ~16.000 MHz (allowed: 15.900–16.100 MHz)

**F2. Probe oscillator Y2**
- Equipment: Oscilloscope
- Expected: ~32.000 MHz (allowed: 31.900–32.100 MHz)

## Firmware Programming
**P1. Flash firmware and open serial console @115200 baud.**
- Equipment: Programmer, USB cable
- Expected: Device boots without faults

## Functional Tests
**T1. LoRa BIT: Run `bit.lora`**
- Equipment: PC serial console
- Expected: PASS

**T2. GPS BIT: Run `bit.gps`**
- Equipment: PC serial console
- Expected: PASS

**T3. IMU BIT: Run `bit.imu`**
- Equipment: PC serial console
- Expected: PASS

---
### Notes
Generated offline via deterministic template. Review tolerances and test point references before lab use.