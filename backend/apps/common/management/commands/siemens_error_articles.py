"""Bilingual Siemens fault articles based on the supplied DOCX files.

Persian titles and body text are loaded verbatim from the source documents.
"""

import json
from pathlib import Path


SIEMENS_ERROR_ARTICLES = [
    {
        "slug": "siemens-drive-f0001-instantaneous-overcurrent",
        "title_en": "Siemens Inverter F0001 (Overcurrent): Root-Cause Analysis and Repair",
        "excerpt_fa": "بررسی خطای F0001 در درایو زیمنس، از پارامترهای موتور و بار مکانیکی تا کابل و طبقهٔ قدرت.",
        "excerpt_en": "A guide to Siemens F0001 overcurrent faults, from motor parameters and mechanical load to cabling and the power stage.",
        "body_en": """
<p><strong>F0001</strong> is one of the best-known and most sensitive Siemens drive fault codes. It indicates that output current has exceeded the drive's hardware limit. Fast protection is intended to prevent damage to power modules such as IGBTs.</p>
<h2>Why does a Siemens drive report F0001?</h2>
<p>ElectroGold checks the fault at three levels:</p>
<h3>Settings and parameters</h3>
<ul>
<li><strong>Ramp-up time:</strong> An acceleration time that is too short for a heavy load can cause a high inrush current at startup.</li>
<li><strong>Motor data:</strong> Parameters left over from a previous motor can make the current calculations incorrect for the motor now connected.</li>
</ul>
<h3>Mechanical system and cabling</h3>
<ul>
<li>A jammed motor or gearbox can sharply increase the torque demand.</li>
<li>Damaged cable insulation or moisture in the motor terminal box may cause leakage or excessive current.</li>
</ul>
<h3>Internal hardware</h3>
<p>If F0001 remains with the drive output disconnected (no load), the output stage, IGBTs, or gate drivers may be faulty.</p>
<h2>Engineering warning: do not repeatedly reset F0001</h2>
<p>Repeated resets while an overcurrent condition remains can thermally stress the IGBTs. A minor repair may become a costly power-module replacement.</p>
<h2>Siemens drive diagnostics at ElectroGold</h2>
<p>We use oscilloscope signal analysis to distinguish noise from a genuine power-stage fault, calibrate the repaired drive for operation under rated load, and use industrial-quality components for Siemens boards.</p>
<p>Has F0001 stopped your production line? Contact ElectroGold for technical advice and specialist Siemens drive repair.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Siemens SINAMICS inverter F0001 overcurrent repair",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "رفع خطای F0001 در درایو زیمنس | الکتروگلد",
        "seo_title_en": "Siemens Drive F0001 Overcurrent Repair | ElectroGold",
        "seo_description_fa": "علت خطای F0001 در درایو زیمنس را از تنظیمات و بار مکانیکی تا کابل، IGBT و درایور گیت بررسی کنید.",
        "seo_description_en": "Diagnose Siemens F0001 faults by checking motor settings, mechanical load, cabling, IGBTs, and gate drivers.",
    },
    {
        "slug": "siemens-drive-f0002-dc-bus-overvoltage",
        "title_en": "Siemens Drive F0002 DC-Bus Overvoltage: Managing Regenerative Energy",
        "excerpt_fa": "علت خطای F0002 در درایو زیمنس و نقش زمان کاهش سرعت، مقاومت ترمز، چاپر و ولتاژ ورودی را بخوانید.",
        "excerpt_en": "Learn how deceleration time, the braking resistor and chopper, and the input supply can contribute to Siemens F0002.",
        "body_en": """
<p><strong>F0002</strong> indicates that the Siemens drive's intermediate-circuit (DC-link) voltage has exceeded its permitted limit. In applications such as lifts, cranes, and centrifuges, this can happen when a braking motor returns mechanical energy to the drive.</p>
<h2>Why does a Siemens drive report F0002?</h2>
<h3>Ramp-down time</h3>
<p>If the motor stops too quickly, regenerative energy can charge the DC-link capacitors rapidly and push the voltage above the threshold.</p>
<h3>Braking chopper or resistor</h3>
<p>The braking circuit dissipates excess energy through a chopper and external resistor. A failed resistor or broken connection may leave the regenerative energy with nowhere to go.</p>
<h3>Input-grid overvoltage</h3>
<p>An input supply above its normal range, for example due to a factory supply or transformer problem, can raise the DC-bus voltage before braking begins.</p>
<h2>Do not rely on an unsuitable stop-time workaround</h2>
<p>Making ramp-down excessively long may not be practical for a lift or production line. The source of the fault should be identified, including the braking chopper and resistor; when the hardware is sound, correct settings can support the required stopping time.</p>
<h2>ElectroGold F0002 diagnostics</h2>
<ul>
<li>Dynamic testing of the braking resistor's resistance and power rating.</li>
<li>Inspection of the drive's internal braking-chopper module.</li>
<li>Input power-quality analysis to distinguish a grid issue from a drive fault.</li>
</ul>
<p>If F0002 occurs during braking or stopping, contact ElectroGold before repeated operation damages sensitive Siemens circuitry.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Siemens drive F0002 DC bus braking resistor chopper",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "علت خطای F0002 در درایو زیمنس | الکتروگلد",
        "seo_title_en": "Siemens Drive F0002 DC-Bus Overvoltage | ElectroGold",
        "seo_description_fa": "عیب‌یابی F0002 زیمنس با بررسی انرژی برگشتی، زمان توقف، چاپر و مقاومت ترمز و کیفیت برق ورودی.",
        "seo_description_en": "Troubleshoot Siemens F0002 by checking regenerative energy, stopping time, braking hardware, and input power quality.",
    },
    {
        "slug": "siemens-drive-f0003-undervoltage",
        "title_en": "Siemens Inverter F0003 DC-Link Undervoltage: Root-Cause Checks",
        "excerpt_fa": "افت ولتاژ شبکه، مدار پیش‌شارژ، فاز ورودی و خازن‌های باس DC از علت‌های قابل بررسی خطای F0003 هستند.",
        "excerpt_en": "Supply quality, the pre-charge circuit, input phases, and DC-link capacitors are among the checks for Siemens F0003.",
        "body_en": """
<p><strong>F0003</strong> occurs when the intermediate-circuit (DC-link) voltage falls below its permitted threshold. The drive may still have power but be unable to maintain enough energy for its output. Siemens drives stop the system to prevent unstable operation.</p>
<h2>Why does a Siemens drive stop with F0003?</h2>
<h3>Power-quality problems</h3>
<p>A brief supply-voltage drop can occur when another large motor or heavy piece of equipment starts and the factory supply cannot support both loads.</p>
<h3>Pre-charge circuit fault</h3>
<p>The pre-charge circuit, which includes a relay or contactor and charging resistor, fills the capacitors gradually at startup. A failed resistor or sticking contact may prevent the DC bus from reaching its rated voltage.</p>
<h3>Phase loss or loose wiring</h3>
<p>A loose input terminal or missing supply phase can cause the rectified DC voltage to fall sharply.</p>
<h2>When F0003 may indicate hardware damage</h2>
<p>If the fault occurs repeatedly while the supply is stable, a DC-link capacitor or the internal pre-charge circuit may be damaged. Repeated restarts can put the rectifier components at risk.</p>
<h2>ElectroGold F0003 service</h2>
<ul>
<li>DC-voltage ripple analysis to assess the bus capacitors.</li>
<li>Pre-charge circuit diagnostics and component replacement where needed.</li>
<li>Power-quality monitoring and input-choke recommendations when the supply is the cause.</li>
</ul>
<p>Contact ElectroGold if F0003 keeps recurring so the drive and its supply conditions can be checked.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Siemens inverter F0003 DC link undervoltage diagnostics",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "رفع خطای F0003 در اینورتر زیمنس | الکتروگلد",
        "seo_title_en": "Siemens Inverter F0003 Undervoltage Diagnosis | ElectroGold",
        "seo_description_fa": "برای رفع F0003 زیمنس، کیفیت برق، مدار پیش‌شارژ، فازهای ورودی، خازن‌ها و یکسوساز را بررسی کنید.",
        "seo_description_en": "Check supply quality, pre-charge, input phases, capacitors, and the rectifier when diagnosing Siemens F0003.",
    },
    {
        "slug": "siemens-drive-f0004-heatsink-overtemperature",
        "title_en": "Siemens Drive F0004 Heatsink Overtemperature: Causes and Prevention",
        "excerpt_fa": "فن، گرفتگی هیت‌سینک، تهویه تابلو، دمای محیط و فرکانس سوئیچینگ را برای عیب‌یابی F0004 بررسی کنید.",
        "excerpt_en": "Check the fan, heatsink airflow, cabinet ventilation, ambient temperature, and switching frequency for Siemens F0004.",
        "body_en": """
<p><strong>F0004</strong> indicates heatsink overtemperature in Siemens drives. The drive's temperature monitoring is intended to protect components such as IGBTs from excessive heat.</p>
<h2>Why does a Siemens drive report F0004?</h2>
<h3>Cooling system</h3>
<ul>
<li>A failed or worn internal fan is a common cause.</li>
<li>Dust, textile fibres, or industrial contamination on the heatsink fins can act as insulation and restrict heat dissipation.</li>
</ul>
<h3>Electrical cabinet and ambient conditions</h3>
<p>A sealed cabinet without adequate ventilation can trap hot air around the drive. High factory-room temperatures also reduce the drive's ability to release heat.</p>
<h3>Operating parameters</h3>
<p>A high switching frequency, sometimes selected to reduce motor noise, increases drive heat losses and may contribute to F0004.</p>
<h2>Do not treat temporary cooling as a repair</h2>
<p>Taking the drive out of the cabinet to cool it does not solve a failed fan or a blocked heatsink. Recurring overheating can damage internal electrolytic capacitors and shorten the life of the drive.</p>
<h2>ElectroGold preventive service</h2>
<ul>
<li>Specialist heatsink cleaning while protecting electronic boards.</li>
<li>Replacement with compatible, long-life Siemens-standard fans.</li>
<li>Switching-frequency optimization for the application.</li>
</ul>
<p>If F0004 occurs during a shift, contact ElectroGold to inspect the cooling system and drive.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Siemens drive F0004 heatsink cooling fan maintenance",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "رفع خطای F0004 درایو زیمنس؛ داغی هیت‌سینک | الکتروگلد",
        "seo_title_en": "Siemens Drive F0004 Heatsink Overtemperature | ElectroGold",
        "seo_description_fa": "علت F0004 زیمنس را با بررسی فن، هیت‌سینک، تهویه تابلو، دمای محیط و فرکانس سوئیچینگ پیدا کنید.",
        "seo_description_en": "Diagnose Siemens F0004 by checking the fan, heatsink, cabinet airflow, ambient temperature, and switching frequency.",
    },
    {
        "slug": "siemens-drive-f0011-motor-overtemperature",
        "title_en": "Siemens Inverter F0011 Motor Overtemperature: Protecting the Windings",
        "excerpt_fa": "خطای F0011 ممکن است از اضافه‌بار مکانیکی، خنک‌کاری موتور یا تنظیمات مدل حرارتی I²t ناشی شود.",
        "excerpt_en": "F0011 may involve mechanical overload, motor cooling, or incorrect I²t thermal-model settings.",
        "body_en": """
<p><strong>F0011</strong> is a Siemens drive warning for abnormal motor overtemperature. It does not always mean the motor has failed; the drive may be monitoring its thermal behavior and reporting a critical condition.</p>
<h2>Why does the connected motor overheat?</h2>
<h3>Mechanical overload</h3>
<p>A gearbox, conveyor, or fan with binding, a failed bearing, or a jam can force the motor to work above its rated capacity. Higher current leads to heat and may trigger F0011.</p>
<h3>Insufficient motor cooling</h3>
<p>A damaged shaft fan or blocked motor air passages can cause overheating even at rated load, particularly in dusty industrial environments.</p>
<h3>Incorrect I²t thermal model settings</h3>
<p>If rated current, power, or thermal class is entered incorrectly, the drive's motor-temperature calculations may be inaccurate and cause an unnecessary stop.</p>
<h2>Engineering warning: do not repeatedly reset F0011</h2>
<p>Repeated operation while windings are too hot can damage their insulation. Resetting the drive to keep production running may turn a warning into a motor rewind or replacement.</p>
<h2>ElectroGold F0011 checks</h2>
<ul>
<li>Load-profile analysis against the permitted thermal cycle.</li>
<li>Commissioning checks to match drive thermal parameters to the motor nameplate.</li>
<li>Inspection of power connections and motor cables, including voltage drop on long runs.</li>
</ul>
<p>Contact ElectroGold before persistent F0011 trips damage the motor windings.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Siemens inverter F0011 motor overheating repair",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "علت خطای F0011 زیمنس؛ دمای بالای موتور | الکتروگلد",
        "seo_title_en": "Siemens F0011 Motor Overtemperature | ElectroGold",
        "seo_description_fa": "اضافه‌بار، خنک‌کاری موتور و تنظیمات I²t را برای عیب‌یابی خطای F0011 در درایو زیمنس بررسی کنید.",
        "seo_description_en": "Troubleshoot Siemens F0011 by checking motor load, cooling, I²t thermal settings, and power connections.",
    },
    {
        "slug": "siemens-drive-f0012-model-specific-fault",
        "title_en": "Siemens Drive F0012: Why the Model Determines the Fault Meaning",
        "excerpt_fa": "کد F0012 در V20 و Micromaster MM440 می‌تواند معانی متفاوتی داشته باشد؛ مدل درایو را پیش از عیب‌یابی مشخص کنید.",
        "excerpt_en": "F0012 can mean different things on a V20 and a Micromaster MM440. Identify the drive model before troubleshooting.",
        "body_en": """
<p>Siemens code <strong>F0012</strong> has different meanings on different drive families. Depending on the model, it may indicate inverter overload or a heatsink temperature-sensor signal loss. Misidentifying it can send troubleshooting in the wrong direction.</p>
<h2>Identify the drive family first</h2>
<h3>V20</h3>
<p>On the V20, F0012 indicates inverter overload: output current has exceeded the thermal I²t limit for too long, and the drive stops to protect its internal components.</p>
<h3>Micromaster MM440</h3>
<p>On the MM440, F0012 is not an overload code. It indicates loss of the heatsink temperature-sensor signal. The drive can no longer monitor its temperature and stops because thermal safety cannot be confirmed.</p>
<h2>Model-specific diagnosis</h2>
<p>For an overload, check the application's duty cycle, acceleration and braking, mechanical friction, and whether the drive is correctly sized. For an MM440 sensor-signal fault, inspect the connectors, sensor wiring, and NTC sensor on the heatsink; changing overload parameters will not repair a hardware signal fault.</p>
<h2>Engineering warning</h2>
<p>Do not bypass F0012 on an MM440 by changing overload parameters. If temperature cannot be measured, the drive may lose an important layer of protection.</p>
<h2>ElectroGold F0012 service</h2>
<p>ElectroGold checks the exact model and protection logic, repairs thermal-sensor signal faults at board level, and advises on drives repeatedly overloaded by heavy loads.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Siemens V20 MM440 F0012 drive fault diagnostics",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "معنی خطای F0012 در V20 و MM440 زیمنس | الکتروگلد",
        "seo_title_en": "Siemens F0012 V20 vs MM440 Fault Diagnosis | ElectroGold",
        "seo_description_fa": "تفاوت خطای F0012 در زیمنس V20 و Micromaster MM440 را بشناسید؛ اضافه‌بار یا قطع سیگنال حسگر دما.",
        "seo_description_en": "Learn the model-specific meanings of Siemens F0012: inverter overload on V20 or heatsink sensor signal loss on MM440.",
    },
    {
        "slug": "siemens-drive-f0015-f90-code-meaning",
        "title_en": "Siemens F0015 and F90: Why These Codes Are Not Ground Faults",
        "excerpt_fa": "معنی F0015 و F90 به مدل درایو زیمنس وابسته است؛ این مقاله تفاوت آن‌ها با خطای واقعی اتصال زمین را توضیح می‌دهد.",
        "excerpt_en": "The meaning of Siemens F0015 and F90 depends on the drive family. This guide distinguishes them from a true ground fault.",
        "body_en": """
<p>Misinterpreting Siemens fault codes can lead to the wrong repair. Despite being associated with a ground fault in some descriptions, <strong>F0015 and F90</strong> can have different meanings depending on the drive family.</p>
<h2>What F0015 and F90 may mean</h2>
<ul>
<li><strong>F0015, commonly on MM440:</strong> Loss of the motor temperature-sensor signal, for example a disconnected sensor cable or failed PTC/KTY sensor. This is motor thermal protection, not a ground-fault indication.</li>
<li><strong>F90 on V20:</strong> Instability in the current setpoint, potentially related to electromagnetic noise or an unstable analog input signal.</li>
</ul>
<p>Checking motor-cable insulation alone will not resolve these faults if their model-specific causes are elsewhere.</p>
<h2>What if there is a real ground fault?</h2>
<p>The source notes that Siemens ground faults may appear as overcurrent (F0001) or as a specific earth-fault message on some advanced models. Possible signs include an immediate trip at startup, arcing or a burning smell from power cables, or an overcurrent that disappears when the motor is disconnected.</p>
<h2>Professional checks and safety</h2>
<ul>
<li>Disconnect the motor from the drive before insulation-resistance testing with a megohmmeter.</li>
<li>Inspect the cable between the drive and motor, especially in damp or vibrating environments.</li>
<li>If an overcurrent remains with no motor connected, the IGBT power module may need board-level repair.</li>
</ul>
<p>A ground fault can create shock and equipment hazards. Do not repeatedly restart the drive. ElectroGold can identify whether the issue is a sensor signal, setpoint, cable insulation, or power module fault.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Siemens drive F0015 F90 ground fault diagnostics",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "تفسیر خطای F0015 و F90 زیمنس؛ اتصال زمین یا سنسور؟ | الکتروگلد",
        "seo_title_en": "Siemens F0015 and F90 Fault Code Meaning | ElectroGold",
        "seo_description_fa": "معنی F0015 در MM440 و F90 در V20 را از خطای اتصال زمین تفکیک کنید و روش بررسی ایمن را بخوانید.",
        "seo_description_en": "Distinguish Siemens MM440 F0015 and V20 F90 from a ground fault, and review the recommended safe checks.",
    },
    {
        "slug": "siemens-drive-f0020-input-phase-loss",
        "title_en": "Siemens Drive F0020 Input Phase Loss: Step-by-Step Diagnosis",
        "excerpt_fa": "خطای F0020 را در ورودی برق، ترمینال‌ها، فیوز، کنتاکتور و پل یکسوساز درایو زیمنس بررسی کنید.",
        "excerpt_en": "Trace Siemens F0020 through the incoming supply, terminals, fuses, contactor, and drive rectifier.",
        "body_en": """
<p><strong>F0020</strong> is an input phase-loss warning on Siemens drives. It indicates that the drive may not be receiving all three phases needed to charge the DC bus. Continued operation with a missing phase can stress the rectifier diodes and capacitors.</p>
<h2>What does F0020 mean?</h2>
<p>The drive monitors its three input phases and stops if it detects a severe imbalance or a missing phase. On some G120 models, the source notes that F30011 may also be displayed for a supply-related problem.</p>
<h2>Professional troubleshooting steps</h2>
<ol>
<li><strong>Inspect connections safely:</strong> After fully isolating power, check L1, L2, and L3 terminals for looseness, arcing, discoloration, or damaged cable ends.</li>
<li><strong>Measure the supply:</strong> A qualified person should compare all phase-to-phase and phase-to-earth voltages at the drive input. The source recommends phase voltage imbalance of no more than 2%.</li>
<li><strong>Check upstream equipment:</strong> Inspect contactors, fuses, and thermal protection for an open or damaged phase.</li>
<li><strong>Assess the power stage:</strong> If the input voltage is balanced at the drive terminals but F0020 remains, the input rectifier bridge may require workshop inspection.</li>
</ol>
<h2>Do not ignore or repeatedly reset F0020</h2>
<p>Operating on two phases can overheat diodes and create DC-bus voltage fluctuations, potentially damaging the IGBT module. ElectroGold offers hardware diagnostics, power-quality checks, and specialist repair for Siemens drives.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Siemens drive F0020 input phase loss rectifier repair",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "عیب‌یابی خطای F0020 درایو زیمنس؛ قطع فاز ورودی | الکتروگلد",
        "seo_title_en": "Siemens Drive F0020 Input Phase Loss | ElectroGold",
        "seo_description_fa": "برای رفع F0020 زیمنس، ولتاژ سه‌فاز، ترمینال‌های L1 تا L3، فیوز و کنتاکتور و پل دیود را بررسی کنید.",
        "seo_description_en": "Troubleshoot Siemens F0020 by checking three-phase voltage, L1-L3 terminals, fuses, contactors, and the rectifier.",
    },
    {
        "slug": "siemens-drive-f0021-output-phase-loss",
        "title_en": "Siemens Drive F0021 Output Phase Loss: Motor Connection Checks",
        "excerpt_fa": "خطای F0021 به فاز خروجی مربوط است؛ کابل، موتور و IGBT را بررسی کنید و آن را با F0020 ورودی اشتباه نگیرید.",
        "excerpt_en": "F0021 concerns the output phase. Check the motor cable, motor, and IGBTs, and distinguish it from input fault F0020.",
        "body_en": """
<p><strong>F0021</strong> indicates output phase loss on Siemens drives: current on one of the U, V, or W phases may be absent or severely unbalanced. Unlike F0020, which concerns the input, F0021 points to the motor, motor cable, or drive output stage.</p>
<h2>Step-by-step checks</h2>
<h3>Inspect connections</h3>
<p>Before any work, isolate the supply and ensure the DC-bus capacitors are discharged. Check the drive's U/V/W terminals and the motor terminal box for loose wires, discoloration, or signs of burning.</p>
<h3>Check the cable and motor</h3>
<p>Disconnect the motor cable from the inverter. Use an appropriate meter to compare winding resistance; the three phases should be consistent. Check cable continuity if an internal break is suspected.</p>
<h3>Megohmmeter warning</h3>
<p>Never insulation-test the inverter output terminals with a megohmmeter. Its high test voltage can destroy IGBTs and power boards. Disconnect the motor cable from the drive before testing the motor insulation.</p>
<h3>Drive inspection</h3>
<p>If the connections, cable, and motor are sound, an output IGBT or related power component may have failed and requires specialist workshop testing.</p>
<h2>F0020 versus F0021</h2>
<p>F0020 points to the incoming L1/L2/L3 supply; F0021 indicates a problem delivering power from the inverter to the motor. ElectroGold can test gate drivers and replace damaged industrial power modules.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Siemens drive F0021 output phase loss motor cable diagnostics",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "رفع خطای F0021 زیمنس؛ قطع فاز خروجی موتور | الکتروگلد",
        "seo_title_en": "Siemens F0021 Output Phase Loss Diagnosis | ElectroGold",
        "seo_description_fa": "تفاوت F0021 خروجی با F0020 ورودی را بدانید؛ کابل، موتور، ترمینال U/V/W و IGBT را ایمن بررسی کنید.",
        "seo_description_en": "Distinguish Siemens F0021 output loss from F0020 input loss and safely check the motor, cable, U/V/W terminals, and IGBTs.",
    },
    {
        "slug": "siemens-drive-f0085-external-fault",
        "title_en": "Siemens Drive F0085 External Fault: Tracing the Trigger Signal",
        "excerpt_fa": "برای عیب‌یابی F0085 زیمنس، ورودی دیجیتال، سنسورها، PLC، سیم‌کشی فرمان و ولتاژ ۲۴ ولت را بررسی کنید.",
        "excerpt_en": "Trace Siemens F0085 through the digital input, sensors, PLC, control wiring, and 24-volt supply.",
        "body_en": """
<p>When a Siemens inverter displays <strong>F0085 (External Fault)</strong>, it is reporting that one of its digital inputs has received a fault signal. An external device—such as a safety relay, pressure sensor, main controller, or emergency-stop circuit—may have requested a stop because it detected an unsafe condition.</p>
<h2>Why can F0085 occur?</h2>
<p>Examples of external signals include an oil-flow sensor stopping a motor when pressure falls, a motor thermostat responding to overheating, or a guard-door switch reporting that a safety door is open.</p>
<h2>Trace the signal instead of repairing the drive blindly</h2>
<h3>Identify the configured input</h3>
<p>On many Siemens models, including MM440 and G120, an external fault is assigned to a digital input. Check the input parameters (for example P0701-P0708) and identify which input is configured for External Fault (listed as function 29 in the source).</p>
<h3>Check connected equipment</h3>
<p>Inspect safety relays, thermal switches, level sensors, and temperature controllers. If a sensor is the cause, the inverter may be operating correctly until the sensor is repaired or reset.</p>
<h3>Review wiring, noise, and the 24 V supply</h3>
<p>Control wiring routed beside motor power cables may pick up electromagnetic noise. Check cable shielding and verify that the digital-input 24 V supply is stable.</p>
<h2>Safety warning</h2>
<p>Do not jumper digital inputs to suppress F0085. This can defeat the machine's safety system. ElectroGold can review the control wiring and input parameters to locate the external signal that triggered the fault.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Siemens inverter F0085 external fault digital input PLC diagnostics",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "عیب‌یابی خطای F0085 درایو زیمنس؛ خطای خارجی | الکتروگلد",
        "seo_title_en": "Siemens Drive F0085 External Fault | ElectroGold",
        "seo_description_fa": "منبع فرمان F0085 زیمنس را در ورودی دیجیتال، PLC، رله ایمنی، سنسورها و سیم‌کشی پیدا کنید؛ ورودی را جامپر نکنید.",
        "seo_description_en": "Trace Siemens F0085 to its digital input, PLC, safety relay, sensors, or wiring. Do not jumper the input.",
    },
]

for _article in SIEMENS_ERROR_ARTICLES:
    _article["brands"] = ["siemens"]

_source_articles = json.loads(
    Path(__file__).with_name("siemens_error_articles_source.json").read_text(encoding="utf-8")
)
for _article in SIEMENS_ERROR_ARTICLES:
    _article.update(_source_articles[_article["slug"]])
