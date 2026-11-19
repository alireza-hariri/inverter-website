"""Bilingual INVT inverter fault articles based on supplied Word documents."""

import html
import json
import re
from pathlib import Path


INVT_ERROR_ARTICLES = [
    {
        "slug": "invt-drive-overcurrent-oc",
        "title_en": "INVT Inverter OC (Overcurrent): Causes and Repair",
        "excerpt_fa": "علت‌های خطای OC اینوت، از بار و تنظیمات موتور تا کابل و بخش قدرت درایو را بررسی کنید.",
        "excerpt_en": "Review common INVT OC causes, from motor load and settings to cabling and the drive power stage.",
        "body_en": """
<p>An <strong>OC (Overcurrent)</strong> indication means current has exceeded the limit monitored by the drive. The exact protection behavior varies by INVT model. A heavy or jammed load, rapid acceleration, incorrect motor data, damaged cabling or an internal power-stage fault may contribute.</p>
<h2>How the fault is diagnosed</h2>
<p>Record when the fault occurs and the drive model. A qualified technician checks the motor and output cable, load conditions and motor parameters before assessing the drive's power components, including IGBTs where appropriate.</p>
<h2>Repair and safety</h2>
<p>Repeated resets do not fix the cause and may increase damage. Isolate and inspect the equipment only using the manufacturer's safe-work procedure; internal testing belongs to a qualified repairer. The repaired drive should be function-tested before return.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "INVT drive overcurrent OC inverter repair",
        "services": ["industrial-inverter-repair"], "brands": ["inovance"],
        "seo_title_fa": "رفع خطای OC اینورتر اینوت | الکتروگلد",
        "seo_title_en": "INVT Inverter OC Fault Diagnosis & Repair | ElectroGold",
        "seo_description_fa": "عیب‌یابی خطای OC اینوت با بررسی بار، تنظیمات موتور، کابل خروجی و بخش قدرت درایو.",
        "seo_description_en": "INVT OC fault diagnosis covering load, motor settings, output cabling and the drive power stage.",
    },
    {
        "slug": "invt-drive-communication-error",
        "title_en": "INVT Drive Communication Error: Network and Port Troubleshooting",
        "excerpt_fa": "علت‌های Communication Error اینوت و بررسی کابل، تنظیمات پروتکل، آدرس شبکه و پورت ارتباطی.",
        "excerpt_en": "Troubleshoot INVT communication faults by checking wiring, protocol settings, network addresses and ports.",
        "body_en": """
<p>A communication error can occur when data between an INVT drive and a controller is delayed, corrupted or not received. The exact message and supported protocol depend on the drive and communication option.</p>
<h2>Common causes</h2>
<ul><li>Damaged, unsuitable or poorly shielded communication cable, especially when routed beside motor-power wiring.</li><li>Mismatched baud rate, parity, stop bits or station address between the drive and PLC/HMI.</li><li>Duplicate network addresses, grounding or noise problems, or a faulty communication card or port.</li></ul>
<h2>Checks and repair</h2>
<p>A technician checks cable condition and routing, compares settings with the equipment manuals and confirms each device has a unique address. If the wiring and configuration are correct, the communication interface may need workshop diagnosis. Do not open powered equipment; follow the manufacturer's isolation procedure.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "INVT inverter communication error RS485 repair",
        "services": ["industrial-inverter-repair"], "brands": ["inovance"],
        "seo_title_fa": "رفع خطای Communication اینورتر اینوت | الکتروگلد",
        "seo_title_en": "INVT Communication Error Troubleshooting | ElectroGold",
        "seo_description_fa": "بررسی خطای ارتباط اینوت از کابل و نویز تا تنظیمات شبکه، آدرس‌دهی و کارت ارتباطی.",
        "seo_description_en": "Diagnose INVT communication faults involving cabling, noise, network settings, addressing and interface hardware.",
    },
    {
        "slug": "invt-drive-encoder-error",
        "title_en": "INVT Encoder Error: Feedback Signal Diagnosis and Repair",
        "excerpt_fa": "عیب‌یابی خطای انکودر اینوت با بررسی کابل و سیگنال بازخورد، تنظیمات و اتصال مکانیکی.",
        "excerpt_en": "Diagnose INVT encoder errors by checking feedback wiring, signal settings and the encoder assembly.",
        "body_en": """
<p>An encoder error may appear when an INVT drive in closed-loop operation receives missing, noisy or unexpected speed/position feedback. The correct checks depend on the drive, encoder type and control configuration.</p>
<h2>Possible causes and checks</h2>
<p>Common causes include loose or damaged encoder wiring, electromagnetic interference, an encoder or connector fault, grounding issues, or mismatched encoder type, resolution or signal settings. A qualified technician checks connections at both ends, cable shielding and routing, the configured feedback data and the signal itself.</p>
<h2>Safety and repair</h2>
<p>Feedback faults can affect motion control. Put the machine in a safe state before inspection and do not bypass encoder protection. If the cable and settings are sound, the encoder interface or drive control board may require specialist testing and calibration.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "INVT encoder feedback error drive repair",
        "services": ["industrial-inverter-repair", "elevator-inverter-repair"], "brands": ["inovance"],
        "seo_title_fa": "عیب‌یابی خطای Encoder اینورتر اینوت | الکتروگلد",
        "seo_title_en": "INVT Encoder Error Diagnosis and Repair | ElectroGold",
        "seo_description_fa": "بررسی خطای Encoder در درایو اینوت، از کابل و نویز تا تنظیمات انکودر و برد کنترل.",
        "seo_description_en": "INVT encoder-error checks for feedback wiring, interference, encoder settings and drive control hardware.",
    },
    {
        "slug": "invt-drive-ground-fault-gf",
        "title_en": "INVT Ground Fault (GF): Safe Diagnosis of Leakage Faults",
        "excerpt_fa": "علت‌های احتمالی GF اینوت در کابل، موتور، اتصال زمین یا بخش قدرت و نکات ایمنی بررسی را بخوانید.",
        "excerpt_en": "Learn possible INVT GF causes in the motor, cable, grounding or power stage—and key safety precautions.",
        "body_en": """
<p>A <strong>Ground Fault (GF)</strong> indication may mean the drive has detected leakage or an abnormal path to earth. The code and detection method differ by model, so consult the relevant INVT manual.</p>
<h2>Possible causes</h2>
<ul><li>Damaged insulation in the motor cable or motor winding.</li><li>Moisture or conductive contamination around terminals or power components.</li><li>A grounding problem, current-sensing issue or internal power-stage fault.</li></ul>
<h2>Professional diagnosis and safety</h2>
<p>A qualified technician isolates the system and checks the motor and cable using equipment suitable for the installation. Insulation testing must never be applied through a connected inverter. If external wiring and the motor are sound, the drive's output stage and sensing circuits may need workshop testing. Do not defeat grounding or protection, and do not open the drive until it has been safely isolated and discharged.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "INVT inverter ground fault GF repair workshop",
        "services": ["industrial-inverter-repair"], "brands": ["inovance"],
        "seo_title_fa": "رفع خطای Ground Fault اینورتر اینوت | الکتروگلد",
        "seo_title_en": "INVT Ground Fault Diagnosis and Repair | ElectroGold",
        "seo_description_fa": "عیب‌یابی ایمن خطای GF اینوت با بررسی عایق موتور و کابل، اتصال زمین و بخش قدرت.",
        "seo_description_en": "Safe INVT GF diagnosis covering motor and cable insulation, grounding and the drive power stage.",
    },
    {
        "slug": "invt-drive-internal-error",
        "title_en": "INVT Internal Error (Err): Control Board and Drive Diagnosis",
        "excerpt_fa": "خطای داخلی Err اینوت می‌تواند به برد کنترل، تغذیه داخلی یا نوسان برق مربوط باشد؛ عیب‌یابی تخصصی لازم است.",
        "excerpt_en": "INVT Err may involve the control board, internal supply or power disturbances and may require workshop diagnosis.",
        "body_en": """
<p>An <strong>Err/Internal Error</strong> message can indicate an internal drive condition, but its meaning is model-specific. Possible areas include the control board, internal low-voltage supply, memory or supporting circuits; external supply disturbances can also contribute.</p>
<h2>What to record and check</h2>
<p>Note the exact model, displayed code, fault history and conditions when the error appears. Check the supply and operating environment against the manual. A single restart should only be considered if the manufacturer's instructions allow it; repeated power cycling is not a repair.</p>
<h2>When workshop repair is needed</h2>
<p>If the fault returns or the drive behaves unpredictably, stop using it and have a qualified technician test the control and power sections. Internal circuits can retain hazardous voltage after shutdown. Do not open or probe the drive without proper training and discharge verification.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "INVT drive internal error control board diagnosis",
        "services": ["industrial-inverter-repair"], "brands": ["inovance"],
        "seo_title_fa": "عیب‌یابی خطای داخلی Err اینورتر اینوت | الکتروگلد",
        "seo_title_en": "INVT Internal Err Fault Diagnosis | ElectroGold",
        "seo_description_fa": "بررسی خطای داخلی Err اینوت و ارزیابی برد کنترل، تغذیه داخلی و شرایط برق ورودی.",
        "seo_description_en": "Diagnose INVT Err faults by assessing the control board, internal supply and incoming power conditions.",
    },
    {
        "slug": "invt-drive-overheating-oh",
        "title_en": "INVT Overheating (OH): Cooling and Load Fault Diagnosis",
        "excerpt_fa": "خطای OH اینوت را با بررسی فن، مسیر هوا، دمای تابلو و میزان بار دستگاه ریشه‌یابی کنید.",
        "excerpt_en": "Trace INVT OH faults by checking the fan, airflow, cabinet temperature and operating load.",
        "body_en": """
<p>An <strong>OH/Overheating</strong> fault means a temperature sensor or protection function has detected excessive heat. Exact thresholds depend on the INVT model and installation.</p>
<h2>Common causes</h2>
<ul><li>A failed fan or blocked heatsink and airflow path.</li><li>High ambient or cabinet temperature, poor ventilation or dust accumulation.</li><li>Excessive load, frequent overload operation or installation conditions outside the drive rating.</li></ul>
<h2>Diagnosis and repair</h2>
<p>After safe isolation, a technician checks the cooling path, fan operation, cabinet conditions and load history. If the fault persists after external causes are corrected, temperature sensing and power components may require workshop inspection. Avoid repeated restarts while the drive is hot.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "INVT drive overheating OH fan heatsink repair",
        "services": ["industrial-inverter-repair"], "brands": ["inovance"],
        "seo_title_fa": "رفع خطای Overheating اینورتر اینوت | الکتروگلد",
        "seo_title_en": "INVT Overheating OH Fault Diagnosis | ElectroGold",
        "seo_description_fa": "عیب‌یابی خطای OH اینوت با بررسی فن، هیت‌سینک، تهویه تابلو و بار کاری.",
        "seo_description_en": "Diagnose INVT OH faults by checking the fan, heatsink, cabinet ventilation and operating load.",
    },
    {
        "slug": "invt-drive-overload-ol",
        "title_en": "INVT Overload (OL): Motor Load and Drive Repair Checks",
        "excerpt_fa": "علت OL اینوت را از اضافه‌بار مکانیکی و پارامتر موتور تا کابل و سیم‌پیچ بررسی کنید.",
        "excerpt_en": "Investigate INVT OL faults from mechanical overload and motor settings to cabling and winding condition.",
        "body_en": """
<p>An <strong>OL (Overload)</strong> trip indicates the drive's overload protection has operated. The threshold and timing are model- and parameter-dependent; it does not by itself identify a failed drive.</p>
<h2>Possible causes</h2>
<p>Excessive mechanical load or friction, a short acceleration time, incorrect motor nameplate data, a motor or cable problem, or an application exceeding the drive rating may contribute.</p>
<h2>Diagnosis and repair</h2>
<p>Record whether OL occurs during startup or continuous operation. A technician compares motor settings with the nameplate, checks load and mechanical movement, and measures electrical conditions using appropriate equipment. Do not raise current limits or disable protection to mask the trip; the drive and motor should be tested after repair.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "INVT inverter overload OL motor drive repair",
        "services": ["industrial-inverter-repair", "elevator-inverter-repair"], "brands": ["inovance"],
        "seo_title_fa": "رفع خطای Overload اینورتر اینوت | الکتروگلد",
        "seo_title_en": "INVT Overload OL Diagnosis and Repair | ElectroGold",
        "seo_description_fa": "عیب‌یابی OL اینوت با بررسی بار مکانیکی، اطلاعات موتور، زمان شتاب و وضعیت سیم‌پیچ.",
        "seo_description_en": "INVT OL diagnosis covering mechanical load, motor data, acceleration settings and winding condition.",
    },
    {
        "slug": "invt-drive-overvoltage-ov",
        "title_en": "INVT Overvoltage (OV): DC Bus Fault Diagnosis and Repair",
        "excerpt_fa": "خطای OV اینوت می‌تواند از انرژی برگشتی، برق ورودی یا مدار ترمز باشد؛ کد و مدل دقیق را بررسی کنید.",
        "excerpt_en": "INVT OV may involve regenerative energy, input power or braking circuits; check the exact model and fault context.",
        "body_en": """
<p>An <strong>OV (Overvoltage)</strong> indication commonly means the DC-bus voltage has exceeded a protection threshold. The code behavior varies between INVT drive families; use the manual for the exact model.</p>
<h2>Possible causes</h2>
<p>Rapid deceleration or an inertial load can return energy to the DC bus. High or unstable input voltage may also contribute. On models equipped with braking hardware, the resistor, chopper and associated wiring may need inspection; internal DC-link or voltage-sensing faults are also possible.</p>
<h2>Professional diagnosis and safety</h2>
<p>Record when OV occurs and have a qualified technician check the supply, settings and braking circuit against the manual. If external causes are ruled out, the DC-link and sensing circuits need workshop testing. Do not repeatedly reset the drive or disable protection. Hazardous voltage may remain inside after power is removed.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "INVT drive overvoltage OV DC bus braking repair",
        "services": ["industrial-inverter-repair"], "brands": ["inovance"],
        "seo_title_fa": "رفع خطای Overvoltage اینورتر اینوت | الکتروگلد",
        "seo_title_en": "INVT Overvoltage OV Diagnosis and Repair | ElectroGold",
        "seo_description_fa": "بررسی خطای OV اینوت با توجه به ولتاژ ورودی، کاهش سرعت، مدار ترمز و باس DC.",
        "seo_description_en": "Diagnose INVT OV faults by checking input voltage, deceleration, braking hardware and the DC bus.",
    },
    {
        "slug": "invt-drive-phase-loss-pl",
        "title_en": "INVT Phase Loss (PL): Input and Output Phase Diagnosis",
        "excerpt_fa": "خطای PL اینوت می‌تواند در ورودی یا خروجی رخ دهد؛ فازها، فیوزها، کابل موتور و سنسورها بررسی می‌شوند.",
        "excerpt_en": "INVT PL may involve the input or output side; supply phases, fuses, motor wiring and sensors are checked.",
        "body_en": """
<p>A <strong>Phase Loss (PL)</strong> warning may refer to an input- or output-phase condition, depending on the model. Consult the drive manual before interpreting the code.</p>
<h2>Possible causes and checks</h2>
<p>Input-side causes include a missing supply phase, fuse or breaker issue, or loose connection. On the output side, a motor cable, winding, current sensor or power-module fault may be involved. Some models also use configurable phase-loss detection.</p>
<h2>Safety and repair</h2>
<p>A qualified technician checks the supply and motor circuits using rated test equipment and isolates the source before any internal inspection. Do not operate the motor with a confirmed missing phase or bypass protection. If external wiring and the motor are sound, the drive's sensing and power sections may need workshop testing.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "INVT phase loss PL inverter repair",
        "services": ["industrial-inverter-repair"], "brands": ["inovance"],
        "seo_title_fa": "عیب‌یابی خطای Phase Loss اینورتر اینوت | الکتروگلد",
        "seo_title_en": "INVT Phase Loss PL Diagnosis | ElectroGold",
        "seo_description_fa": "بررسی خطای PL اینوت در ورودی یا خروجی، همراه با ارزیابی ایمن کابل، موتور و بخش قدرت.",
        "seo_description_en": "Diagnose INVT PL input- or output-phase faults with safe checks of wiring, motor and power stage.",
    },
    {
        "slug": "invt-drive-undervoltage-uv",
        "title_en": "INVT Undervoltage (UV): DC-Link and Supply Diagnosis",
        "excerpt_fa": "عیب‌یابی UV اینوت با بررسی افت یا عدم‌تعادل برق ورودی، اتصالات، یکسوساز و خازن‌های باس DC.",
        "excerpt_en": "Troubleshoot INVT UV faults by checking supply dips, phase balance, connections, rectifier and DC-link capacitors.",
        "body_en": """
<p>An <strong>UV (Undervoltage)</strong> fault commonly indicates that the drive's DC-link voltage has fallen below its model-specific threshold. The drive may stop to protect operation.</p>
<h2>Common causes</h2>
<p>Possible causes include a supply-voltage dip, phase imbalance, loose input connections, a rectifier fault, aged DC-link capacitors or an incorrect setting. The exact diagnosis depends on the model and when the fault occurs.</p>
<h2>Diagnosis and repair</h2>
<p>A qualified technician checks the supply and connections using properly rated equipment. If those are within specification, the rectifier, DC-link capacitors and voltage-sensing circuit may need workshop assessment. Do not continue repeated restarts when UV recurs; internal measurements must be performed only by trained personnel after safe isolation and discharge.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "INVT inverter undervoltage UV DC link repair",
        "services": ["industrial-inverter-repair"], "brands": ["inovance"],
        "seo_title_fa": "رفع خطای Undervoltage اینورتر اینوت | الکتروگلد",
        "seo_title_en": "INVT Undervoltage UV Diagnosis and Repair | ElectroGold",
        "seo_description_fa": "بررسی UV اینوت با ارزیابی ولتاژ ورودی، فازها، اتصالات، یکسوساز و لینک DC.",
        "seo_description_en": "INVT UV diagnosis covering input voltage, phase balance, connections, rectifier and DC link.",
    },
]


_source_articles = json.loads(
    Path(__file__).with_name("invt_error_articles_source.json").read_text(encoding="utf-8")
)


def _format_persian_body(raw):
    """Keep source paragraphs readable and promote short section labels to headings."""
    blocks = [block.strip() for block in re.split(r"\n\s*\n", raw) if block.strip()]
    rendered = []
    for block in blocks:
        escaped = html.escape(block)
        if len(block) <= 100 and (block.endswith(":") or block.endswith("؟")):
            rendered.append(f"<h2>{escaped}</h2>")
        else:
            rendered.append(f"<p>{escaped.replace(chr(10), '<br>')}</p>")
    return "\n".join(rendered)


for _article in INVT_ERROR_ARTICLES:
    _source = _source_articles[_article["slug"]]
    _article["title_fa"] = _source["title_fa"]
    _article["body_fa"] = _format_persian_body(_source["body_fa"])
