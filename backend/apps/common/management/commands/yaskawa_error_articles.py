"""Bilingual Yaskawa fault articles based on the supplied DOCX files.

Persian titles and body text are loaded verbatim from the source documents.
"""

import json
from pathlib import Path


YASKAWA_ERROR_ARTICLES = [
    {
        "slug": "yaskawa-drive-ef-external-fault",
        "title_en": "Yaskawa Drive EF/EF0 External Fault: Causes and Checks",
        "excerpt_fa": "راهنمای خطای خارجی EF یا EF0 در درایو یاسکاوا و بررسی فرمان‌های بیرونی، ورودی‌ها و تجهیزات حفاظتی.",
        "excerpt_en": "A guide to Yaskawa EF/EF0 external faults and checks for external commands, inputs, and safety equipment.",
        "body_en": """
<p>Yaskawa drive codes <strong>EF/EF0</strong> indicate an external fault input or stop command. Depending on the model and parameter configuration, the source may be a controller, safety device, sensor, or external wiring rather than a failed drive.</p>
<h2>What to check</h2>
<ul>
<li>Review emergency-stop and safety-relay status.</li>
<li>Check connected sensors, thermal protection, and PLC signals.</li>
<li>Inspect the digital input and its wiring for an open circuit, loose terminal, or electrical noise.</li>
</ul>
<h2>Safe troubleshooting</h2>
<p>Identify which input is assigned to the external fault and trace the signal to its source. Do not bypass the safety input or repeatedly reset the drive without correcting the external condition. Follow the manual for the specific Yaskawa model.</p>
<p>ElectroGold can help trace the command and diagnose the drive if the external circuit checks out.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Yaskawa drive EF0 external fault control wiring diagnostics",
        "services": ["industrial-inverter-repair"], "brands": ["yaskawa"],
        "seo_title_fa": "رفع خطای EF و EF0 در درایو یاسکاوا | الکتروگلد",
        "seo_title_en": "Yaskawa EF/EF0 External Fault Diagnosis | ElectroGold",
        "seo_description_fa": "برای عیب‌یابی EF یا EF0 یاسکاوا، ورودی خارجی، PLC، سنسورها، مدار ایمنی و سیم‌کشی فرمان را بررسی کنید.",
        "seo_description_en": "Troubleshoot Yaskawa EF/EF0 by checking the external input, PLC, sensors, safety circuit, and control wiring.",
    },
    {
        "slug": "yaskawa-drive-gf-ground-fault",
        "title_en": "Yaskawa Drive GF Ground Fault: Motor, Cable, and Inverter Checks",
        "excerpt_fa": "علت خطای GF در درایو یاسکاوا را در عایق کابل، سیم‌پیچ موتور و بخش قدرت اینورتر بررسی کنید.",
        "excerpt_en": "Check motor-cable insulation, motor windings, and the inverter power stage when a Yaskawa drive reports GF.",
        "body_en": """
<p>A <strong>GF (Ground Fault)</strong> indication means that the drive has detected a possible leakage path to ground. The exact detection method depends on the Yaskawa model.</p>
<h2>Possible causes</h2>
<ul>
<li>Damaged insulation or a short in the cable between the drive and motor.</li>
<li>Moisture, contamination, or insulation failure in the motor winding.</li>
<li>A fault in the inverter's output power stage or current-detection circuit.</li>
</ul>
<h2>Inspection and safety</h2>
<p>Isolate the drive safely before external checks. Insulation testing must be performed with the motor cable disconnected from the inverter; never apply a megohmmeter to the drive output. Do not defeat protective earth or disable ground-fault protection.</p>
<p>If the motor and cable are sound but GF remains, have the drive inspected by a qualified repairer. ElectroGold can diagnose Yaskawa power-stage faults.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Yaskawa inverter GF ground fault repair diagnostics",
        "services": ["industrial-inverter-repair"], "brands": ["yaskawa"],
        "seo_title_fa": "علت خطای GF در درایو یاسکاوا و عیب‌یابی | الکتروگلد",
        "seo_title_en": "Yaskawa Drive GF Ground Fault Diagnosis | ElectroGold",
        "seo_description_fa": "خطای GF یاسکاوا می‌تواند از کابل، موتور یا بخش قدرت باشد؛ نکات بررسی ایمن و زمان تعمیر تخصصی را بخوانید.",
        "seo_description_en": "A Yaskawa GF fault may involve the cable, motor, or power stage. Review safe checks and when specialist repair is needed.",
    },
    {
        "slug": "yaskawa-drive-lf-output-phase-loss",
        "title_en": "Yaskawa Drive LF Fault: Output Phase Loss to the Motor",
        "excerpt_fa": "برای رفع خطای LF یاسکاوا، اتصالات خروجی، کابل و سیم‌پیچ موتور و مدار قدرت درایو را بررسی کنید.",
        "excerpt_en": "Check output connections, motor cable and windings, and the drive power stage when troubleshooting Yaskawa LF.",
        "body_en": """
<p>The <strong>LF</strong> fault on a Yaskawa drive indicates an output-phase problem under the conditions defined by that model. The drive may have detected a missing or unbalanced phase between its output and the motor.</p>
<h2>Common areas to inspect</h2>
<ul>
<li>Loose, overheated, or damaged U/V/W terminals.</li>
<li>A broken motor cable or poor connection in the motor terminal box.</li>
<li>An open or damaged motor winding.</li>
<li>A fault in the inverter output stage if the external circuit is sound.</li>
</ul>
<h2>Safety and repair</h2>
<p>Isolate the equipment and verify it is de-energized before checking connections. Do not keep resetting the drive or operate the motor with a missing phase. If the cable and motor check out, have a qualified technician inspect the drive power components.</p>
<p>ElectroGold provides Yaskawa drive diagnostics and post-repair testing.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Yaskawa LF output phase loss motor drive repair",
        "services": ["industrial-inverter-repair"], "brands": ["yaskawa"],
        "seo_title_fa": "رفع خطای LF یاسکاوا؛ قطع فاز خروجی | الکتروگلد",
        "seo_title_en": "Yaskawa LF Output Phase Loss Diagnosis | ElectroGold",
        "seo_description_fa": "علت خطای LF درایو یاسکاوا را با بررسی اتصالات U/V/W، کابل، موتور و بخش خروجی اینورتر پیدا کنید.",
        "seo_description_en": "Diagnose Yaskawa LF by checking U/V/W connections, the motor cable and windings, and the inverter output stage.",
    },
    {
        "slug": "yaskawa-drive-oc-dc-bus-overvoltage",
        "title_en": "Yaskawa Drive oC Fault: DC-Bus Overvoltage Diagnosis",
        "excerpt_fa": "علت خطای oC اضافه‌ولتاژ باس DC در درایو یاسکاوا و نقش ترمز، انرژی برگشتی و ولتاژ ورودی را بخوانید.",
        "excerpt_en": "Learn possible causes of a Yaskawa oC DC-bus overvoltage, including braking, regenerative energy, and input voltage.",
        "body_en": """
<p>The supplied article identifies <strong>oC</strong> as a DC-bus overvoltage fault on the Yaskawa drive models it discusses. Confirm the code's exact meaning in the manual for your specific drive.</p>
<h2>Possible causes</h2>
<ul>
<li>Regenerative energy returning to the DC bus while the motor decelerates.</li>
<li>A braking resistor or braking circuit that is disconnected, incorrectly sized, or faulty.</li>
<li>High or unstable input-supply voltage.</li>
<li>Incorrect deceleration or braking-related settings for the application.</li>
</ul>
<h2>What to check</h2>
<p>Review the stopping conditions and the braking circuit, and have the input voltage checked by a qualified person. Do not repeatedly reset the drive or alter protection limits to conceal the fault.</p>
<p>If the braking components and supply are sound but the fault continues, the DC bus and internal power circuits may need workshop diagnostics. ElectroGold can inspect and test Yaskawa drives.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Yaskawa drive DC bus overvoltage braking repair",
        "services": ["industrial-inverter-repair"], "brands": ["yaskawa"],
        "seo_title_fa": "رفع خطای oC اضافه ولتاژ باس DC یاسکاوا | الکتروگلد",
        "seo_title_en": "Yaskawa oC DC-Bus Overvoltage Diagnosis | ElectroGold",
        "seo_description_fa": "خطای oC باس DC یاسکاوا را با بررسی ترمز، انرژی برگشتی، تنظیمات توقف و برق ورودی عیب‌یابی کنید.",
        "seo_description_en": "Troubleshoot Yaskawa oC DC-bus overvoltage by checking braking, regenerative energy, stopping settings, and supply voltage.",
    },
    {
        "slug": "yaskawa-drive-oh1-heatsink-overtemperature",
        "title_en": "Yaskawa Drive oH1 Fault: Heatsink Overtemperature",
        "excerpt_fa": "فن، هیت‌سینک، تهویه تابلو و بار کاری را برای عیب‌یابی خطای oH1 یاسکاوا بررسی کنید.",
        "excerpt_en": "Check the fan, heatsink, cabinet airflow, and operating load when a Yaskawa drive reports oH1.",
        "body_en": """
<p>The <strong>oH1</strong> fault indicates a heatsink overtemperature condition on the Yaskawa models covered by the source document. Stop repeated operation while the drive is overheating and verify the model-specific fault description.</p>
<h2>Potential causes</h2>
<ul>
<li>A failed, slow, or obstructed cooling fan.</li>
<li>Dust or debris blocking the heatsink and ventilation path.</li>
<li>High ambient temperature or insufficient airflow in the electrical cabinet.</li>
<li>Heavy loading, frequent starts, or operating conditions that create excess heat.</li>
</ul>
<h2>Prevent repeat trips</h2>
<p>After safely isolating the drive, have its fan and cooling path inspected. Internal cleaning and component checks should be left to a qualified technician. If airflow and load conditions are normal but oH1 returns, the temperature sensor or power stage may need diagnosis.</p>
<p>ElectroGold can service and test Yaskawa inverters.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Yaskawa inverter oH1 heatsink fan cooling service",
        "services": ["industrial-inverter-repair"], "brands": ["yaskawa"],
        "seo_title_fa": "علت خطای oH1 یاسکاوا؛ داغی هیت‌سینک | الکتروگلد",
        "seo_title_en": "Yaskawa oH1 Heatsink Overtemperature | ElectroGold",
        "seo_description_fa": "برای عیب‌یابی oH1 یاسکاوا، فن، مسیر هوا، هیت‌سینک، دمای تابلو و شرایط بار را بررسی کنید.",
        "seo_description_en": "Diagnose Yaskawa oH1 by checking the fan, airflow, heatsink, cabinet temperature, and load conditions.",
    },
    {
        "slug": "yaskawa-drive-ol1-motor-overload",
        "title_en": "Yaskawa Drive oL1 Fault: Motor Overload Causes and Checks",
        "excerpt_fa": "خطای oL1 موتور یاسکاوا را با بررسی بار مکانیکی، جریان نامی، پارامترهای موتور و خنک‌کاری عیب‌یابی کنید.",
        "excerpt_en": "Troubleshoot Yaskawa motor-overload code oL1 by checking mechanical load, rated current, motor parameters, and cooling.",
        "body_en": """
<p>The <strong>oL1</strong> fault is associated with motor overload on the Yaskawa models described in the supplied article. The drive may be protecting the motor when current or the calculated thermal load exceeds its configured limit.</p>
<h2>Common causes</h2>
<ul>
<li>Excessive mechanical load, binding, or a jammed machine.</li>
<li>Motor rated-current or other nameplate data entered incorrectly.</li>
<li>Poor motor cooling or a motor fault that causes abnormal current.</li>
</ul>
<h2>Do not repeatedly reset the fault</h2>
<p>Repeated trips may indicate that the motor remains overloaded. Restarting without checking the load and motor can lead to overheating and winding damage. Verify the settings against the nameplate and inspect the driven mechanism safely.</p>
<p>If the motor and load are in good condition but oL1 continues, a technician should check the drive's current measurement and protection setup. ElectroGold can diagnose Yaskawa drive and motor-related faults.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Yaskawa oL1 motor overload drive diagnostics",
        "services": ["industrial-inverter-repair"], "brands": ["yaskawa"],
        "seo_title_fa": "رفع خطای oL1 یاسکاوا؛ اضافه‌بار موتور | الکتروگلد",
        "seo_title_en": "Yaskawa oL1 Motor Overload Diagnosis | ElectroGold",
        "seo_description_fa": "علت خطای oL1 یاسکاوا را در بار مکانیکی، جریان نامی موتور، تنظیمات و خنک‌کاری بررسی کنید.",
        "seo_description_en": "Check mechanical load, motor rated current, settings, and cooling when troubleshooting Yaskawa oL1.",
    },
    {
        "slug": "yaskawa-drive-ol2-inverter-overload",
        "title_en": "Yaskawa Drive oL2 Fault: Inverter Overload Diagnosis",
        "excerpt_fa": "ظرفیت درایو، جریان خروجی، بار کاری و شرایط نصب از موارد بررسی خطای oL2 اینورتر یاسکاوا هستند.",
        "excerpt_en": "Drive capacity, output current, duty cycle, and installation conditions are important checks for Yaskawa oL2.",
        "body_en": """
<p>The <strong>oL2</strong> code in the supplied document refers to inverter overload. The exact protection definition varies by Yaskawa model, so confirm it in the relevant manual before changing settings.</p>
<h2>Potential causes</h2>
<ul>
<li>The drive may be undersized for the motor or the application's load cycle.</li>
<li>Excessive output current or sustained heavy-duty operation may exceed the drive's rating.</li>
<li>Incorrect motor or protection parameters can affect the overload calculation.</li>
<li>A current-sensing or internal drive fault may be present if the application is within its rated conditions.</li>
</ul>
<h2>Recommended checks</h2>
<p>Compare the motor and drive nameplates, assess the load profile, and check the actual operating current. Do not raise overload limits or disable protection as a workaround.</p>
<p>If the equipment is correctly sized and oL2 persists, the drive should be inspected and load-tested by a repair specialist. ElectroGold provides Yaskawa inverter diagnostics.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Yaskawa inverter oL2 overload repair industrial drive",
        "services": ["industrial-inverter-repair"], "brands": ["yaskawa"],
        "seo_title_fa": "عیب‌یابی خطای oL2 یاسکاوا؛ اضافه‌بار اینورتر | الکتروگلد",
        "seo_title_en": "Yaskawa oL2 Inverter Overload Diagnosis | ElectroGold",
        "seo_description_fa": "برای رفع oL2 یاسکاوا، ظرفیت اینورتر، جریان خروجی، بار کاری و پارامترهای حفاظتی را بررسی کنید.",
        "seo_description_en": "Troubleshoot Yaskawa oL2 by checking inverter capacity, output current, duty cycle, and protection settings.",
    },
    {
        "slug": "yaskawa-drive-ov-dc-bus-overvoltage",
        "title_en": "Yaskawa Drive ov Fault: DC-Bus Overvoltage",
        "excerpt_fa": "علت خطای ov اضافه‌ولتاژ باس DC در درایو یاسکاوا و راه‌های بررسی ترمز و ولتاژ ورودی را بخوانید.",
        "excerpt_en": "Learn possible causes of Yaskawa ov DC-bus overvoltage and checks for braking and input-supply conditions.",
        "body_en": """
<p>The <strong>ov</strong> code in the supplied Yaskawa article indicates DC-bus overvoltage. The drive may trip when the DC-link voltage rises above its permitted limit.</p>
<h2>Possible causes</h2>
<ul>
<li>Regenerative energy from the motor during deceleration.</li>
<li>A braking resistor or braking circuit that cannot dissipate the returned energy.</li>
<li>High input voltage or a supply fluctuation.</li>
<li>Stopping or braking settings that do not match the load.</li>
</ul>
<h2>What to do</h2>
<p>Check the supply and the braking circuit, and review the stopping conditions against the application requirements. Do not repeatedly reset the drive or disable its overvoltage protection.</p>
<p>If the fault continues after external checks, the DC bus, braking components, and power circuit may need specialist inspection. ElectroGold can diagnose Yaskawa inverters.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Yaskawa inverter ov DC bus overvoltage braking repair",
        "services": ["industrial-inverter-repair"], "brands": ["yaskawa"],
        "seo_title_fa": "رفع خطای ov اضافه ولتاژ باس DC یاسکاوا | الکتروگلد",
        "seo_title_en": "Yaskawa ov DC-Bus Overvoltage Diagnosis | ElectroGold",
        "seo_description_fa": "خطای ov یاسکاوا را با بررسی انرژی برگشتی موتور، مدار ترمز، تنظیمات توقف و برق ورودی عیب‌یابی کنید.",
        "seo_description_en": "Troubleshoot Yaskawa ov by checking regenerative energy, braking hardware, stopping settings, and input voltage.",
    },
    {
        "slug": "yaskawa-drive-pf-input-phase-loss",
        "title_en": "Yaskawa Drive PF Fault: Input Phase Loss",
        "excerpt_fa": "خطای PF درایو یاسکاوا را در برق ورودی سه‌فاز، فیوزها، کنتاکتور و اتصالات بررسی کنید.",
        "excerpt_en": "Check the three-phase supply, fuses, contactor, and input connections when a Yaskawa drive reports PF.",
        "body_en": """
<p>The <strong>PF</strong> fault indicates an input-phase or supply problem on the Yaskawa drive models covered in the source. A missing or unbalanced phase can affect the rectified DC bus and stress the input components.</p>
<h2>Checks to make</h2>
<ul>
<li>Inspect the three-phase supply and input terminals for a missing phase or loose connection.</li>
<li>Check fuses, upstream contactors, and other supply equipment.</li>
<li>Have the phase voltages measured by a qualified electrician.</li>
</ul>
<h2>When the drive may need repair</h2>
<p>If the supply is correct at the drive terminals but PF remains, the input rectifier or phase-detection circuit may need inspection. Do not repeatedly reset the inverter or operate it with a missing phase.</p>
<p>ElectroGold can diagnose the input power circuit and test the repaired Yaskawa drive.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Yaskawa drive PF input phase loss rectifier diagnostics",
        "services": ["industrial-inverter-repair"], "brands": ["yaskawa"],
        "seo_title_fa": "علت خطای PF یاسکاوا؛ قطع فاز ورودی | الکتروگلد",
        "seo_title_en": "Yaskawa PF Input Phase Loss Diagnosis | ElectroGold",
        "seo_description_fa": "برای رفع خطای PF یاسکاوا، برق سه‌فاز، ترمینال‌ها، فیوز و کنتاکتور ورودی را بررسی کنید.",
        "seo_description_en": "Troubleshoot Yaskawa PF by checking the three-phase supply, input terminals, fuses, and contactor.",
    },
    {
        "slug": "yaskawa-drive-uv1-dc-bus-undervoltage",
        "title_en": "Yaskawa Drive uv1 Fault: DC-Bus Undervoltage",
        "excerpt_fa": "افت ولتاژ ورودی، اتصالات، مدار پیش‌شارژ، پل دیود و خازن‌ها از موارد بررسی خطای uv1 یاسکاوا هستند.",
        "excerpt_en": "Check input voltage, connections, pre-charge, rectifier, and capacitors when troubleshooting Yaskawa uv1.",
        "body_en": """
<p>The <strong>uv1</strong> fault indicates that the DC-bus voltage has fallen below the permitted level on the Yaskawa drive models described in the source document. This may happen even when the drive is still connected to the supply.</p>
<h2>Possible causes</h2>
<ul>
<li>A low or unstable input supply.</li>
<li>Loose input connections or excessive voltage drop during startup.</li>
<li>A pre-charge circuit that is not charging the DC bus correctly.</li>
<li>Worn DC-link capacitors or a damaged input rectifier.</li>
</ul>
<h2>Safe troubleshooting</h2>
<p>Have a qualified person check the supply and connections first. Do not lower protection limits to conceal the warning. Internal measurements and capacitor or rectifier checks require a trained repairer because the DC bus can retain hazardous voltage after power is removed.</p>
<p>If the input supply is stable but uv1 persists, ElectroGold can inspect the pre-charge, rectifier, and DC-link components.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Yaskawa drive uv1 DC bus undervoltage repair",
        "services": ["industrial-inverter-repair"], "brands": ["yaskawa"],
        "seo_title_fa": "رفع خطای uv1 یاسکاوا؛ افت ولتاژ باس DC | الکتروگلد",
        "seo_title_en": "Yaskawa uv1 DC-Bus Undervoltage Diagnosis | ElectroGold",
        "seo_description_fa": "علت خطای uv1 یاسکاوا را در برق ورودی، اتصالات، پیش‌شارژ، خازن باس و پل یکسوساز بررسی کنید.",
        "seo_description_en": "Diagnose Yaskawa uv1 by checking input power, connections, pre-charge, DC-link capacitors, and the rectifier.",
    },
]

_source_articles = json.loads(
    Path(__file__).with_name("yaskawa_error_articles_source.json").read_text(encoding="utf-8")
)
for _article in YASKAWA_ERROR_ARTICLES:
    _article.update(_source_articles[_article["slug"]])
