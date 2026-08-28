import sys
sys.path.insert(0, '.')

from entity_extractor import EntityExtractor

methods = [m for m in dir(EntityExtractor) if m.startswith('_extract')]
print('الدوال الموجودة:')
for m in methods:
    print(f'  - {m}')

print(f'\nإجمالي الدوال: {len(methods)}')

# تحقق من الدوال المهمة
required_methods = [
    '_extract_block_entity',
    '_extract_line_entity', 
    '_extract_polyline_entity',
    '_extract_circle_entity',
    '_extract_text_entity',
    '_extract_mtext_entity',
    '_extract_block_attributes'
]

print('\nالتحقق من الدوال المطلوبة:')
for method in required_methods:
    if method in methods:
        print(f'  ✅ {method}')
    else:
        print(f'  ❌ {method} - مفقودة!')