# src/integrated_report.py
"""
تقرير موحد يجمع كل التكاليف
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List


class IntegratedReport:
    """تقرير موحد شامل"""
    
    def __init__(self, project_name: str = ""):
        self.project_name = project_name
        self.cad_costs = None      # تكاليف من تحليل CAD
        self.gas_costs = []        # قائمة تكاليف أنظمة الغاز
        self.manual_items = []     # بنود يدوية إضافية
    
    def add_cad_costs(self, cost_summary: Dict[str, Any]):
        """إضافة تكاليف CAD"""
        self.cad_costs = cost_summary
    
    def add_gas_calculation(self, gas_results):
        """إضافة حساب نظام غاز"""
        if not hasattr(self, 'gas_costs'):
            self.gas_costs = []
        self.gas_costs.append(gas_results)
    
    def add_manual_item(self, item_name: str, quantity: float, unit_price: float):
        """إضافة بند يدوي"""
        self.manual_items.append({
            'item': item_name,
            'quantity': quantity,
            'unit_price': unit_price,
            'subtotal': quantity * unit_price
        })
    
    def generate_total_report(self) -> Dict[str, Any]:
        """توليد التقرير الموحد"""
        total_material = 0
        total_installation = 0
        
        # تكاليف CAD
        if self.cad_costs:
            total_material += self.cad_costs.get('total_material_cost', 0)
            total_installation += self.cad_costs.get('total_labor_cost', 0)
        
        # تكاليف الغاز
        gas_total = 0
        for gas in self.gas_costs:
            cost = gas.get('cost', {})
            gas_total += cost.get('total_cost', 0)
        
        total_material += gas_total
        
        # البنود اليدوية
        manual_total = sum(item['subtotal'] for item in self.manual_items)
        total_material += manual_total
        
        # الإجمالي الكلي
        grand_total = total_material + total_installation
        
        return {
            'project_name': self.project_name,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'cad_costs': self.cad_costs,
            'gas_systems': self.gas_costs,
            'manual_items': self.manual_items,
            'total_material': round(total_material, 2),
            'total_installation': round(total_installation, 2),
            'grand_total': round(grand_total, 2),
        }
    
    def save_json(self, output_dir: str = "reports") -> str:
        """حفظ التقرير الموحد"""
        report = self.generate_total_report()
        
        os.makedirs(output_dir, exist_ok=True)
        filename = f"integrated_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def print_summary(self):
        """طباعة الملخص"""
        report = self.generate_total_report()
        
        print("\n" + "=" * 60)
        print("📊 التقرير الموحد النهائي")
        print("=" * 60)
        print(f"المشروع: {report['project_name'] or 'غير محدد'}")
        print(f"التاريخ: {report['date']}")
        print("-" * 60)
        
        if self.cad_costs:
            print(f"تكاليف نظام الرشاشات: {self.cad_costs.get('total_material_cost', 0):,.2f} ريال")
            print(f"  (تشمل: رشاشات، مواسير، مضخات)")
        
        if self.gas_costs:
            gas_total = sum(g.get('cost', {}).get('total_cost', 0) for g in self.gas_costs)
            print(f"تكاليف أنظمة الغاز ({len(self.gas_costs)} نظام): {gas_total:,.2f} ريال")
        
        if self.manual_items:
            manual_total = sum(item['subtotal'] for item in self.manual_items)
            print(f"بنود إضافية: {manual_total:,.2f} ريال")
        
        print("-" * 60)
        print(f"إجمالي المواد: {report['total_material']:,.2f} ريال")
        print(f"إجمالي التركيب: {report['total_installation']:,.2f} ريال")
        print(f"💰 الإجمالي الكلي: {report['grand_total']:,.2f} ريال")
        print("=" * 60)