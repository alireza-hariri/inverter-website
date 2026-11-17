"""Editorial copy for the solar-plant and inverter service page."""

import json
from pathlib import Path


_source = json.loads(
    Path(__file__).with_name("solar_service_source.json").read_text(encoding="utf-8")
)
SOLAR_SERVICE_BODY_FA = _source["body_fa"]
SOLAR_SERVICE_BODY_EN = """
Specialist Solar Inverter Repair: Diagnostics and Performance Recovery

Has a fault stopped your solar inverter and interrupted the plant's energy production?

The inverter converts DC to AC and helps optimize a solar system. A fault can directly affect energy yield and return on investment. ElectroGold provides diagnostics and repair for on-grid and hybrid solar inverters, drawing on specialist power-electronics and control expertise.

Why is specialist inverter repair important?

Solar-inverter faults may involve more than a simple software error. Proper diagnostics include:

MPPT root-cause analysis to check tracking stability and impedance matching with the PV array.

DC/AC circuit repair and replacement of damaged semiconductors such as IGBTs and diodes with quality components.

Monitoring and communication troubleshooting to restore access to plant-performance data.

Operational load testing to confirm stable operation after repair and reduce repeat faults.

ElectroGold solar-inverter services

We repair control and power boards for on-grid and hybrid inverters, diagnose voltage, current, insulation and communication faults, check internal protection circuits, and optimize settings for the grid and PV array.

We rely on engineering, not unrealistic promises

System efficiency also depends on panel condition, orientation, environment and cable design. Our commitment is to restore the inverter to the manufacturer's intended operating range and accurately diagnose inverter-related production losses.

Our process includes collecting the model and fault code, technical assessment and cost estimate, electronic diagnostics and repair, and final testing under operating conditions.

Contact our solar-energy specialists to diagnose the fault and help return the system to production.
""".strip()
