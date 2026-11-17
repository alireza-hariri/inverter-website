"""Editorial copy for the elevator-inverter service page."""

import json
from pathlib import Path


_source = json.loads(
    Path(__file__).with_name("elevator_service_source.json").read_text(encoding="utf-8")
)
ELEVATOR_SERVICE_BODY_FA = _source["body_fa"]
ELEVATOR_SERVICE_BODY_EN = """
Specialist Elevator Inverter Repair: Elevator Drive Diagnostics and Reconditioning at ElectroGold

Is your elevator drive repeatedly faulting? Cabin vibration or sudden stops can put residents' safety and comfort at risk.

Any disruption to an elevator drive can lead to recurring failures, costly building-management expenses, or unsafe cabin stops. ElectroGold uses specialist technical knowledge and advanced equipment to diagnose and recondition elevator drives from major brands at the root cause.

Why entrust your elevator drive to ElectroGold?

Unlike routine services that only reset a fault or replace an entire board, we focus on resolving the underlying cause:

Root-cause diagnostics: identify faults in the power and control sections to help prevent repeat failures.

Load testing: after repair, the drive is tested with a test motor under operating conditions, including S-curve motion and encoder response.

Quality components: replace IGBTs, DC-link capacitors and other power components with suitable original-quality parts.

Specialist adjustment: optimize motion parameters for a smooth, quiet ride.

Our elevator-drive services

We provide a range of services for elevator inverters, including:

Resolving common software and control faults.

Repairing gate-driver and power-stage circuits.

Diagnosing power supplies and reducing drive noise susceptibility (EMI).

Reconditioning damaged boards with precision equipment.

Signs of failure not to ignore

Contact us before other equipment is affected if you notice drive-panel fault codes such as Overcurrent, Overvoltage or Ground Fault; cabin vibration at startup or stopping; no response to control-panel commands; or smoke and a burning smell.

Our repair process

We keep the repair process clear: initial consultation, technical inspection with a cost and time estimate, reconditioning and operational testing, then delivery with a performance-test period.

An elevator outage cannot wait. Call ElectroGold's technical team for a repair estimate and to help restore safe operation.
""".strip()
