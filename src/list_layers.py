# src/list_layers.py
"""
أداة لاستكشاف الطبقات والبلوكات في ملف CAD
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import ezdxf
from collections import Counter

def list_layers_and_blocks(file_path):
    """عرض جميع الطبقات والبلوكات في الملف"""
    try:
        doc = ezdxf.readfile(file_path)
        
        print("\n" + "="*70)
        print("📋 الطبقات (Layers) في الملف:")
        print("="*70)
        
        # جمع الطبقات
        layer_entities = Counter()
        for entity in doc.modelspace():
            layer_entities[entity.dxf.layer] += 1
        
        # عرض الطبقات
        for i, (layer, count) in enumerate(layer_entities.most_common(), 1):
            print(f"{i:3}. {layer:50} - {count:5} عنصر")
        
        print("\n" + "="*70)
        print("🔷 البلوكات (Blocks) في الملف:")
        print("="*70)
        
        # جمع البلوكات
        block_entities = Counter()
        for entity in doc.modelspace():
            if entity.dxftype() == 'INSERT':
                block_entities[entity.dxf.name] += 1
        
        # عرض البلوكات
        for i, (block, count) in enumerate(block_entities.most_common(), 1):
            print(f"{i:3}. {block:50} - {count:5} مرة")
        
        print("\n" + "="*70)
        print("📐 أنواع العناصر (Entity Types):")
        print("="*70)
        
        # جمع أنواع العناصر
        type_entities = Counter()
        for entity in doc.modelspace():
            type_entities[entity.dxftype()] += 1
        
        # عرض الأنواع
        for entity_type, count in type_entities.most_common():
            print(f"   {entity_type:30} - {count:5} عنصر")
        
        return True
        
    except Exception as e:
        print(f"خطأ: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("الاستخدام: python list_layers.py <path_to_dxf_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    list_layers_and_blocks(file_path)