import sys
import time
import ezdxf

sys.path.insert(0, '.')

from entity_extractor import EntityExtractor
from nfpa_validator import NFPAValidator

print("قراءة الملف...")
doc = ezdxf.readfile(r'D:\Testing.dxf')

print("استخراج العناصر...")
ext = EntityExtractor(doc.modelspace(), doc)
entities = ext.extract_all()

print("بدء فحص NFPA...")
start = time.time()

validator = NFPAValidator(entities)
results = validator.validate_all()

end = time.time()

print(f"اكتمل الفحص في {end-start:.2f} ثانية")
print(f"عدد المخالفات: {len(results['violations'])}")
print(f"عدد التحذيرات: {len(results['warnings'])}")

# عرض أول 10 مخالفات
if results['violations']:
    print("\nأول 10 مخالفات:")
    for i, violation in enumerate(results['violations'][:10], 1):
        print(f"  {i}. {violation.get('type', 'unknown')}: {violation.get('message', '')[:100]}")