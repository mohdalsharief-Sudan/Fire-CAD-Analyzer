# summary.py
import sys
import json

sys.path.insert(0, '.')

# قراءة التقرير المحفوظ
with open('reports/analysis_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

print("=" * 60)
print("📊 تقرير تحليل نظام مكافحة الحريق")
print("=" * 60)

# ملخص العناصر
entities = report.get('entities_summary', {})
print("\n🔹 العناصر المستخرجة:")
print(f"   • الرشاشات: {entities.get('sprinklers', {}).get('count', 0)}")
print(f"   • المواسير: {entities.get('pipes', {}).get('count', 0)}")
print(f"   • إجمالي طول المواسير: {entities.get('pipes', {}).get('total_length', 0):.2f} متر")
print(f"   • المضخات: {entities.get('pumps', {}).get('count', 0)}")
print(f"   • الخزانات: {entities.get('tanks', {}).get('count', 0)}")

# المخالفات
validation = report.get('validation', {})
nfpa = validation.get('nfpa', {})
saudi = validation.get('saudi', {})

print(f"\n⚠️ المخالفات:")
print(f"   • NFPA: {len(nfpa.get('violations', []))} مخالفة")
print(f"   • الكود السعودي: {len(saudi.get('violations', []))} مخالفة")

# أنواع المخالفات
violations = nfpa.get('violations', [])
violation_types = {}
for v in violations:
    vtype = v.get('type', 'unknown')
    violation_types[vtype] = violation_types.get(vtype, 0) + 1

print(f"\n📋 أنواع مخالفات NFPA:")
for vtype, count in sorted(violation_types.items(), key=lambda x: x[1], reverse=True):
    print(f"   • {vtype}: {count}")