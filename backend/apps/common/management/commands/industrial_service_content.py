"""Editorial copy for the industrial-drive service page."""

import json
from pathlib import Path


_source = json.loads(
    Path(__file__).with_name("industrial_service_source.json").read_text(encoding="utf-8")
)
INDUSTRIAL_SERVICE_BODY_FA = _source["body_fa"]
INDUSTRIAL_SERVICE_BODY_EN = """
Specialist Industrial Drive Repair and Reconditioning: Root-Cause Diagnostics

Has an industrial-drive stoppage disrupted your production line?

Variable-frequency drives are critical components of industrial automation. A fault can stop production and damage machinery or motors. ElectroGold combines specialist knowledge and advanced test equipment to repair and recondition drives for reliable operation.

ElectroGold's engineering-led drive repair

Repair means more than replacing a component. Our root-cause process includes:

Power-circuit analysis: test IGBT/IPM semiconductors, rectifier bridges and DC-bus capacitors with precision instruments.

Control and command-circuit diagnostics: inspect control boards, gate-drive sections and switching power supplies.

Fieldbus communication troubleshooting: resolve problems with protocols such as Modbus, Profibus, CANopen and industrial Ethernet.

Environmental assessment: evaluate how EMI/RFI noise affects the drive and recommend ways to reduce interference.

Our specialist services

Repair and reconditioning of AC and DC drives in different power ratings; control-parameter updates for PID, torque and speed; hardware and software fault diagnosis across drive brands; and functional testing before delivery.

How we work

We first collect the drive model, fault code and operating conditions. After inspection, we report the fault and estimated cost and timing. The drive is then repaired, tested, and returned with a performance-test period.

Unexpected drive downtime disrupts production and resources. Call ElectroGold's technical support team for advice and repair estimates.
""".strip()
