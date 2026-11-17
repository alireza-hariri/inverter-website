"""Editorial copy for the welding-equipment service page."""

import json
from pathlib import Path


_source = json.loads(
    Path(__file__).with_name("welding_service_source.json").read_text(encoding="utf-8")
)
WELDING_SERVICE_BODY_FA = _source["body_fa"]
WELDING_SERVICE_BODY_EN = """
Specialist Inverter Welding-Machine Repair: Board and Power-Stage Diagnostics

If your welding machine has an unstable arc or output current, or shuts down repeatedly, avoid delays caused by unsuitable repairs.

A welding-machine stoppage can halt an industrial project and add significant cost. ElectroGold uses specialist expertise and advanced equipment to diagnose and repair inverter welding machines for home and industrial use.

Why entrust your welding machine to ElectroGold?

We focus on the root causes of electronic faults, not just component replacement:

Switching-circuit diagnostics and repair to address voltage and current fluctuations that can damage the machine.

Load testing: after repair, the machine is tested under operating conditions to check current stability during welding.

Quality power components, including suitable IGBTs, to help restore reliable performance.

Control-board diagnostics to resolve digital faults and gate-driver issues that may cause secondary damage.

Signs of failure to watch for include a persistent thermal-warning light, smoke or a burning smell, arc instability or fluctuating output current, and sudden shutdown during welding.

Our process covers intake information, initial diagnosis and an estimate, repair and protection-circuit checks, operational load testing, and delivery with a performance-test period.

A faulty welding machine can slow work and damage electrodes or workpieces. Call ElectroGold for repair estimates, or submit a repair request for assessment.
""".strip()
