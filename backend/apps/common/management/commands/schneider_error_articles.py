"""Bilingual Schneider fault articles based on the supplied DOCX files.

Persian titles and body text are loaded verbatim from the source documents.
"""

import json
from pathlib import Path


SCHNEIDER_ERROR_ARTICLES = [
    {
        "slug": "schneider-drive-lff",
        "title_en": "Schneider Drive LFF Fault: Low-Frequency and Speed-Control Issues",
        "excerpt_fa": "راهنمای خطای LFF اشنایدر و بررسی بار مکانیکی، پارامترهای کنترل فرکانس و فیدبک انکودر.",
        "excerpt_en": "A guide to Schneider LFF faults, including checks for mechanical load, frequency-control settings, and encoder feedback.",
        "body_en": """
<p>The supplied article describes <strong>LFF (Low Frequency Fault)</strong> as an output-frequency drop below the configured limit. In a production line, this may stop equipment, cause motor vibration, and affect products in process.</p>
<h2>What can cause LFF?</h2>
<ul>
<li><strong>Mechanical overload:</strong> A load heavier than the motor and drive are designed for may place the output under strain.</li>
<li><strong>Incorrect parameters:</strong> Frequency-control settings or the permitted frequency range may not match the application.</li>
<li><strong>Feedback issues:</strong> On closed-loop drives, an encoder signal fault can make the drive misread motor speed.</li>
</ul>
<h2>Why address the fault promptly?</h2>
<p>Frequency fluctuations may cause mechanical vibration, motor heating, and unplanned production stops. ElectroGold can check harmonics and frequency stability, assess the mechanical load, and review PID and V/f control settings.</p>
<p>Call our experts to discuss Schneider drive diagnostics and restore stable operation.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Schneider Altivar LFF low frequency drive diagnostics",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "رفع خطای LFF در اینورتر اشنایدر | الکتروگلد",
        "seo_title_en": "Schneider LFF Low-Frequency Fault Diagnosis | ElectroGold",
        "seo_description_fa": "علت خطای LFF اشنایدر را در بار مکانیکی، تنظیمات فرکانس و فیدبک انکودر بررسی کنید.",
        "seo_description_en": "Troubleshoot Schneider LFF by checking mechanical load, frequency settings, and encoder feedback.",
    },
    {
        "slug": "schneider-drive-ocf",
        "title_en": "Schneider Altivar OCF Overcurrent: Root-Cause Diagnosis",
        "excerpt_fa": "خطای OCF را از روی زمان وقوع، بار، پارامترهای موتور، کابل، سنسور جریان و برد قدرت ریشه‌یابی کنید.",
        "excerpt_en": "Diagnose Schneider OCF by considering when it occurs and checking the load, motor parameters, cabling, current sensing, and power stage.",
        "body_en": """
<p><strong>OCF (Overcurrent Fault)</strong> is a protection response, not necessarily the underlying fault. Repeated resets or replacing an IGBT without finding the cause may turn a repairable issue into a major power-stage failure.</p>
<h2>When does OCF occur?</h2>
<ul>
<li><strong>OCF1, during startup or acceleration:</strong> Possible causes include a jammed load, aggressive acceleration, incorrect motor parameters, or an output short.</li>
<li><strong>OCF2, during deceleration or braking:</strong> Regenerative energy, a short deceleration ramp, or a braking-circuit issue may be involved.</li>
<li><strong>OCF3, at steady speed:</strong> Check for sustained or varying overload, mechanical deterioration, or current-sensing problems.</li>
</ul>
<h2>Possible root causes</h2>
<p>Investigate the mechanical load first, then motor nameplate and drive settings, motor and cable insulation, and finally the IGBT, gate-driver, and current-sensor circuits. A false current-sensor reading can trip an otherwise functional drive.</p>
<h2>Safety and specialist testing</h2>
<p>Isolate the supply and safely discharge the DC bus before inspection. Never apply a megohmmeter to the inverter terminals; insulation testing is only for the motor and cable when disconnected from the drive. ElectroGold can analyze gate waveforms, current-sensor readings, and operation under controlled load. Call our experts before repeated resets cause further damage.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Schneider Altivar OCF overcurrent IGBT drive repair",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "عیب‌یابی تخصصی خطای OCF اشنایدر | الکتروگلد",
        "seo_title_en": "Schneider OCF Overcurrent Fault Diagnosis | ElectroGold",
        "seo_description_fa": "خطای OCF اشنایدر را بر اساس زمان وقوع و با بررسی بار، موتور، کابل، سنسور جریان و IGBT عیب‌یابی کنید.",
        "seo_description_en": "Diagnose Schneider OCF by trip timing and checks of the load, motor, cable, current sensor, and IGBT stage.",
    },
    {
        "slug": "schneider-drive-ohf",
        "title_en": "Schneider Inverter OHF Fault: Overheating and Cooling Checks",
        "excerpt_fa": "برای عیب‌یابی OHF اشنایدر، فن، مسیر هوا، هیت‌سینک، بار و سنسورهای حرارتی را بررسی کنید.",
        "excerpt_en": "Check the fan, airflow, heatsink, load, and temperature sensors when a Schneider drive reports OHF.",
        "body_en": """
<p><strong>OHF (Overheat)</strong> indicates excessive temperature in the drive, commonly at the heatsink or power modules. Repeated overheating stresses IGBTs and can shorten the drive's service life.</p>
<h2>Possible causes</h2>
<ul>
<li>Dust on fans or blocked airflow paths.</li>
<li>A failed internal cooling fan or reduced heatsink performance.</li>
<li>High ambient temperature or inadequate ventilation.</li>
<li>Excessive current or a fault in the internal temperature-control circuit.</li>
</ul>
<h2>When to seek specialist service</h2>
<p>If cleaning filters and checking airflow do not resolve OHF, the temperature sensor or power components may need inspection. ElectroGold can test the thermal sensors, fans, and cooling circuits. Call our experts before continued overheating damages the drive.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Schneider Altivar OHF overheating fan heatsink repair",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "رفع خطای OHF در اینورتر اشنایدر | الکتروگلد",
        "seo_title_en": "Schneider OHF Overheat Fault Diagnosis | ElectroGold",
        "seo_description_fa": "فن، هیت‌سینک، تهویه، بار کاری و سنسور دما را برای رفع خطای OHF اشنایدر بررسی کنید.",
        "seo_description_en": "Check the fan, heatsink, ventilation, load, and temperature sensor to troubleshoot Schneider OHF.",
    },
    {
        "slug": "schneider-drive-olf",
        "title_en": "Schneider Inverter OLF Motor Overload: Diagnosis and Prevention",
        "excerpt_fa": "خطای OLF اشنایدر را با بررسی بار مکانیکی، تنظیمات جریان موتور، عایق سیم‌پیچ و جریان درایو پیگیری کنید.",
        "excerpt_en": "Troubleshoot Schneider OLF by checking the mechanical load, motor-current settings, winding insulation, and drive current.",
        "body_en": """
<p><strong>OLF (Motor Overload)</strong> occurs when motor current remains above its permitted setpoint for too long. The drive stops to protect the motor and equipment.</p>
<h2>Why can OLF occur?</h2>
<ul>
<li>A jam or excessive friction in the gearbox, bearings, belt, or driven equipment.</li>
<li>Incorrect motor-current parameters or a sudden increase in the process load.</li>
<li>Winding-insulation problems or a supply-voltage drop that increases current demand.</li>
</ul>
<h2>Do not simply reset the drive</h2>
<p>Repeated operation under overload can overheat motor windings and stress the drive's IGBTs. ElectroGold checks the mechanical system, motor parameters, current profile, and drive current-control circuit. Call our experts if OLF continues after the external load and settings are checked.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Schneider Altivar OLF motor overload diagnostics",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "رفع خطای OLF اشنایدر؛ اضافه‌بار موتور | الکتروگلد",
        "seo_title_en": "Schneider OLF Motor Overload Diagnosis | ElectroGold",
        "seo_description_fa": "علت خطای OLF را در بار مکانیکی، پارامتر جریان موتور، سیم‌پیچ و شرایط تغذیه بررسی کنید.",
        "seo_description_en": "Check mechanical load, motor-current settings, winding condition, and supply voltage for Schneider OLF.",
    },
    {
        "slug": "schneider-drive-osf",
        "title_en": "Schneider Inverter OSF Overvoltage: DC-Bus Causes and Checks",
        "excerpt_fa": "علت خطای OSF اشنایدر را در انرژی برگشتی، ترمز، ولتاژ شبکه و مدار باس DC بررسی کنید.",
        "excerpt_en": "Check regenerative energy, braking, the supply voltage, and DC-bus circuitry when troubleshooting Schneider OSF.",
        "body_en": """
<p><strong>OSF (Over-voltage Fault)</strong> indicates that the drive's DC-bus voltage has exceeded its permitted limit. It can occur rapidly and may damage IGBTs, DC-bus capacitors, or control electronics.</p>
<h2>Potential causes</h2>
<ul>
<li>Regenerative energy returned by the motor during sudden stopping or braking.</li>
<li>Input-supply voltage fluctuations.</li>
<li>A faulty braking resistor or braking circuit.</li>
<li>An internal voltage-control fault.</li>
</ul>
<h2>Do not repeatedly restart after OSF</h2>
<p>Repeated restarts can expose the drive to further electrical stress. ElectroGold checks braking behavior, capacitor health, and the DC-bus power circuitry to identify the cause. Call our technical team for Schneider OSF diagnostics.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Schneider inverter OSF DC bus overvoltage braking repair",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "رفع خطای OSF اشنایدر؛ اضافه‌ولتاژ باس DC | الکتروگلد",
        "seo_title_en": "Schneider OSF DC-Bus Overvoltage Diagnosis | ElectroGold",
        "seo_description_fa": "خطای OSF اشنایدر را با بررسی ولتاژ ورودی، انرژی برگشتی، مقاومت ترمز و خازن‌های باس عیب‌یابی کنید.",
        "seo_description_en": "Troubleshoot Schneider OSF by checking supply voltage, regenerative energy, braking resistance, and DC-bus capacitors.",
    },
    {
        "slug": "schneider-drive-phf",
        "title_en": "Schneider Inverter PHF Input Phase Fault: Causes and Diagnosis",
        "excerpt_fa": "خطای PHF اشنایدر را در برق ورودی، پل رکتیفایر، موتور و کابل‌ها مرحله‌به‌مرحله بررسی کنید.",
        "excerpt_en": "Trace Schneider PHF through the input supply, rectifier bridge, motor, and cabling.",
        "body_en": """
<p>The supplied article describes <strong>PHF</strong> as a phase-balance or input-power warning. Depending on the installation, the cause may be the supply, the drive's rectifier, or connected motor and cable equipment.</p>
<h2>Why PHF should not be ignored</h2>
<p>Phase imbalance can overload rectifier diodes, affect motor current, and stop a production line. Repeated resets may turn a minor supply issue into damage to the drive or motor.</p>
<h2>Possible sources</h2>
<ul>
<li>A missing or unstable input phase.</li>
<li>A damaged rectifier bridge or internal power-board component.</li>
<li>A motor-cable or winding fault that disrupts current balance.</li>
</ul>
<h2>Specialist diagnostics</h2>
<p>A qualified technician should distinguish an external supply fault from an internal power-stage issue using suitable test equipment. ElectroGold can locate the source and restore the drive. Call our experts for Schneider PHF support.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Schneider inverter PHF phase fault rectifier diagnostics",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "عیب‌یابی خطای PHF اینورتر اشنایدر | الکتروگلد",
        "seo_title_en": "Schneider PHF Phase Fault Diagnosis | ElectroGold",
        "seo_description_fa": "برای رفع PHF اشنایدر، تعادل فاز ورودی، پل رکتیفایر، موتور و کابل‌ها را بررسی کنید.",
        "seo_description_en": "Troubleshoot Schneider PHF by checking input phase balance, the rectifier, motor, and cabling.",
    },
    {
        "slug": "schneider-drive-scf",
        "title_en": "Schneider Inverter SCF Short-Circuit Fault: Safe Troubleshooting",
        "excerpt_fa": "خطای SCF اشنایدر می‌تواند از کابل، موتور، IGBT یا مدار تشخیص جریان باشد؛ از ریست مکرر خودداری کنید.",
        "excerpt_en": "Schneider SCF may involve the cable, motor, IGBTs, or current-detection circuit. Avoid repeated resets.",
        "body_en": """
<p><strong>SCF (Short Circuit Fault)</strong> means the drive has detected a short circuit at its output. Repeatedly resetting the drive can damage its power module, DC bus, and control board.</p>
<h2>Possible causes</h2>
<ul>
<li>Damaged insulation or loose connections in the motor cable.</li>
<li>A shorted motor winding or moisture-related insulation failure.</li>
<li>A failed IGBT, output power circuit, or current-detection circuit inside the drive.</li>
</ul>
<h2>When to seek specialist repair</h2>
<p>If the motor and cables have been checked and SCF remains, the drive needs workshop testing. ElectroGold can test the output, analyze the power board, and replace defective components. Call our technical team instead of attempting repeated restarts.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Schneider inverter SCF short circuit IGBT repair",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "رفع خطای SCF اشنایدر؛ اتصال کوتاه خروجی | الکتروگلد",
        "seo_title_en": "Schneider SCF Short-Circuit Fault Diagnosis | ElectroGold",
        "seo_description_fa": "علت خطای SCF اشنایدر را در کابل موتور، سیم‌پیچ، IGBT و مدار تشخیص جریان پیدا کنید.",
        "seo_description_en": "Check the motor cable, winding, IGBTs, and current-detection circuit when troubleshooting Schneider SCF.",
    },
    {
        "slug": "schneider-drive-ssf",
        "title_en": "Schneider Drive SSF Speed-Sensor Fault: Encoder and Feedback Checks",
        "excerpt_fa": "خطای SSF اشنایدر را با بررسی انکودر، کابل سیگنال، نویز و کارت‌های ارتباطی عیب‌یابی کنید.",
        "excerpt_en": "Troubleshoot Schneider SSF by checking the encoder, signal cable, electrical noise, and communication cards.",
        "body_en": """
<p><strong>SSF (Speed Sensor Fault)</strong> indicates that the drive cannot read a valid motor-speed signal. On closed-loop systems, the sensor is commonly an encoder, and the drive stops when its feedback becomes unavailable or unreliable.</p>
<h2>Potential consequences and causes</h2>
<ul>
<li>Uncontrolled speed or vibration if commanded and measured speeds do not match.</li>
<li>Electrical noise coupling from motor-power wiring into the encoder cable.</li>
<li>A damaged encoder, loose control terminals, or a faulty communication card.</li>
</ul>
<h2>Why specialist testing matters</h2>
<p>Accurate diagnosis requires checking both the sensor and the full signal path. ElectroGold can test encoder signals and drive communication circuits to prevent repeat SSF stops. Call our experts for Schneider motion-control diagnostics.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Schneider drive SSF encoder speed sensor fault repair",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "رفع خطای SSF اشنایدر؛ خرابی سنسور سرعت | الکتروگلد",
        "seo_title_en": "Schneider SSF Speed-Sensor Fault Diagnosis | ElectroGold",
        "seo_description_fa": "خطای SSF اشنایدر را در انکودر، کابل فیدبک، اتصالات کنترلی و کارت ارتباطی بررسی کنید.",
        "seo_description_en": "Diagnose Schneider SSF by checking the encoder, feedback cable, control terminals, and communication card.",
    },
    {
        "slug": "schneider-drive-thf",
        "title_en": "Schneider Drive THF Fault: Input Power-Quality and High-Frequency Noise",
        "excerpt_fa": "برای عیب‌یابی THF اشنایدر، کیفیت توان، نویز تجهیزات مجاور، ارتینگ و فیلتر ورودی را بررسی کنید.",
        "excerpt_en": "Check power quality, nearby equipment noise, grounding, and input filters when troubleshooting Schneider THF.",
        "body_en": """
<p>The supplied article describes <strong>THF (Terminal High Frequency / Voltage Fluctuation)</strong> as high-frequency disturbance or abnormal fluctuation at the drive input. Such disturbance may affect DC-bus stability and trigger protective shutdown.</p>
<h2>Possible sources</h2>
<ul>
<li>Electrical noise from large motors, welding equipment, or nearby machinery.</li>
<li>Weak or incorrect grounding that allows interference into the drive input.</li>
<li>A damaged EMI/RFI input filter.</li>
<li>Unstable power from an industrial generator or supply network.</li>
</ul>
<h2>Power-quality diagnostics</h2>
<p>Repeatedly resetting the drive will not remove the source of interference. ElectroGold can analyze input power quality and recommend practical corrections, including suitable filters or grounding improvements. Call our experts to protect your drive and production line.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Schneider inverter THF power quality EMC filter diagnostics",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "عیب‌یابی خطای THF درایو اشنایدر | الکتروگلد",
        "seo_title_en": "Schneider THF Input Power-Quality Diagnosis | ElectroGold",
        "seo_description_fa": "خطای THF اشنایدر را با بررسی نویز، ارتینگ، فیلتر EMI/RFI و کیفیت برق ورودی عیب‌یابی کنید.",
        "seo_description_en": "Troubleshoot Schneider THF by checking electrical noise, grounding, EMI/RFI filters, and input power quality.",
    },
    {
        "slug": "schneider-drive-usf",
        "title_en": "Schneider Inverter USF Undervoltage: DC-Bus and Supply Checks",
        "excerpt_fa": "خطای USF اشنایدر را در ولتاژ شبکه، اتصالات، مدار پیش‌شارژ و خازن‌های باس DC ریشه‌یابی کنید.",
        "excerpt_en": "Trace Schneider USF through the supply voltage, connections, pre-charge circuit, and DC-bus capacitors.",
        "body_en": """
<p><strong>USF (Under-voltage Fault)</strong> occurs when the drive's DC-link voltage falls below its permitted level. Repeated resets can add stress to the pre-charge circuit and electrolytic capacitors.</p>
<h2>Common causes</h2>
<ul>
<li>An unstable or low-voltage supply, including voltage drop along a long cable run.</li>
<li>A faulty internal pre-charge relay or contactor.</li>
<li>Aged DC-bus capacitors with reduced capacity.</li>
<li>Loose input terminals that cause voltage drop during motor startup.</li>
</ul>
<h2>Specialist troubleshooting</h2>
<p>First have the input supply and connections checked. If USF persists, the pre-charge circuit, capacitors, and rectifier may need workshop testing. Internal DC circuits can retain hazardous voltage after shutdown. ElectroGold can assess the power quality and repair the drive; call our experts before repeated operation causes further damage.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Schneider inverter USF undervoltage DC bus precharge repair",
        "services": ["industrial-inverter-repair"], "brands": [],
        "seo_title_fa": "رفع خطای USF اشنایدر؛ افت ولتاژ باس DC | الکتروگلد",
        "seo_title_en": "Schneider USF DC-Bus Undervoltage Diagnosis | ElectroGold",
        "seo_description_fa": "برای رفع USF اشنایدر، برق ورودی، اتصالات، مدار پیش‌شارژ و ظرفیت خازن‌های DC را بررسی کنید.",
        "seo_description_en": "Troubleshoot Schneider USF by checking input power, connections, pre-charge, and DC-link capacitor capacity.",
    },
]

for _article in SCHNEIDER_ERROR_ARTICLES:
    _article["brands"] = ["schneider"]

_source_articles = json.loads(
    Path(__file__).with_name("schneider_error_articles_source.json").read_text(encoding="utf-8")
)
for _article in SCHNEIDER_ERROR_ARTICLES:
    _article.update(_source_articles[_article["slug"]])
