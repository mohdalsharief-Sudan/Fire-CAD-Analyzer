# src/pricing_exporter.py
"""
تصدير النتائج إلى صيغة متوافقة مع Fire-Pricing
"""

import json
import os
from datetime import datetime
from typing import Dict, Any


class PricingExporter:
    """مصدر النتائج إلى Fire-Pricing"""
    
    def __init__(self):
        pass
    
    def export_for_fire_pricing(self, 
                                 cost_summary: Dict[str, Any],
                                 entities: Dict[str, Any],
                                 project_name: str = "",
                                 output_dir: str = "pricing_export") -> str:
        """
        تصدير بصيغة متوافقة مع Fire-Pricing
        
        Returns:
            str: مسار الملف المُصدَّر
        """
        # تحويل البنود لصيغة Fire-Pricing
        materials = []
        equipment = []
        labor = []
        services = []
        
        for item in cost_summary.get('items', []):
            item_name = item.get('item', '')
            quantity = item.get('quantity', 0)
            unit = item.get('unit', '')
            unit_price = item.get('unit_price', 0)
            subtotal = item.get('subtotal', 0)
            
            # تصنيف البنود
            if 'مضخة' in item_name:
                # المضخات = أجهزة
                equipment.append({
                    'name': item_name,
                    'qty': quantity,
                    'supplyCost': round(unit_price, 2),
                    'installCost': 0,
                })
            elif 'تركيب' in item_name or 'تركيب' in item_name:
                # تكلفة التركيب = عمالة
                labor.append({
                    'name': item_name,
                    'workers': 1,
                    'days': 1,
                    'dailyCost': round(subtotal, 2),
                })
            elif 'تصميم' in item_name or 'هندسة' in item_name or 'إدارية' in item_name or 'ربح' in item_name or 'احتياطي' in item_name:
                # النسب = خدمات
                services.append({
                    'name': item_name,
                    'value': round(subtotal, 2),
                    'type': 'fixed',
                    'amount': round(subtotal, 2),
                })
            else:
                # الباقي = مواد
                materials.append({
                    'name': item_name,
                    'qty': quantity,
                    'unit': unit,
                    'unitCost': round(unit_price, 2),
                })
        
        # بناء بيانات Fire-Pricing
        fire_pricing_data = {
            'name': project_name.replace('.dxf', '').replace('.dwg', ''),
            'quoteNo': f"CAD-{datetime.now().strftime('%Y%m%d')}",
            'date': datetime.now().strftime("%Y-%m-%d"),
            'source': 'Fire-CAD-Analyzer',
            'materials': materials,
            'equipment': equipment,
            'labor': labor,
            'services': services,
            'totals': {
                'baseCost': round(cost_summary.get('total_material_cost', 0), 2),
                'materialsTotal': round(
                    sum(m['qty'] * m['unitCost'] for m in materials), 2
                ),
                'eqTotal': round(
                    sum(e['qty'] * (e['supplyCost'] + e['installCost']) for e in equipment), 2
                ),
                'laborTotal': round(
                    sum(l['workers'] * l['days'] * l['dailyCost'] for l in labor), 2
                ),
                'servicesTotal': round(
                    sum(s['amount'] for s in services), 2
                ),
                'grandTotal': round(cost_summary.get('total_cost', 0), 2),
            },
            'summary': {
                'sprinklers': len(entities.get('sprinklers', [])),
                'pipes': len(entities.get('pipes', [])),
                'pumps': len(entities.get('pumps', [])),
                'gas_systems': len(entities.get('gas_systems', [])),
                'hose_cabinets': len(entities.get('hose_cabinets', [])),
            },
            'currency': 'SAR',
        }
        
        # حفظ
        os.makedirs(output_dir, exist_ok=True)
        filename = f"fire_pricing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(fire_pricing_data, f, ensure_ascii=False, indent=2)
        
        return filepath