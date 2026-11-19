"""General, bilingual brand-comparison articles based on supplied Word files."""

import json
from pathlib import Path


GENERAL_COMPARISON_ARTICLES = [
    {
        "slug": "huawei-vs-sungrow-solar-inverter-comparison",
        "article_type": "general",
        "published_days_ago": 0,
        "title_en": "Huawei vs Sungrow Solar Inverters: A Project-Based Comparison",
        "excerpt_fa": "مقایسهٔ Huawei و Sungrow بر اساس مدل، ذخیره‌سازی، پایش و نیاز پروژه؛ نه انتخاب یک برندهٔ همیشگی.",
        "excerpt_en": "Compare Huawei and Sungrow by model, storage, monitoring and project needs—not by declaring one universal winner.",
        "body_en": """
<p>Huawei and Sungrow should not be ranked as universally better or worse. The right choice depends on the exact inverter, grid rules, PV array, storage design, backup requirements and the local service team. This comparison focuses on the product families identified in the supplied document; verify all specifications against current datasheets for the project.</p>
<h2>Scope and grid-connected operation</h2>
<p>For a grid-connected system, compare the model's MPPT range and count, maximum DC voltage and current, AC ratings, protection functions and supported grid code. Brand name alone does not establish better MPPT performance or grid stability. String design, site temperature and the local supply must be considered with the selected inverter.</p>
<h2>Monitoring and diagnostics</h2>
<p>The cited Huawei material describes Smart I-V Curve Diagnosis for supported models, including PV-string analysis and reporting. The Sungrow SH-series manual documents monitoring and commissioning through iSolarCloud. These capabilities depend on model and firmware; confirm they are available on the exact unit rather than assuming they apply to every product.</p>
<h2>Battery storage and backup</h2>
<p>The cited Huawei LUNA2000-S1 information describes modular storage and module-level management. The Sungrow SH manual covers battery communication, charge/discharge management and backup-load wiring. Before selection, verify battery compatibility, BMS protocol, voltage range, backup topology, firmware and required accessories.</p>
<h2>Repair and selection checklist</h2>
<p>For serviceability, record the exact model, firmware, fault log, PV-string layout, battery type and grid conditions. Compare genuine local parts, warranty, commissioning support and technician experience alongside purchase cost. PV and battery circuits can remain hazardous after shutdown; measurements and repairs belong to qualified personnel.</p>
<h2>Official references</h2>
<ul>
<li><a href="https://solar.huawei.com/en-GB/download?p=%252F-%252Fmedia%252FSolar%252Fattachment%252Fpdf%252Feu%252Fdatasheet%252FIV-Curve.pdf">Huawei Smart I-V Curve Diagnosis</a></li>
<li><a href="https://aus.sungrowpower.com/upload/file/20210816/SH3.0_3.6_4.0_5.0_6.0RS-UEN-Ver11-20210629.pdf">Sungrow SH-series user manual</a></li>
<li><a href="https://solar.huawei.com/en/products/luna2000-7-14-21-s1/">Huawei LUNA2000-S1 product information</a></li>
</ul>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Huawei Sungrow solar inverter comparison PV battery monitoring",
        "services": ["solar-inverter-repair"],
        "brands": ["huawei", "sungrow"],
        "seo_title_fa": "مقایسهٔ اینورترهای خورشیدی Huawei و Sungrow | الکتروگلد",
        "seo_title_en": "Huawei vs Sungrow Solar Inverters | ElectroGold",
        "seo_description_fa": "مقایسهٔ مدل‌محور Huawei و Sungrow در پایش، ذخیره‌سازی، برق پشتیبان و ملاحظات تعمیراتی.",
        "seo_description_en": "A model-based comparison of Huawei and Sungrow monitoring, storage, backup and service considerations.",
    },
    {
        "slug": "siemens-sinamics-vs-abb-acs-comparison",
        "article_type": "general",
        "published_days_ago": 1,
        "title_en": "Siemens SINAMICS vs ABB ACS: Choosing an Industrial Drive",
        "excerpt_fa": "مقایسهٔ SINAMICS و ACS بر پایهٔ مدل هم‌رده، کنترل حرکت، PLC، شبکه و امکانات تعمیر؛ نه برتری مطلق برند.",
        "excerpt_en": "Compare SINAMICS and ACS using equivalent models, motion control, PLCs, networks and service needs—not brand claims.",
        "body_en": """
<p>There is no universal winner between Siemens SINAMICS and ABB ACS. Selection depends on the motor and load, motion-control needs, existing automation architecture, networks, environment and local service capability. The supplied documents discuss G120/G120C and S120 from Siemens, and ACS580/ACS880 from ABB. These are different families and must be compared by matching ratings and applications.</p>
<h2>Control and automation integration</h2>
<p>SINAMICS may provide a straightforward engineering path in a SIMATIC-based project; the supplied references describe S120/S7-1500 integration through a Technology Object and Startdrive/TIA Portal workflows for supported equipment. ABB describes Direct Torque Control (DTC) for applicable ACS products. Neither feature proves universal superiority: confirm compatibility, motor, controller, firmware and required performance for the selected model.</p>
<h2>Networks and commissioning</h2>
<p>Available protocols depend on the model and installed communication option. ABB drives can integrate with Siemens PLCs using supported modules and documented configuration; Siemens families also offer model-specific network options. Confirm device files, telegram or word mapping, addressing, firmware and PLC logic before commissioning.</p>
<h2>Repair and lifecycle considerations</h2>
<p>Record the full drive and motor nameplates, installed cards, firmware, fault log and parameter backup. Diagnosis should distinguish installation or motor faults from internal power or control-board issues. Parts availability, manuals, qualified repair support and downtime can matter more than purchase price alone. Test a repaired drive progressively under a suitable load.</p>
<h2>Choosing between model families</h2>
<p>For coordinated motion in a Siemens-based installation, evaluate a suitable SINAMICS model and controller integration. For a general-purpose comparison, G120/G120C and ACS580 may be relevant starting points, while S120 and ACS880 address different performance needs. Compare exact voltage, current, overload rating, options and application—not just the family name.</p>
<h2>Official references</h2>
<ul>
<li><a href="https://assets.new.siemens.com/siemens/assets/api/uuid:42691564-b532-42e2-9af5-2c8199145d0b/sinamics-g120-brochure.pdf">Siemens SINAMICS G120 brochure</a></li>
<li><a href="https://support.industry.siemens.com/cs/attachments/109482718/109482718_FAQ_S7-1500_TO-S120_en.pdf">Siemens S120 and SIMATIC S7-1500 application guide</a></li>
<li><a href="https://www.abb.com/global/en/areas/motion/drives/expertise-technology/direct-torque-control">ABB Direct Torque Control overview</a></li>
<li><a href="https://library.e.abb.com/public/8e4a4a75677e4b04a828059e684a672a/ABB_Drives_function_blocks_for_Siemens_PLCs_Quick_start-up_guide_A_A4.pdf">ABB drives with Siemens PLCs quick-start guide</a></li>
<li><a href="https://library.e.abb.com/public/2ea96e5d24c1419794e6f126d537c301/ACS880-PHTC04U-EN_Rev_A.pdf">ABB ACS880 technical brochure</a></li>
</ul>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Siemens SINAMICS ABB ACS industrial drive comparison PLC",
        "services": ["industrial-inverter-repair"],
        "brands": ["siemens", "abb"],
        "seo_title_fa": "مقایسهٔ درایوهای Siemens SINAMICS و ABB ACS | الکتروگلد",
        "seo_title_en": "Siemens SINAMICS vs ABB ACS Industrial Drives | ElectroGold",
        "seo_description_fa": "مقایسهٔ درایوهای زیمنس و ABB بر اساس مدل، کنترل حرکت، شبکهٔ صنعتی و سرویس‌پذیری.",
        "seo_description_en": "Compare Siemens and ABB drives by model, motion control, industrial networks and serviceability.",
    },
    {
        "slug": "delta-vs-invt-industrial-drive-comparison",
        "article_type": "general",
        "published_days_ago": 2,
        "title_en": "Delta vs INVT Drives: Technical and Lifecycle Comparison",
        "excerpt_fa": "راهنمای مقایسهٔ Delta و INVT بر اساس مدل، بار، کنترل، خدمات و هزینهٔ کل مالکیت.",
        "excerpt_en": "Compare Delta and INVT by model, load, control features, service access and total cost of ownership.",
        "body_en": """
<p>Delta and INVT both offer variable-frequency drives for general and industrial applications, but there is no single brand-level winner. Compare exact models with similar voltage, current, overload rating and duty—not entire product portfolios as if they were equivalent. The supplied document is a selection framework; final values and functions must be confirmed in the relevant datasheets.</p>
<h2>Technical fit</h2>
<p>Depending on the series, both manufacturers offer scalar V/f and vector-control options. Low-speed torque, dynamic response, overload duration, programmable I/O and communication interfaces vary by model or optional card. For fans and pumps, evaluate the load profile and control method; for conveyors, mixers and high-inertia loads, pay particular attention to starting torque, acceleration/deceleration ramps and braking needs.</p>
<h2>Installation, maintenance and repair</h2>
<p>Cabinet ventilation, temperature, dust, altitude, grounding and supply quality affect both brands. Before purchase, check local parts availability, warranty, manuals, parameter backup and qualified service support. For a fault, start with the exact code, operating conditions, motor and cable, then check settings and the drive hardware as indicated. Isolate power and follow the manufacturer's discharge and safety procedure before service.</p>
<h2>Total cost and decision</h2>
<p>Purchase price alone is not total cost of ownership. Include accessories such as filters or braking components, installation and commissioning, energy use, expected downtime, spare parts and service. Estimate energy savings from the real load curve and operating hours rather than applying a generic percentage. The preferred drive is the model that meets the process requirements and can be supported at the installation site.</p>
""",
        "author": "تیم فنی الکتروگلد",
        "image_query": "Delta INVT industrial variable frequency drive comparison",
        "services": ["industrial-inverter-repair"],
        "brands": ["delta", "inovance"],
        "seo_title_fa": "مقایسهٔ اینورترهای Delta و INVT | الکتروگلد",
        "seo_title_en": "Delta vs INVT Industrial Drives | ElectroGold",
        "seo_description_fa": "مقایسهٔ مدل‌محور دلتا و اینوت از نظر بار، کنترل، نگهداری، قطعات و هزینهٔ کل مالکیت.",
        "seo_description_en": "A model-based Delta and INVT comparison covering load, control, maintenance, parts and lifecycle cost.",
    },
]


_comparison_sources = json.loads(
    Path(__file__).with_name("comparison_articles_source.json").read_text(encoding="utf-8")
)
for _article in GENERAL_COMPARISON_ARTICLES:
    _source = _comparison_sources[_article["slug"]]
    _article["title_fa"] = _source["title_fa"]
    _article["body_fa"] = _source["body_fa"]
    if _article["slug"] == "siemens-sinamics-vs-abb-acs-comparison":
        _article["body_fa"] += """
<h2>مقایسهٔ خانواده‌های عمومی‌تر</h2>
<p>در فایل همراه، G120/G120C زیمنس و ACS580 اشنایدر نیز برای کاربردهای عمومی مطرح شده‌اند. این خانواده‌ها را باید با مدل هم‌رده، توان، جریان و قابلیت کنترل مقایسه کرد؛ G120 یا ACS580 را نمی‌توان صرفاً از روی نام با هر مدل S120 یا ACS880 هم‌ارز دانست. یکپارچگی با TIA Portal و SIMATIC، امکانات DTC، کارت‌های شبکه و نسخهٔ نرم‌افزار باید در پروژهٔ واقعی بررسی شوند.</p>
<h2>منابع رسمی تکمیلی</h2>
<ul>
<li><a href="https://assets.new.siemens.com/siemens/assets/api/uuid:42691564-b532-42e2-9af5-2c8199145d0b/sinamics-g120-brochure.pdf">بروشور SINAMICS G120 زیمنس</a></li>
<li><a href="https://support.industry.siemens.com/cs/attachments/109482718/109482718_FAQ_S7-1500_TO-S120_en.pdf">راهنمای کار SINAMICS S120 با SIMATIC S7-1500</a></li>
<li><a href="https://www.abb.com/global/en/areas/motion/drives/expertise-technology/direct-torque-control">شرح فناوری DTC شرکت ABB</a></li>
<li><a href="https://library.e.abb.com/public/8e4a4a75677e4b04a828059e684a672a/ABB_Drives_function_blocks_for_Siemens_PLCs_Quick_start-up_guide_A_A4.pdf">راهنمای اتصال درایوهای ABB به PLCهای زیمنس</a></li>
<li><a href="https://library.e.abb.com/public/2ea96e5d24c1419794e6f126d537c301/ACS880-PHTC04U-EN_Rev_A.pdf">مرجع فنی ACS880 شرکت ABB</a></li>
</ul>
"""
