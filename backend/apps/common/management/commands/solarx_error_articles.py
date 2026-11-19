"""Bilingual SolarX fault articles transcribed from the supplied Word files."""

import html
import json
import re
from pathlib import Path


SOLARX_ERROR_ARTICLES = [
    {
        "slug": "solarx-battery-fault",
        "title_en": "SolarX Battery Fault: Battery, BMS and Charging Diagnosis",
        "excerpt_fa": "علت خطای باتری سولارکس را در ولتاژ، اتصالات، تنظیمات شارژ یا ارتباط با BMS بررسی کنید.",
        "excerpt_en": "Diagnose SolarX battery faults involving voltage, connections, charging settings or BMS communication.",
        "body_en": """
<p>A battery fault indicates that the inverter has detected a battery voltage, current or communication condition outside its configured limits. The exact thresholds depend on the SolarX model and battery type.</p>
<h2>Common causes</h2>
<ul><li>Battery voltage outside the permitted charge or discharge range.</li><li>Loose or oxidized terminals causing resistance and voltage drop.</li><li>Incorrect battery chemistry or charging parameters.</li><li>Reduced battery capacity or a BMS fault or communication issue.</li></ul>
<h2>Diagnosis</h2>
<p>A qualified technician checks the model manual, battery specifications, connections and charge settings. For lithium systems, BMS alarms and the supported communication protocol should also be reviewed. Battery and inverter terminals can carry dangerous energy; do not work on them unless trained and safely isolated.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "SolarX solar inverter battery fault BMS repair",
        "services": ["solar-inverter-repair"], "brands": ["solarx"],
        "seo_title_fa": "عیب‌یابی خطای Battery Fault سولارکس | الکتروگلد",
        "seo_title_en": "SolarX Battery Fault Diagnosis and Repair | ElectroGold",
        "seo_description_fa": "بررسی خطای باتری سولارکس با ارزیابی ولتاژ، اتصالات، تنظیمات شارژ و هشدارهای BMS.",
        "seo_description_en": "Diagnose SolarX battery faults by checking voltage, connections, charging settings and BMS alerts.",
    },
    {
        "slug": "solarx-communication-error",
        "title_en": "SolarX Communication Error: Monitoring and Data Link Troubleshooting",
        "excerpt_fa": "عیب‌یابی قطع ارتباط سولارکس با دیتالاگر یا مانیتورینگ از طریق بررسی کابل، نویز و تنظیمات.",
        "excerpt_en": "Troubleshoot SolarX inverter links to data loggers and monitoring systems by checking wiring, noise and settings.",
        "body_en": """
<p>A Communication Error means the inverter is not exchanging data as expected with an accessory such as a data logger, monitoring unit or energy-management system. The supported interface varies by model.</p>
<h2>Possible causes</h2>
<p>Damaged or loose RS485/Ethernet wiring, electromagnetic interference, mismatched baud rate or device address, or a failed communication port or data logger can interrupt the link.</p>
<h2>Checks and repair</h2>
<p>Inspect connector and cable condition, keep data wiring routed as specified by the manufacturer, and compare protocol settings at both ends. Restart equipment only as allowed by the manual. If the wiring and settings are correct, the communication module may need workshop testing.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "SolarX inverter RS485 communication error monitoring repair",
        "services": ["solar-inverter-repair"], "brands": ["solarx"],
        "seo_title_fa": "رفع خطای Communication Error سولارکس | الکتروگلد",
        "seo_title_en": "SolarX Communication Error Troubleshooting | ElectroGold",
        "seo_description_fa": "بررسی خطای ارتباط سولارکس با دیتالاگر از نظر کابل، نویز، آدرس و تنظیمات پروتکل.",
        "seo_description_en": "Troubleshoot SolarX monitoring links by checking cabling, interference, addresses and protocol settings.",
    },
    {
        "slug": "solarx-earth-fault-ef",
        "title_en": "SolarX Earth Fault (EF): Safe Leakage Diagnosis",
        "excerpt_fa": "خطای EF سولارکس را با بررسی ایمن عایق کابل‌های DC، کانکتورها، پنل‌ها و سیستم ارت پیگیری کنید.",
        "excerpt_en": "Investigate SolarX EF faults with safe checks of PV cable insulation, connectors, modules and grounding.",
        "body_en": """
<p>An <strong>Earth Fault (EF)</strong> may indicate leakage current or an unintended path from the PV circuit to earth. The exact detection method and threshold depend on the inverter model.</p>
<h2>Possible causes</h2>
<ul><li>Damaged DC cable insulation or a fault within a PV module.</li><li>Moisture or damage in PV connectors.</li><li>Incorrect or damaged protective earthing, or an internal inverter fault.</li></ul>
<h2>Professional diagnosis and safety</h2>
<p>A qualified solar technician checks the installation, connectors and grounding and uses suitable insulation-test equipment under the manufacturer's procedure. PV strings may remain live in daylight, even when the inverter is off. Never disconnect live connectors or apply an insulation tester through a connected inverter.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "SolarX PV earth fault EF insulation repair",
        "services": ["solar-inverter-repair"], "brands": ["solarx"],
        "seo_title_fa": "عیب‌یابی خطای Earth Fault سولارکس | الکتروگلد",
        "seo_title_en": "SolarX Earth Fault EF Diagnosis | ElectroGold",
        "seo_description_fa": "عیب‌یابی ایمن EF سولارکس با بررسی عایق کابل‌های خورشیدی، کانکتورها و اتصال زمین.",
        "seo_description_en": "Safe SolarX EF diagnosis covering PV cable insulation, connectors and protective grounding.",
    },
    {
        "slug": "solarx-grid-fault-ac-error",
        "title_en": "SolarX Grid Fault / AC Error: Grid Connection Diagnosis",
        "excerpt_fa": "خطای Grid Fault سولارکس می‌تواند به ولتاژ، فرکانس، فاز، کابل یا تنظیمات شبکه مربوط باشد.",
        "excerpt_en": "SolarX Grid Fault may involve grid voltage, frequency, phase balance, wiring or configuration.",
        "body_en": """
<p>A Grid Fault or AC Error means that a grid parameter is outside the range accepted by the inverter. SolarX units must synchronize with the permitted grid voltage and frequency; exact limits depend on the model and approved local settings.</p>
<h2>Common causes</h2>
<ul><li>High, low or unstable grid voltage or frequency.</li><li>A missing or imbalanced phase in a three-phase installation.</li><li>Loose AC terminals, unsuitable cable sizing or a protective-device issue.</li><li>Incorrect grid-code settings or a fault in the inverter's measurement circuit.</li></ul>
<h2>Diagnosis and repair</h2>
<p>A qualified electrician measures the AC supply with correctly rated equipment, checks wiring and protective devices, and verifies configuration against the manual and applicable grid requirements. Do not change protection thresholds to force a connection. If the supply is normal, the inverter's sensing and control sections may need workshop diagnosis.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "SolarX solar inverter grid fault AC error repair",
        "services": ["solar-inverter-repair"], "brands": ["solarx"],
        "seo_title_fa": "رفع خطای Grid Fault و AC Error سولارکس | الکتروگلد",
        "seo_title_en": "SolarX Grid Fault and AC Error Diagnosis | ElectroGold",
        "seo_description_fa": "بررسی Grid Fault سولارکس با ارزیابی ولتاژ و فرکانس شبکه، فازها و اتصالات AC.",
        "seo_description_en": "Diagnose SolarX grid faults by checking AC voltage, frequency, phase balance and connections.",
    },
    {
        "slug": "solarx-isolation-fault-iso",
        "title_en": "SolarX Isolation Fault (ISO): PV Insulation and Leakage Checks",
        "excerpt_fa": "علت ISO سولارکس را در عایق کابل، کانکتور، پنل یا اتصال زمین با تست تخصصی پیدا کنید.",
        "excerpt_en": "Trace SolarX ISO faults to PV cable, connector, module or grounding issues using qualified testing.",
        "body_en": """
<p>An <strong>Isolation Fault (ISO)</strong> indicates that insulation monitoring has detected resistance to earth below the model's permitted limit. This is a protective warning, not a location-specific diagnosis.</p>
<h2>Possible sources</h2>
<p>UV, heat or mechanical damage can degrade DC cable insulation. Water ingress or arcing may affect connectors, and a damaged PV module or earthing problem can also contribute.</p>
<h2>Specialist diagnosis</h2>
<p>A qualified technician inspects the array and connectors and tests strings using equipment and isolation procedures approved for the installation. PV conductors can remain live under sunlight. Do not touch exposed conductors, disconnect energized connectors or connect a megohmmeter to the inverter electronics.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "SolarX inverter isolation fault ISO PV repair",
        "services": ["solar-inverter-repair"], "brands": ["solarx"],
        "seo_title_fa": "عیب‌یابی خطای Isolation Fault سولارکس | الکتروگلد",
        "seo_title_en": "SolarX Isolation Fault ISO Diagnosis | ElectroGold",
        "seo_description_fa": "بررسی خطای ISO سولارکس با ارزیابی عایق کابل‌های DC، کانکتور، پنل و سیستم ارت.",
        "seo_description_en": "Diagnose SolarX ISO faults by assessing PV cable insulation, connectors, modules and grounding.",
    },
    {
        "slug": "solarx-load-output-fault",
        "title_en": "SolarX Load/Output Fault: AC Load and Output Diagnosis",
        "excerpt_fa": "خطای Load/Output سولارکس را با بررسی اضافه‌بار، اتصال کوتاه، شبکه و مدار خروجی عیب‌یابی کنید.",
        "excerpt_en": "Diagnose SolarX Load/Output faults by checking load demand, short circuits, grid conditions and output hardware.",
        "body_en": """
<p>A Load/Output Fault points to an abnormal condition on the inverter's AC output or connected load. The exact protection represented by this message varies by SolarX model.</p>
<h2>Possible causes</h2>
<p>Connected equipment may exceed the inverter's rated output, an AC cable or load may be shorted, grid conditions may be outside limits, or the inverter's output power stage may be damaged.</p>
<h2>Checks and repair</h2>
<p>Record the code and operating conditions. A qualified technician checks the load rating, AC wiring and supply using suitable test equipment. If external circuits are within specification, the output stage and current-sensing circuits may require workshop repair. Isolate equipment safely before inspection.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "SolarX inverter load output fault AC repair",
        "services": ["solar-inverter-repair"], "brands": ["solarx"],
        "seo_title_fa": "رفع خطای Load/Output سولارکس | الکتروگلد",
        "seo_title_en": "SolarX Load/Output Fault Diagnosis | ElectroGold",
        "seo_description_fa": "عیب‌یابی Load/Output سولارکس با بررسی بار، کابل AC، وضعیت شبکه و بخش خروجی دستگاه.",
        "seo_description_en": "Troubleshoot SolarX output faults by checking load, AC wiring, grid conditions and output hardware.",
    },
    {
        "slug": "solarx-overcurrent-oc",
        "title_en": "SolarX Overcurrent (OC): DC and AC Current Fault Diagnosis",
        "excerpt_fa": "برای خطای OC سولارکس، مسیرهای DC و AC، استرینگ‌ها، بار و سنسورهای جریان بررسی می‌شوند.",
        "excerpt_en": "SolarX OC diagnosis checks the DC and AC paths, PV strings, load and current-sensing hardware.",
        "body_en": """
<p>An <strong>Overcurrent (OC)</strong> fault means measured current has exceeded a protection limit on the DC or AC side. The code behavior and limits are model-specific.</p>
<h2>Possible causes</h2>
<p>Potential causes include a short circuit or wiring fault, abnormal string current, a load beyond rating, a protective-device issue, or a current sensor or power-stage fault.</p>
<h2>Professional checks</h2>
<p>A qualified technician identifies whether the event is on the PV or AC side, inspects wiring and protection devices, and compares measurements with the equipment ratings and manual. Do not disconnect PV connectors under load or repeatedly reset the inverter. Internal current sensors and power devices require workshop testing.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "SolarX inverter overcurrent OC DC AC fault repair",
        "services": ["solar-inverter-repair"], "brands": ["solarx"],
        "seo_title_fa": "رفع خطای Overcurrent اینورتر سولارکس | الکتروگلد",
        "seo_title_en": "SolarX Overcurrent OC Diagnosis and Repair | ElectroGold",
        "seo_description_fa": "بررسی خطای OC سولارکس در مدار DC یا AC، استرینگ، بار و سنسورهای جریان.",
        "seo_description_en": "Diagnose SolarX OC faults on DC or AC circuits, PV strings, connected loads and current sensors.",
    },
    {
        "slug": "solarx-overheating-oh",
        "title_en": "SolarX Overheating (OH): Cooling and Installation Checks",
        "excerpt_fa": "خطای OH سولارکس می‌تواند از تهویه، فن، گردوغبار، دمای محیط یا بار زیاد باشد.",
        "excerpt_en": "SolarX OH faults may involve ventilation, fans, dust, ambient temperature or excessive load.",
        "body_en": """
<p>An <strong>Overheating (OH)</strong> warning means the inverter's temperature protection has reached its model-specific limit.</p>
<h2>Common causes</h2>
<p>Blocked airflow, a failed fan, dust on cooling surfaces, direct sun or high ambient temperature can reduce cooling. Sustained operation near or above the rated load may also increase temperature.</p>
<h2>Diagnosis and repair</h2>
<p>After safe isolation, check that the installation has the clearances and ventilation required by the manual. A technician checks fans, cooling paths and load history. If overheating persists in suitable conditions, temperature sensors or power components may need workshop inspection. Avoid repeated operation while the warning remains active.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "SolarX inverter overheating OH cooling fan repair",
        "services": ["solar-inverter-repair"], "brands": ["solarx"],
        "seo_title_fa": "رفع خطای Overheating سولارکس | الکتروگلد",
        "seo_title_en": "SolarX Overheating OH Diagnosis | ElectroGold",
        "seo_description_fa": "عیب‌یابی OH سولارکس با بررسی تهویه، فن خنک‌کننده، دمای نصب و بار کاری.",
        "seo_description_en": "Diagnose SolarX OH faults by checking ventilation, cooling fans, installation temperature and load.",
    },
    {
        "slug": "solarx-pv-overvoltage",
        "title_en": "SolarX PV Overvoltage: String Voltage and Design Checks",
        "excerpt_fa": "ولتاژ بالای ورودی PV سولارکس را با بازبینی تعداد پنل‌های سری، دمای طراحی و مشخصات اینورتر بررسی کنید.",
        "excerpt_en": "Investigate SolarX PV overvoltage by reviewing series-module count, cold-weather design and inverter ratings.",
        "body_en": """
<p>A <strong>PV Overvoltage</strong> fault means the array's DC voltage may exceed the inverter's maximum PV input rating. The limit is specific to the model and must be taken from its datasheet.</p>
<h2>Common causes</h2>
<p>Too many modules in series, an incorrect string design or wiring configuration can exceed the limit. PV open-circuit voltage rises as module temperature falls, so the design must account for the site's minimum temperature.</p>
<h2>Safety and corrective action</h2>
<p>A qualified solar designer or technician compares the string design and measured values with the module and inverter specifications. Any redesign must consider the complete array and MPPT limits. PV DC voltage can be lethal and remains present in daylight; do not disconnect live connectors or measure exposed conductors without the required training and rated protection.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "SolarX PV overvoltage string design solar inverter repair",
        "services": ["solar-inverter-repair"], "brands": ["solarx"],
        "seo_title_fa": "رفع خطای PV Overvoltage سولارکس | الکتروگلد",
        "seo_title_en": "SolarX PV Overvoltage Diagnosis | ElectroGold",
        "seo_description_fa": "بررسی خطای PV OV سولارکس با تطبیق ولتاژ رشته پنل‌ها و شرایط دمایی با مشخصات اینورتر.",
        "seo_description_en": "Diagnose SolarX PV OV by comparing string voltage and temperature conditions with inverter ratings.",
    },
    {
        "slug": "solarx-pv-undervoltage",
        "title_en": "SolarX PV Undervoltage: Startup and MPPT Troubleshooting",
        "excerpt_fa": "علت PV UV سولارکس را در تابش کم، سایه، طراحی استرینگ، اتصالات یا خرابی پنل بررسی کنید.",
        "excerpt_en": "SolarX PV UV can involve low irradiance, shading, string design, connections or a module fault.",
        "body_en": """
<p>A <strong>PV Undervoltage</strong> warning may appear when PV input voltage is below the model's startup or MPPT operating range, preventing normal production.</p>
<h2>Possible causes</h2>
<p>Low irradiance at dawn, dusk or in cloudy conditions can reduce string voltage. Shading, too few modules in series, a mismatch with the inverter's input range, a weak connection or a damaged module may also contribute.</p>
<h2>Diagnosis and correction</h2>
<p>Compare the string design with the inverter and module datasheets and record the conditions when the warning appears. A qualified technician checks for shading, connectors and string performance with PV-rated equipment. Any redesign must stay within the inverter's maximum voltage and current limits. PV conductors can remain energized in daylight.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "SolarX PV undervoltage startup MPPT solar inverter diagnosis",
        "services": ["solar-inverter-repair"], "brands": ["solarx"],
        "seo_title_fa": "رفع خطای PV Undervoltage سولارکس | الکتروگلد",
        "seo_title_en": "SolarX PV Undervoltage Diagnosis | ElectroGold",
        "seo_description_fa": "عیب‌یابی PV UV سولارکس با بررسی تابش، سایه، طراحی استرینگ و اتصالات پنل.",
        "seo_description_en": "Troubleshoot SolarX PV UV by checking irradiance, shading, string design and PV connections.",
    },
]


_source_articles = json.loads(
    Path(__file__).with_name("solarx_error_articles_source.json").read_text(encoding="utf-8")
)


def _format_persian_body(raw):
    blocks = [block.strip() for block in re.split(r"\n\s*\n", raw) if block.strip()]
    rendered = []
    for block in blocks:
        escaped = html.escape(block)
        if len(block) <= 140 and (
            block.endswith((":", "؟"))
            or re.match(r"^[۰-۹0-9]+[.٫)]", block)
            or re.match(r"^[الف-ی][).]", block)
            or block.startswith("🛠")
        ):
            rendered.append(f"<h2>{escaped}</h2>")
        else:
            rendered.append(f"<p>{escaped.replace(chr(10), '<br>')}</p>")
    safety = (
        "<h2>هشدار ایمنی</h2><p>مدارهای PV و باتری می‌توانند حتی پس از خاموش‌شدن اینورتر ولتاژ خطرناک داشته باشند. "
        "بازرسی و اندازه‌گیری را فقط تکنسین واجد صلاحیت، با تجهیزات مناسب و طبق دستورالعمل سازنده انجام دهد؛ "
        "کانکتورهای DC را زیر بار جدا نکنید و تستر عایقی را به اینورتر متصل نکنید.</p>"
    )
    return "\n".join([*rendered, safety])


for _article in SOLARX_ERROR_ARTICLES:
    _source = _source_articles[_article["slug"]]
    _article["title_fa"] = _source["title_fa"]
    _article["body_fa"] = _format_persian_body(_source["body_fa"])
