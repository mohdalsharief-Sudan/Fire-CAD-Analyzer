\# Fire CAD Analyzer 🔥



أداة احترافية لتحليل ملفات CAD لأنظمة مكافحة الحريق، مع حساب التكاليف والتحقق من المعايير.



\## ✨ المميزات



\- 📁 قراءة ملفات \*\*DXF\*\* مباشرة و \*\*DWG\*\* (عبر ODA File Converter)

\- 🔍 استخراج تلقائي للعناصر:

&#x20; - الرشاشات (Sprinklers)

&#x20; - المواسير (Pipes)

&#x20; - المضخات (Pumps)

&#x20; - الصمامات (Valves)

&#x20; - أنظمة الغاز (FM-200, Novec, CO2)

&#x20; - خزانات الخراطيم (Hose Cabinets)

&#x20; - أنظمة الإنذار (Fire Alarm)

\- 📐 كشف تلقائي لوحدة القياس (متر، مليمتر، بوصة)

\- 🏷️ تصنيف المخاطر (Hazard Classification):

&#x20; - Light Hazard

&#x20; - Ordinary Hazard G1/G2

&#x20; - Extra Hazard G1/G2

\- ✅ التحقق من المعايير:

&#x20; - NFPA 13 (مساحة التغطية، التباعد)

&#x20; - الكود السعودي (SBC 801)

\- 💰 حساب التكاليف التفصيلي

\- 📊 تصدير التقارير:

&#x20; - Excel (جدول تكاليف قابل للتعديل)

&#x20; - PDF (تقرير احترافي بالعربية)

&#x20; - JSON (بيانات كاملة)



\## 📋 المتطلبات



\### Python 3.8+



\### المكتبات:

```bash

pip install -r requirements.txt


\🏗️ هيكل المشروع

Fire-CAD-Analyzer/
├── src/
│   ├── main.py                 ← البرنامج الرئيسي
│   ├── cad_reader.py           ← قراءة DXF/DWG
│   ├── entity_extractor.py     ← استخراج العناصر
│   ├── hazard_classifier.py    ← تصنيف المخاطر
│   ├── nfpa_validator.py       ← فحص NFPA
│   ├── saudi_validator.py      ← فحص الكود السعودي
│   ├── cost_calculator.py      ← حاسبة التكاليف
│   ├── cost_data.py            ← بيانات الأسعار
│   ├── excel_exporter.py       ← تصدير Excel
│   ├── report_generator.py     ← تقارير PDF/JSON
│   └── utils/
│       └── constants.py        ← الثوابت والمعايير
├── tests/
│   └── test_cad_analyzer.py    ← الاختبارات
├── requirements.txt
└── README.md
