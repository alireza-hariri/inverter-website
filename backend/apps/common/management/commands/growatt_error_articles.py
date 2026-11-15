"""Bilingual Growatt fault articles based on the supplied DOCX files.

Persian titles and body text are loaded verbatim from the source documents.
"""

import json
from pathlib import Path


GROWATT_ERROR_ARTICLES = [
    {
        "slug": "growatt-solar-ce",
        "title_en": "Growatt Inverter CE Fault: Communication Error Checks",
        "excerpt_fa": "راهنمای عیب‌یابی خطای CE در سانورتر گراوات و بررسی ارتباط، سیم‌کشی و تنظیمات دستگاه.",
        "excerpt_en": "A guide to Growatt CE faults and checks for inverter communications, wiring, and configuration.",
        "body_en": """
<p>The supplied article covers the Growatt <strong>CE</strong> fault. The exact meaning can depend on inverter model and system configuration, so use the model manual as the reference during diagnosis.</p>
<h2>What to check</h2>
<ul>
<li>Inspect communication cables and connectors for loose or damaged connections.</li>
<li>Check the connected monitoring device and configuration settings.</li>
<li>Look for electrical noise or interruptions that may affect communications.</li>
</ul>
<p>A qualified technician can test the communication path and inverter interface. Call our experts at ElectroGold for Growatt inverter diagnostics.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Growatt solar inverter CE communication fault diagnostics",
        "services": ["solar-inverter-repair"], "brands": ["growatt"],
        "seo_title_fa": "رفع خطای CE سانورتر گراوات | الکتروگلد",
        "seo_title_en": "Growatt Inverter CE Fault Diagnosis | ElectroGold",
        "seo_description_fa": "برای رفع خطای CE گراوات، ارتباط، اتصالات، تجهیزات مانیتورینگ و تنظیمات مدل دستگاه را بررسی کنید.",
        "seo_description_en": "Troubleshoot Growatt CE by checking communication wiring, monitoring equipment, and model settings.",
    },
    {
        "slug": "growatt-solar-ef",
        "title_en": "Growatt Inverter EF Fault: External Fault and Safety Inputs",
        "excerpt_fa": "علت خطای EF در سانورتر گراوات را در ورودی‌های خارجی، تجهیزات حفاظتی و سیم‌کشی بررسی کنید.",
        "excerpt_en": "Check external fault inputs, safety equipment, and wiring when a Growatt inverter reports EF.",
        "body_en": """
<p>The <strong>EF</strong> fault in the supplied Growatt article indicates an external fault condition or input. The trip may be requested by connected controls or safety equipment rather than an internal inverter failure.</p>
<h2>Possible checks</h2>
<ul>
<li>Review external stop and safety-circuit status.</li>
<li>Check digital inputs, control wiring, sensors, and connected equipment.</li>
<li>Confirm the input configuration against the manual for the inverter model.</li>
</ul>
<p>Do not bypass safety inputs to clear an EF warning. Have the external signal traced by a qualified technician; call ElectroGold for Growatt support.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Growatt inverter EF external fault diagnosis",
        "services": ["solar-inverter-repair"], "brands": ["growatt"],
        "seo_title_fa": "رفع خطای EF در سانورتر گراوات | الکتروگلد",
        "seo_title_en": "Growatt EF External Fault Diagnosis | ElectroGold",
        "seo_description_fa": "خطای EF گراوات را با بررسی ورودی خارجی، مدار ایمنی، سنسورها و سیم‌کشی فرمان عیب‌یابی کنید.",
        "seo_description_en": "Diagnose Growatt EF by checking external inputs, safety circuits, sensors, and control wiring.",
    },
    {
        "slug": "growatt-solar-errfault",
        "title_en": "Growatt Inverter ErrFault: Identifying the Displayed Fault",
        "excerpt_fa": "برای عیب‌یابی پیام ErrFault گراوات، کد کامل، مدل سانورتر و شرایط وقوع خطا را ثبت کنید.",
        "excerpt_en": "For a Growatt ErrFault message, record the full code, inverter model, and conditions when it occurs.",
        "body_en": """
<p><strong>ErrFault</strong> is a general fault indication in the supplied Growatt document. The full displayed code and inverter model are needed to identify the specific protection that has tripped.</p>
<h2>Information to collect</h2>
<ul>
<li>Record the complete fault text and model number.</li>
<li>Note whether the fault occurs at startup, under load, or during a grid event.</li>
<li>Check the manufacturer's troubleshooting guidance before attempting a reset.</li>
</ul>
<p>If the same fault returns, the supply, connected equipment, and inverter should be professionally inspected. Call our experts at ElectroGold for Growatt diagnostics.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Growatt solar inverter error fault troubleshooting",
        "services": ["solar-inverter-repair"], "brands": ["growatt"],
        "seo_title_fa": "عیب‌یابی پیام ErrFault سانورتر گراوات | الکتروگلد",
        "seo_title_en": "Growatt ErrFault Troubleshooting | ElectroGold",
        "seo_description_fa": "برای تشخیص ErrFault گراوات، مدل دستگاه، کد کامل و شرایط بروز خطا را بررسی کنید.",
        "seo_description_en": "Identify a Growatt ErrFault by checking the inverter model, full code, and operating conditions.",
    },
    {
        "slug": "growatt-solar-oc",
        "title_en": "Growatt Inverter OC Fault: Overcurrent Causes and Checks",
        "excerpt_fa": "خطای OC سانورتر گراوات را با بررسی بار، کابل، اتصالات و بخش قدرت عیب‌یابی کنید.",
        "excerpt_en": "Troubleshoot a Growatt OC fault by checking the load, wiring, connections, and inverter power stage.",
        "body_en": """
<p><strong>OC (Overcurrent)</strong> indicates that the inverter detected current outside its permitted operating range. The cause can be external equipment or an internal power-stage issue.</p>
<h2>Possible causes</h2>
<ul>
<li>An abnormal load or short circuit in connected wiring.</li>
<li>Loose, damaged, or incorrectly connected cables.</li>
<li>A fault in current sensing or the inverter's power components.</li>
</ul>
<p>Isolate the system safely and follow the Growatt model manual. Do not repeatedly reset the inverter without finding the cause. Call ElectroGold for specialist diagnosis.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Growatt inverter OC overcurrent fault repair",
        "services": ["solar-inverter-repair"], "brands": ["growatt"],
        "seo_title_fa": "رفع خطای OC سانورتر گراوات؛ اضافه‌جریان | الکتروگلد",
        "seo_title_en": "Growatt Inverter OC Overcurrent Diagnosis | ElectroGold",
        "seo_description_fa": "علت خطای OC گراوات را در بار، کابل‌کشی، اتصالات و مدار قدرت بررسی کنید.",
        "seo_description_en": "Check the load, cabling, connections, and power stage when diagnosing Growatt OC.",
    },
    {
        "slug": "growatt-solar-of",
        "title_en": "Growatt Inverter OF Fault: Frequency and Grid Checks",
        "excerpt_fa": "برای عیب‌یابی خطای OF گراوات، فرکانس و پایداری شبکه و تنظیمات اتصال به برق را بررسی کنید.",
        "excerpt_en": "Check grid frequency, supply stability, and connection settings when troubleshooting Growatt OF.",
        "body_en": """
<p>The <strong>OF</strong> fault in the supplied article is associated with an out-of-range frequency condition. Verify the exact definition and limits for the specific Growatt inverter model and grid standard.</p>
<h2>What to check</h2>
<ul>
<li>Measure grid frequency and confirm it is within the required range.</li>
<li>Review supply stability and upstream electrical connections.</li>
<li>Check the inverter's grid and country-code settings against the installation requirements.</li>
</ul>
<p>Do not alter protection thresholds to suppress the fault. If the grid is stable but OF continues, have the inverter and its sensing circuits checked by a qualified technician.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Growatt solar inverter OF frequency grid fault",
        "services": ["solar-inverter-repair"], "brands": ["growatt"],
        "seo_title_fa": "عیب‌یابی خطای OF سانورتر گراوات | الکتروگلد",
        "seo_title_en": "Growatt OF Frequency Fault Diagnosis | ElectroGold",
        "seo_description_fa": "خطای OF گراوات را با بررسی فرکانس شبکه، پایداری برق و تنظیمات اتصال به شبکه پیگیری کنید.",
        "seo_description_en": "Troubleshoot Growatt OF by checking grid frequency, supply stability, and grid-connection settings.",
    },
    {
        "slug": "growatt-solar-oh",
        "title_en": "Growatt Inverter OH Fault: Overtemperature and Cooling",
        "excerpt_fa": "فن، تهویه، دمای محیط و شرایط کاری را برای عیب‌یابی خطای OH سانورتر گراوات بررسی کنید.",
        "excerpt_en": "Check the fan, ventilation, ambient temperature, and operating conditions for a Growatt OH fault.",
        "body_en": """
<p><strong>OH</strong> indicates an overtemperature condition on the Growatt inverter models covered by the source document. The exact sensor and threshold depend on the model.</p>
<h2>Possible causes</h2>
<ul>
<li>Blocked air inlets or insufficient ventilation around the inverter.</li>
<li>A cooling fan that is stopped, slow, or damaged.</li>
<li>High ambient temperature, direct sun, or sustained heavy operating conditions.</li>
<li>A temperature-sensor or internal cooling-circuit fault.</li>
</ul>
<p>Keep the cooling path clear and avoid opening energized equipment. If OH returns after installation and airflow checks, contact ElectroGold for Growatt service.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Growatt inverter OH overheating ventilation fan service",
        "services": ["solar-inverter-repair"], "brands": ["growatt"],
        "seo_title_fa": "رفع خطای OH سانورتر گراوات؛ دمای بالا | الکتروگلد",
        "seo_title_en": "Growatt OH Overtemperature Diagnosis | ElectroGold",
        "seo_description_fa": "علت خطای OH گراوات را با بررسی فن، تهویه، دمای محیط و سنسور حرارتی پیدا کنید.",
        "seo_description_en": "Diagnose Growatt OH by checking the fan, ventilation, ambient temperature, and thermal sensor.",
    },
    {
        "slug": "growatt-solar-ol",
        "title_en": "Growatt Inverter OL Fault: Overload Diagnosis",
        "excerpt_fa": "خطای OL گراوات را در بار متصل، جریان، کابل‌ها و تنظیمات دستگاه بررسی کنید.",
        "excerpt_en": "Check the connected load, current, wiring, and inverter settings when a Growatt unit reports OL.",
        "body_en": """
<p><strong>OL (Overload)</strong> indicates that load or current has exceeded the operating limit defined for the inverter. Confirm the exact trip behavior in the manual for the model.</p>
<h2>Checks to make</h2>
<ul>
<li>Compare the connected load with the inverter's rated capacity.</li>
<li>Check for abnormal current draw, wiring faults, or a short circuit.</li>
<li>Review operating parameters and recent changes to the system.</li>
</ul>
<p>Do not raise protection limits without an engineering assessment. If the system is correctly sized and OL continues, have the inverter inspected and tested.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Growatt solar inverter OL overload troubleshooting",
        "services": ["solar-inverter-repair"], "brands": ["growatt"],
        "seo_title_fa": "رفع خطای OL سانورتر گراوات؛ اضافه‌بار | الکتروگلد",
        "seo_title_en": "Growatt OL Overload Fault Diagnosis | ElectroGold",
        "seo_description_fa": "برای رفع OL گراوات، ظرفیت بار، جریان، سیم‌کشی و پارامترهای اینورتر را بررسی کنید.",
        "seo_description_en": "Troubleshoot Growatt OL by checking load capacity, current, wiring, and inverter settings.",
    },
    {
        "slug": "growatt-solar-ov",
        "title_en": "Growatt Inverter OV Fault: Overvoltage Checks",
        "excerpt_fa": "علت خطای OV گراوات را در ولتاژ ورودی، رشته‌های پنل و شرایط شبکه بررسی کنید.",
        "excerpt_en": "Check input voltage, PV strings, and grid conditions when troubleshooting a Growatt OV fault.",
        "body_en": """
<p><strong>OV (Overvoltage)</strong> means that a monitored voltage has exceeded its permitted limit. The relevant input and threshold vary by Growatt inverter model and whether the fault is on the PV or grid side.</p>
<h2>Possible areas to check</h2>
<ul>
<li>PV string voltage and configuration against the inverter's rated range.</li>
<li>Grid voltage and stability at the connection point.</li>
<li>Wiring, polarity, and the inverter's voltage-sensing circuit.</li>
</ul>
<p>Use the model manual and qualified solar technicians for measurements. Do not disconnect PV wiring under load. If OV persists with valid external voltages, ElectroGold can inspect the inverter.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Growatt inverter OV overvoltage PV string diagnostics",
        "services": ["solar-inverter-repair"], "brands": ["growatt"],
        "seo_title_fa": "عیب‌یابی خطای OV سانورتر گراوات | الکتروگلد",
        "seo_title_en": "Growatt OV Overvoltage Diagnosis | ElectroGold",
        "seo_description_fa": "خطای OV گراوات را با بررسی ولتاژ پنل‌ها، رشته‌های PV، برق شبکه و مدار سنجش عیب‌یابی کنید.",
        "seo_description_en": "Diagnose Growatt OV by checking PV voltage, string configuration, grid supply, and voltage sensing.",
    },
    {
        "slug": "growatt-solar-ug",
        "title_en": "Growatt Inverter UG Fault: Under-Voltage Diagnosis",
        "excerpt_fa": "افت ولتاژ پنل یا شبکه، اتصالات و محدودیت‌های ورودی را برای عیب‌یابی خطای UG گراوات بررسی کنید.",
        "excerpt_en": "Check PV or grid voltage, connections, and input limits when troubleshooting a Growatt UG fault.",
        "body_en": """
<p>The supplied article identifies <strong>UG</strong> as an under-voltage fault. Confirm which input is being monitored on the specific Growatt model before troubleshooting.</p>
<h2>Possible causes</h2>
<ul>
<li>PV voltage below the startup or operating range.</li>
<li>Grid-voltage drop or unstable supply, where applicable to the model.</li>
<li>Loose connections, damaged wiring, or an open circuit.</li>
</ul>
<p>Check the system configuration and input measurements safely. If the source voltage is within range but UG remains, the sensing or internal power circuit may need service.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Growatt solar inverter UG under voltage fault diagnosis",
        "services": ["solar-inverter-repair"], "brands": ["growatt"],
        "seo_title_fa": "رفع خطای UG سانورتر گراوات؛ افت ولتاژ | الکتروگلد",
        "seo_title_en": "Growatt UG Under-Voltage Fault Diagnosis | ElectroGold",
        "seo_description_fa": "علت خطای UG گراوات را در ولتاژ ورودی، رشته‌های پنل، شبکه و اتصالات بررسی کنید.",
        "seo_description_en": "Troubleshoot Growatt UG by checking input voltage, PV strings, grid supply, and connections.",
    },
    {
        "slug": "growatt-solar-uv",
        "title_en": "Growatt Inverter UV Fault: DC-Link Under-Voltage Checks",
        "excerpt_fa": "خطای UV گراوات را با بررسی ولتاژ ورودی، اتصالات، مدار پیش‌شارژ و خازن‌های DC عیب‌یابی کنید.",
        "excerpt_en": "Check input voltage, connections, pre-charge, and DC capacitors when troubleshooting Growatt UV.",
        "body_en": """
<p><strong>UV (Under-voltage)</strong> indicates that an internal or monitored DC voltage has fallen below its permitted threshold. The exact circuit and code behavior are model-specific.</p>
<h2>What may cause UV?</h2>
<ul>
<li>Low or unstable input voltage.</li>
<li>Loose terminals or voltage drop under load.</li>
<li>A pre-charge, rectifier, or DC-link capacitor fault.</li>
</ul>
<p>Do not disable under-voltage protection or repeatedly restart the unit. Internal DC circuits may retain hazardous voltage after shutdown. If input measurements are normal, have the inverter inspected by a qualified repairer. Call our experts at ElectroGold.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Growatt inverter UV DC link undervoltage repair",
        "services": ["solar-inverter-repair"], "brands": ["growatt"],
        "seo_title_fa": "رفع خطای UV سانورتر گراوات؛ افت ولتاژ DC | الکتروگلد",
        "seo_title_en": "Growatt UV DC Under-Voltage Diagnosis | ElectroGold",
        "seo_description_fa": "برای عیب‌یابی UV گراوات، ولتاژ ورودی، اتصالات، مدار پیش‌شارژ و خازن‌های باس DC را بررسی کنید.",
        "seo_description_en": "Troubleshoot Growatt UV by checking input voltage, connections, pre-charge, and DC-link capacitors.",
    },
]

_source_articles = json.loads(
    Path(__file__).with_name("growatt_error_articles_source.json").read_text(encoding="utf-8")
)
for _article in GROWATT_ERROR_ARTICLES:
    _article.update(_source_articles[_article["slug"]])
