"""
حاسبة التكاليف لأنظمة مكافحة الحريق
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

from cost_data import (
    SPRINKLER_COSTS,
    PIPE_COSTS,
    PUMP_COSTS,
    GAS_SYSTEM_COSTS,
    HOSE_CABINET_COSTS,
    VALVE_COSTS,
    ADDITIONAL_COSTS,
    CURRENCY
)


class CostCalculator:
    """حاسبة تكاليف أنظمة مكافحة الحريق"""
    
    def __init__(self, entities: Dict[str, List[Dict]]):
        self.entities = entities
        self.cost_items = []
        self.total_material_cost = 0
        self.total_labor_cost = 0
        self.total_cost = 0
    
    def calculate_all(self) -> Dict[str, Any]:
        """حساب جميع التكاليف"""
        self._calculate_sprinklers()
        self._calculate_pipes()
        self._calculate_pumps()
        self._calculate_gas_systems()
        self._calculate_hose_cabinets()
        self._calculate_valves()
        self._calculate_additional_costs()
        
        return self.get_summary()
    
    def _calculate_sprinklers(self):
        """حساب تكلفة الرشاشات"""
        sprinklers = self.entities.get('sprinklers', [])
        
        if not sprinklers:
            return
        
        # تجميع حسب النوع
        types = {}
        for sprinkler in sprinklers:
            stype = sprinkler.get('sprinkler_type', 'standard')
            types[stype] = types.get(stype, 0) + 1
        
        total = 0
        for stype, count in types.items():
            unit_price = SPRINKLER_COSTS.get('pendant', {}).get('standard', 45)
            subtotal = unit_price * count
            total += subtotal
            
            self.cost_items.append({
                'item': f'رشاشات {stype}',
                'quantity': count,
                'unit': 'رشاش',
                'unit_price': unit_price,
                'subtotal': subtotal
            })
        
        self.total_material_cost += total
    
    def _calculate_pipes(self):
        """حساب تكلفة المواسير"""
        pipes = self.entities.get('pipes', [])
        
        if not pipes:
            return
        
        # تجميع حسب القطر
        diameters = {}
        for pipe in pipes:
            diameter = pipe.get('diameter', 50)
            length = pipe.get('length', 0)
            diameters[diameter] = diameters.get(diameter, 0) + length
        
        total = 0
        for diameter, length in diameters.items():
            # إيجاد أقرب قطر في جدول الأسعار
            price_table = PIPE_COSTS.get('steel', {})
            closest = min(price_table.keys(), key=lambda x: abs(x - diameter))
            unit_price = price_table[closest].get('sch40', 50)
            subtotal = unit_price * length
            total += subtotal
            
            self.cost_items.append({
                'item': f'مواسير فولاذ {closest} مم',
                'quantity': round(length, 2),
                'unit': 'متر',
                'unit_price': unit_price,
                'subtotal': round(subtotal, 2)
            })
        
        self.total_material_cost += total
    
    def _calculate_pumps(self):
        """حساب تكلفة المضخات"""
        pumps = self.entities.get('pumps', [])
        
        if not pumps:
            return
        
        total = 0
        for pump in pumps:
            ptype = pump.get('pump_type', 'electric')
            
            # أسعار حسب النوع
            if ptype == 'electric':
                unit_price = PUMP_COSTS['electric'].get(500, 45000)
            elif ptype == 'diesel':
                unit_price = PUMP_COSTS['diesel'].get(500, 65000)
            elif ptype == 'jockey':
                unit_price = PUMP_COSTS['jockey'].get(100, 12000)
            else:
                unit_price = 45000
            
            total += unit_price
            self.cost_items.append({
                'item': f'مضخة {ptype}',
                'quantity': 1,
                'unit': 'مضخة',
                'unit_price': unit_price,
                'subtotal': unit_price
            })
        
        self.total_material_cost += total
    
    def _calculate_gas_systems(self):
        """حساب تكلفة أنظمة الغاز"""
        gas_systems = self.entities.get('gas_systems', [])
        
        if not gas_systems:
            return
        
        total = 0
        for system in gas_systems:
            gas_type = system.get('gas_type', 'FM-200')
            price_table = GAS_SYSTEM_COSTS.get(gas_type, {})
            unit_price = price_table.get('cylinder_small', 8500)
            
            total += unit_price
            self.cost_items.append({
                'item': f'نظام {gas_type}',
                'quantity': 1,
                'unit': 'نظام',
                'unit_price': unit_price,
                'subtotal': unit_price
            })
        
        self.total_material_cost += total
    
    def _calculate_hose_cabinets(self):
        """حساب تكلفة خزانات الخراطيم"""
        cabinets = self.entities.get('hose_cabinets', [])
        
        if not cabinets:
            return
        
        unit_price = HOSE_CABINET_COSTS.get('standard', 850)
        count = len(cabinets)
        subtotal = unit_price * count
        
        self.cost_items.append({
            'item': 'خزانات خرطوم',
            'quantity': count,
            'unit': 'خزانة',
            'unit_price': unit_price,
            'subtotal': subtotal
        })
        
        self.total_material_cost += subtotal
    
    def _calculate_valves(self):
        """حساب تكلفة الصمامات"""
        valves = self.entities.get('valves', [])
        
        if not valves:
            return
        
        unit_price = VALVE_COSTS.get('zone_control', 350)
        count = len(valves)
        subtotal = unit_price * count
        
        self.cost_items.append({
            'item': 'صمامات',
            'quantity': count,
            'unit': 'صمام',
            'unit_price': unit_price,
            'subtotal': subtotal
        })
        
        self.total_material_cost += subtotal
    
    def _calculate_additional_costs(self):
        """حساب التكاليف الإضافية"""
        labor = self.total_material_cost * ADDITIONAL_COSTS['labor_ratio']
        engineering = self.total_material_cost * ADDITIONAL_COSTS['engineering_ratio']
        overhead = self.total_material_cost * ADDITIONAL_COSTS['overhead_ratio']
        contingency = self.total_material_cost * ADDITIONAL_COSTS['contingency']
        
        self.total_labor_cost = labor
        
        subtotal_with_labor = self.total_material_cost + labor + engineering + overhead
        profit = subtotal_with_labor * ADDITIONAL_COSTS['profit_margin']
        
        self.total_cost = subtotal_with_labor + profit + contingency
        
        self.cost_items.extend([
            {
                'item': 'تكلفة التركيب (35%)',
                'quantity': 1,
                'unit': 'بند',
                'unit_price': labor,
                'subtotal': labor
            },
            {
                'item': 'التصميم والهندسة (10%)',
                'quantity': 1,
                'unit': 'بند',
                'unit_price': engineering,
                'subtotal': engineering
            },
            {
                'item': 'مصاريف إدارية (15%)',
                'quantity': 1,
                'unit': 'بند',
                'unit_price': overhead,
                'subtotal': overhead
            },
            {
                'item': 'هامش الربح (20%)',
                'quantity': 1,
                'unit': 'بند',
                'unit_price': profit,
                'subtotal': profit
            },
            {
                'item': 'احتياطي (5%)',
                'quantity': 1,
                'unit': 'بند',
                'unit_price': contingency,
                'subtotal': contingency
            },
        ])
    
    def get_summary(self) -> Dict[str, Any]:
        """ملخص التكاليف"""
        return {
            'currency': CURRENCY,
            'total_material_cost': round(self.total_material_cost, 2),
            'total_labor_cost': round(self.total_labor_cost, 2),
            'total_cost': round(self.total_cost, 2),
            'items': self.cost_items,
        }
    
    def print_summary(self):
        """طباعة ملخص التكاليف"""
        summary = self.get_summary()
        
        print("\n" + "=" * 60)
        print("💰 ملخص التكاليف")
        print("=" * 60)
        print(f"\n📦 تكلفة المواد: {summary['total_material_cost']:,.2f} {CURRENCY}")
        print(f"🔧 تكلفة التركيب: {summary['total_labor_cost']:,.2f} {CURRENCY}")
        print(f"\n📊 الإجمالي: {summary['total_cost']:,.2f} {CURRENCY}")
        print(f"\n📋 تفاصيل البنود:")
        print("-" * 60)
        
        for item in summary['items']:
            print(f"  {item['item']}: {item['subtotal']:,.2f} {CURRENCY}")