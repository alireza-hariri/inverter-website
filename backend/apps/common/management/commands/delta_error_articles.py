"""Bilingual Delta-drive articles based on the supplied DOCX files.

Persian titles and body text are loaded verbatim from the source documents.
"""

import json
from pathlib import Path

DELTA_ERROR_ARTICLES = [
    {
        "slug": "delta-inverter-gf-ground-fault",
        "title_en": "Delta Inverter GF/GFF Fault: Causes of a Ground Fault",
        "excerpt_fa": "علت‌های احتمالی خطای اتصال به زمین در درایو دلتا، روش بررسی کابل و موتور و هشدارهای ایمنی مهم را بخوانید.",
        "excerpt_en": "Learn what may trigger a ground-fault indication on a Delta drive, how external wiring and the motor are checked, and which safety precautions matter.",
        "body_en": """
<p>A <strong>GF or GFF</strong> indication on some Delta inverter models may point to leakage current or an abnormal condition detected on the output side. The exact code and protection logic vary by drive family and settings, so use the manual for the specific model as the final reference. The drive stops its output to protect the equipment.</p>
<h2>Possible causes</h2>
<ul>
<li><strong>Motor cable:</strong> Damaged insulation, crushing, or contact with the machine frame can cause leakage.</li>
<li><strong>Motor winding:</strong> Moisture, conductive contamination, or insulation damage may create a path to ground; a fault can become apparent as the motor heats up.</li>
<li><strong>The drive itself:</strong> If the motor and cable have been safely isolated and checked but the drive still reports the fault, its output stage or current-detection circuit needs assessment by a qualified repairer.</li>
</ul>
<h2>Safe troubleshooting</h2>
<p>Isolate the equipment according to the manufacturer's instructions before inspecting the cable or motor, and have a qualified person perform the checks. Insulation-resistance testing with a megohmmeter must be done with the inverter fully disconnected; applying the tester to the drive output can damage its electronics.</p>
<h2>Safety warning</h2>
<p>Do not disable ground-fault protection or disconnect protective earth. The DC-link capacitors may retain hazardous voltage after power is removed. Only trained technicians should open the drive or measure inside it, after verifying safe discharge.</p>
<h2>When professional repair is needed</h2>
<p>If the motor and cable are sound, the fault remains with the motor disconnected, or the power stage may have been damaged, the drive's output and current-sensing circuits should be checked in a workshop. Contact ElectroGold for Delta inverter diagnostics and repair.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Delta inverter ground fault repair workshop",
        "services": ["industrial-inverter-repair"],
        "brands": ["delta"],
        "seo_title_fa": "رفع خطای GF و GFF اینورتر دلتا | الکتروگلد",
        "seo_title_en": "Delta Inverter GF/GFF Fault Diagnosis | ElectroGold",
        "seo_description_fa": "با علت‌های احتمالی خطای GF یا GFF در درایو دلتا، بررسی ایمن کابل و موتور و زمان مناسب برای تعمیر تخصصی آشنا شوید.",
        "seo_description_en": "Understand possible Delta GF/GFF fault causes, safe motor and cable checks, and when professional inverter repair is required.",
    },
    {
        "slug": "delta-inverter-oc-overcurrent",
        "title_en": "Technical Analysis of OC (Overcurrent) Faults in Siemens Drives",
        "excerpt_fa": "تحلیل خطای جریان اضافه در درایوهای زیمنس، علت‌های احتمالی در موتور و کابل و بخش قدرت و خطر ریست مکرر.",
        "excerpt_en": "An analysis of overcurrent faults in Siemens drives, possible motor, cable, and power-stage causes, and the risks of repeated resets.",
        "body_en": """
<p>An <strong>OC (Overcurrent)</strong> fault in Siemens drives, including SINAMICS models, is commonly displayed as F0001. It is a frequent but sensitive protection warning. Repeatedly resetting the drive does not resolve its cause and may worsen damage.</p>
<h2>Why an OC fault is more than a simple connection issue</h2>
<ul>
<li><strong>Motor and cable:</strong> Damaged motor-cable insulation or a shorted motor winding can cause excessive current.</li>
<li><strong>Current sensing and feedback:</strong> A failed current sensor or its signal-processing path on the control board may report a false overcurrent.</li>
<li><strong>Power stage:</strong> A leaking or damaged IGBT, or an inaccurate gate-driver circuit, can trigger an OC fault at startup.</li>
</ul>
<h2>Why repeated resets can make the damage worse</h2>
<p>If an IGBT or gate-driver component is already faulty, every reset can turn a small defect into a major power-stage failure. The DC-link capacitors can retain hazardous energy after the supply is disconnected; never open the drive unless it has been safely discharged by a qualified technician.</p>
<h2>When to contact ElectroGold</h2>
<p>Check the motor cable and make sure the motor shaft can rotate freely. If the OC fault remains, ElectroGold can analyze waveforms and gate-driver signals to determine whether the fault is external or the drive needs specialist repair. Do not repeatedly reset the unit.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Delta inverter overcurrent troubleshooting industrial drive",
        "services": ["industrial-inverter-repair"],
        "brands": ["delta"],
        "seo_title_fa": "تحلیل خطای OC در درایو زیمنس (SINAMICS) | الکتروگلد",
        "seo_title_en": "Siemens SINAMICS OC (F0001) Fault Analysis | ElectroGold",
        "seo_description_fa": "علت خطای جریان اضافه OC و کد F0001 در درایوهای زیمنس، خطر ریست مکرر و زمان نیاز به تعمیر تخصصی را بخوانید.",
        "seo_description_en": "Learn about Siemens SINAMICS OC/F0001 causes, the risks of repeated resets, and when specialist drive repair is needed.",
    },
    {
        "slug": "delta-inverter-oh-overheat",
        "title_en": "Delta Inverter oH Fault: Why Is the Drive Overheating?",
        "excerpt_fa": "فن، مسیر تهویه، بار موتور و حسگر دما از مواردی هستند که هنگام بروز خطای دمای بالا در اینورتر دلتا باید بررسی شوند.",
        "excerpt_en": "Check the cooling fan, airflow, motor load, and temperature sensing when a Delta inverter reports an overheat fault.",
        "body_en": """
<p>An <strong>oH (Overheat)</strong> fault on some Delta inverter models indicates that the heatsink or internal components have become too hot. The displayed code and trip threshold vary by drive family; consult the manual and do not continue operating the equipment while it is overheating.</p>
<h2>Possible causes</h2>
<ul>
<li><strong>Weak or failed fan:</strong> A fan may still spin but move too little air because of dust or wear.</li>
<li><strong>Blocked airflow:</strong> Dust and grease on air inlets or heatsink fins can prevent heat from dissipating.</li>
<li><strong>Load or installation conditions:</strong> Heavy loads, frequent starts, a hot enclosure, or insufficient clearance around the drive can raise its temperature.</li>
<li><strong>Sensor or internal circuit:</strong> A failed temperature sensor or power component may cause a false indication or actual overheating.</li>
</ul>
<h2>What should you do?</h2>
<p>Stop the equipment safely, then check ventilation and load conditions. Fan servicing, internal cleaning, thermal-compound replacement, or sensor testing must be done only after the drive has been isolated and safely discharged according to the manufacturer's instructions. These tasks should be handled by a qualified technician.</p>
<h2>Prevent a recurring fault</h2>
<p>If the fault returns after airflow and installation conditions are corrected, the fan, temperature sensor, and thermal transfer from power components should be checked. Repeated operation at high temperature can shorten capacitor and power-component life. ElectroGold can assess the drive after servicing.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Delta inverter overheating fan heatsink repair",
        "services": ["industrial-inverter-repair"],
        "brands": ["delta"],
        "seo_title_fa": "رفع خطای oH اینورتر دلتا و علت داغ‌شدن درایو | الکتروگلد",
        "seo_title_en": "Delta Inverter oH Overheat Diagnosis | ElectroGold",
        "seo_description_fa": "علت خطای oH اینورتر دلتا را با بررسی فن، تهویه، بار کاری و حسگر دما پیدا کنید؛ نکات ایمنی سرویس درایو.",
        "seo_description_en": "Find possible causes of a Delta oH fault by checking fan operation, airflow, load, and temperature sensing.",
    },
    {
        "slug": "delta-inverter-ol-overload",
        "title_en": "Delta Inverter oL Fault: Motor or Drive Overload?",
        "excerpt_fa": "با بررسی بار مکانیکی، جریان موتور، تنظیمات پلاک و ظرفیت درایو، علت هشدار اضافه‌بار را مرحله‌به‌مرحله پیدا کنید.",
        "excerpt_en": "Trace an overload indication by checking the mechanical load, motor current, nameplate settings, and inverter capacity.",
        "body_en": """
<p>An <strong>oL (Overload)</strong> indication means that the calculated current or load has exceeded the permitted range for the configured conditions. The meaning of suffix codes such as oL1 varies by drive model; check the manual for the specific inverter and do not assume all codes mean the same thing.</p>
<h2>Where to begin</h2>
<ul>
<li><strong>Mechanical load:</strong> A jam, excessive friction, gearbox trouble, or increased process load can raise motor current.</li>
<li><strong>Motor nameplate data:</strong> Rated voltage, current, and frequency must be entered according to the motor plate and drive instructions.</li>
<li><strong>Drive sizing:</strong> The inverter must suit the motor current and the load's duty cycle.</li>
<li><strong>Current measurement:</strong> If the load and settings are correct but the warning continues, the drive's current measurement should also be checked.</li>
</ul>
<h2>Do not bypass overload protection</h2>
<p>Increasing the current limit or disabling protection without proper engineering calculations can expose both motor and drive to overheating and failure. Do not simply clear the warning and repeatedly restart the equipment; correct the cause first.</p>
<h2>When is repair needed?</h2>
<p>If the motor and mechanism are sound, the parameters match the nameplate, and the fault still recurs, the current-sensing circuit and power stage need inspection. ElectroGold can diagnose and test a Delta inverter.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Delta inverter overload fault industrial motor diagnostics",
        "services": ["industrial-inverter-repair"],
        "brands": ["delta"],
        "seo_title_fa": "علت خطای oL اینورتر دلتا و عیب‌یابی اضافه‌بار | الکتروگلد",
        "seo_title_en": "Delta Inverter oL Overload Troubleshooting | ElectroGold",
        "seo_description_fa": "تفاوت اضافه‌بار موتور و درایو را بشناسید و علت خطای oL دلتا را با بررسی بار، پلاک موتور و تنظیمات پیدا کنید.",
        "seo_description_en": "Troubleshoot a Delta oL overload by checking the motor load, nameplate data, drive sizing, and current measurement.",
    },
    {
        "slug": "delta-inverter-ol1-motor-overload",
        "title_en": "Delta Inverter oL1 Fault: How to Check Motor Overload",
        "excerpt_fa": "خطای oL1 معمولاً به بار یا جریان موتور مربوط است؛ علت‌های مکانیکی، تنظیمات موتور و موارد نیازمند تعمیر درایو را بشناسید.",
        "excerpt_en": "An oL1 trip is commonly associated with motor load or current. Review mechanical causes, motor settings, and signs that the drive needs repair.",
        "body_en": """
<p>On many Delta drives, <strong>oL1</strong> is associated with motor overload protection; the precise meaning depends on the model and enabled parameters. To help prevent motor overheating, the drive may stop its output when current exceeds the configured limit for a specified time.</p>
<h2>Common causes</h2>
<ul>
<li><strong>Excessive load or mechanical binding:</strong> A faulty bearing, overtight belt, damaged gearbox, or heavy load can increase current.</li>
<li><strong>Incorrect motor data:</strong> Rated current and other motor information should be entered from its nameplate.</li>
<li><strong>Motor or cable trouble:</strong> Insulation damage or phase imbalance may cause abnormal current and should be checked by a qualified technician.</li>
</ul>
<h2>Why repeated resets are risky</h2>
<p>A recurring trip usually means the overload condition remains. Restarting without investigation can overheat the motor. Follow workplace and manufacturer safety instructions before testing, and avoid changing protection parameters at random.</p>
<h2>Could the drive itself be faulty?</h2>
<p>If the mechanical load and motor have been checked, settings are correct, and the warning appears under unusual or no-load conditions, the drive's current-sensing circuit should be inspected by a repair specialist. Contact ElectroGold for Delta inverter diagnostics.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Delta inverter motor overload current diagnostics",
        "services": ["industrial-inverter-repair"],
        "brands": ["delta"],
        "seo_title_fa": "رفع خطای oL1 اینورتر دلتا؛ اضافه‌بار موتور | الکتروگلد",
        "seo_title_en": "Delta Inverter oL1 Motor Overload Diagnosis | ElectroGold",
        "seo_description_fa": "علت خطای oL1 در درایو دلتا را با بررسی بار مکانیکی، جریان نامی موتور و تنظیمات پیدا کنید؛ از ریست مکرر خودداری کنید.",
        "seo_description_en": "Diagnose a Delta oL1 trip by checking mechanical load, motor rated current, and drive settings. Avoid repeated resets.",
    },
    {
        "slug": "delta-inverter-orp-output-phase-loss",
        "title_en": "Delta Inverter OrP Fault: Output Phase Loss",
        "excerpt_fa": "شل‌شدن ترمینال، خرابی کابل یا موتور و ایراد بخش خروجی درایو از علت‌های احتمالی خطای OrP هستند.",
        "excerpt_en": "Loose terminals, damaged motor wiring, motor faults, or an inverter output-stage problem may cause an OrP indication.",
        "body_en": """
<p>On some Delta models, <strong>OrP (Output Phase Loss)</strong> indicates a problem with an output phase. Detection conditions depend on the drive family, settings, and load, so confirm the code in the manual for your model.</p>
<h2>What should be checked?</h2>
<ul>
<li><strong>Terminals and cable:</strong> Check for loose connections, damaged cable, or an open phase between the inverter and motor.</li>
<li><strong>Motor winding:</strong> An open winding or electrical damage may cause unbalanced current.</li>
<li><strong>Drive output:</strong> If the motor and wiring are sound, a specialist should assess the output power stage and measurement circuits.</li>
</ul>
<h2>Do not continue running with the fault</h2>
<p>Operating a motor with a missing phase can increase heat, reduce torque, and further damage the motor or inverter. Do not ignore the fault by repeatedly resetting it. Isolate the supply under the applicable safety procedures and verify the circuit is de-energized before inspecting connections.</p>
<h2>Professional drive repair</h2>
<p>If the fault remains despite sound wiring and motor checks, or the drive trips as soon as it starts, the inverter should be examined in a workshop. ElectroGold can diagnose the output stage and test the equipment after repair.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Delta inverter output phase loss repair",
        "services": ["industrial-inverter-repair"],
        "brands": ["delta"],
        "seo_title_fa": "علت خطای OrP اینورتر دلتا و قطعی فاز خروجی | الکتروگلد",
        "seo_title_en": "Delta Inverter OrP Output Phase Loss | ElectroGold",
        "seo_description_fa": "برای رفع خطای OrP درایو دلتا، ترمینال‌ها، کابل موتور، سیم‌پیچ و بخش خروجی اینورتر را ایمن بررسی کنید.",
        "seo_description_en": "Troubleshoot a Delta OrP fault by safely checking terminals, motor cable, windings, and the inverter output stage.",
    },
    {
        "slug": "delta-inverter-phl-phase-loss",
        "title_en": "Delta Inverter PHL Fault: What Causes Phase Loss?",
        "excerpt_fa": "خطای PHL ممکن است به تغذیهٔ ورودی، اتصالات، کنتاکتور، کابل موتور یا مدار تشخیص فاز مربوط باشد.",
        "excerpt_en": "A PHL indication may involve the incoming supply, connections, contactor, motor cable, or phase-detection circuit.",
        "body_en": """
<p>A <strong>PHL (Phase Loss)</strong> fault on some Delta drives means the unit has detected a missing or unbalanced phase somewhere in the system. The detection point and trip conditions depend on the model; either the incoming supply or motor output may be involved.</p>
<h2>Possible external causes</h2>
<ul>
<li>Loose or overheated input or output terminals.</li>
<li>A failed fuse, supply cable, or upstream contactor.</li>
<li>An open motor cable or winding fault on the output side.</li>
</ul>
<h2>Issues requiring specialist inspection</h2>
<p>A failed input rectifier, voltage-measurement circuit, or phase-detection circuit can also trigger the warning. These components are inside the inverter and should be inspected by a trained repairer. Input and output tests must use suitable instruments and follow the manual for the specific model.</p>
<h2>Safety warning</h2>
<p>Do not bypass phase protection by raising limits or repeatedly resetting the drive. Only authorized personnel should isolate the supply or open the panel; the DC link may remain charged after power is removed.</p>
<h2>Resolving a PHL fault</h2>
<p>If an electrician has checked the supply, fuses, and connections but the fault remains, have a repair specialist inspect the rectifier and detection circuitry. ElectroGold provides Delta inverter diagnostics and repair.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Delta inverter phase loss rectifier diagnostics",
        "services": ["industrial-inverter-repair"],
        "brands": ["delta"],
        "seo_title_fa": "رفع خطای PHL اینورتر دلتا؛ عیب‌یابی فقدان فاز | الکتروگلد",
        "seo_title_en": "Delta Inverter PHL Phase-Loss Diagnosis | ElectroGold",
        "seo_description_fa": "علت خطای PHL در درایو دلتا را در تغذیه، فیوز، کنتاکتور، کابل موتور و مدار تشخیص فاز بررسی کنید.",
        "seo_description_en": "Check the supply, fuses, contactor, motor cable, and phase-detection circuit when troubleshooting a Delta PHL fault.",
    },
    {
        "slug": "delta-inverter-uv-undervoltage",
        "title_en": "Delta Inverter uV Fault: DC-Link Undervoltage Causes",
        "excerpt_fa": "افت ولتاژ شبکه، اتصال سست، مدار شارژ اولیه، پل دیود و خازن‌ها از موارد قابل بررسی هنگام بروز خطای uV هستند.",
        "excerpt_en": "Supply dips, loose connections, the pre-charge circuit, rectifier, and capacitors are among the areas to check for a uV fault.",
        "body_en": """
<p>An <strong>uV (Undervoltage)</strong> fault on some Delta inverters occurs when the DC-bus voltage does not reach, or falls below, its permitted range. It does not always mean that power has been completely lost; check the manual for the exact code and threshold on your model.</p>
<h2>External factors</h2>
<ul>
<li>A low or unstable supply, particularly when heavy loads start.</li>
<li>A loose connection, unsuitable cable, or voltage drop in the supply path.</li>
<li>A problem with fuses, a contactor, or upstream equipment.</li>
</ul>
<h2>Possible faults inside the drive</h2>
<p>Aged DC-link capacitors, a failed rectifier, or a pre-charge circuit problem may also cause undervoltage. Diagnosing these components requires specialist measurements; do not open the inverter yourself.</p>
<h2>Do not disable protection</h2>
<p>Changing protection parameters to conceal uV may lead to unstable operation or further damage. Have the input supply checked by a qualified person and follow the manufacturer's safety instructions before taking action.</p>
<h2>When is inverter repair needed?</h2>
<p>If the supply is within range but the fault keeps recurring, the capacitors, rectifier, and pre-charge circuit should be inspected. ElectroGold can provide specialist diagnostics and functional testing for a Delta inverter.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Delta inverter undervoltage DC bus repair",
        "services": ["industrial-inverter-repair"],
        "brands": ["delta"],
        "seo_title_fa": "علت خطای uV اینورتر دلتا و افت ولتاژ | الکتروگلد",
        "seo_title_en": "Delta Inverter uV Undervoltage Troubleshooting | ElectroGold",
        "seo_description_fa": "علت خطای uV درایو دلتا را با بررسی برق ورودی، اتصالات، خازن لینک DC و مدار یکسوساز پیدا کنید.",
        "seo_description_en": "Troubleshoot a Delta uV fault by checking the input supply, connections, DC-link capacitors, and rectifier circuit.",
    },
    {
        "slug": "delta-inverter-ef-external-fault",
        "title_en": "Delta Inverter EF Fault: Checking the External Fault Input",
        "excerpt_fa": "خطای EF اغلب از فرمان ورودی یا مدار ایمنی بیرونی می‌آید؛ وضعیت توقف اضطراری، سنسورها و سیم‌کشی فرمان را بررسی کنید.",
        "excerpt_en": "An EF indication often comes from an external command or safety circuit. Check the emergency stop, sensors, and control wiring.",
        "body_en": """
<p>On many applications, a Delta <strong>EF (External Fault)</strong> indication means that a digital input configured for an external fault has been activated. EF does not necessarily mean the inverter itself has failed; a PLC, emergency-stop circuit, or external sensor may have requested a stop. Exact behavior depends on the drive model and input configuration.</p>
<h2>What should be checked?</h2>
<ul>
<li><strong>Emergency stop:</strong> Check the switch and continuity of the safety circuit.</li>
<li><strong>Motor protection and sensors:</strong> An overload relay, thermostat, pressure sensor, or other connected input may be reporting a fault.</li>
<li><strong>PLC and control wiring:</strong> Check the PLC output, digital-input terminals, broken wires, and electrical noise.</li>
</ul>
<h2>Do not bypass the protection</h2>
<p>Disabling the EF input without finding its cause can defeat the machine's safety system. If the input was triggered by motor overheating or another unsafe condition, forcing a restart can put people and equipment at risk.</p>
<h2>Systematic troubleshooting</h2>
<p>First identify why the external circuit issued the command. Only a person familiar with the wiring diagram and manufacturer instructions should change parameters or disconnect wires. If the inputs are correct but EF remains, the inverter's input circuit may need specialist inspection. ElectroGold can advise on Delta drive diagnostics.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Delta inverter external fault control panel diagnostics",
        "services": ["industrial-inverter-repair"],
        "brands": ["delta"],
        "seo_title_fa": "رفع خطای EF اینورتر دلتا؛ خطای خارجی چیست؟ | الکتروگلد",
        "seo_title_en": "Delta Inverter EF External Fault Diagnosis | ElectroGold",
        "seo_description_fa": "با بررسی ورودی دیجیتال، توقف اضطراری، PLC و سنسورها علت خطای EF در اینورتر دلتا را پیدا کنید؛ حفاظت را غیرفعال نکنید.",
        "seo_description_en": "Trace a Delta EF fault through the digital input, emergency stop, PLC, and sensors. Do not bypass safety protection.",
    },
]

_source_articles = json.loads(
    Path(__file__).with_name("delta_error_articles_source.json").read_text(encoding="utf-8")
)
DELTA_OV_ARTICLE_SOURCE = _source_articles["delta-inverter-ov-overvoltage-error-analysis"]
for _article in DELTA_ERROR_ARTICLES:
    _article.update(_source_articles[_article["slug"]])
