# src/pump_selector.py
"""
اختيار المضخة المناسبة من الكتالوج
"""

import json
import os
import logging

logger = logging.getLogger(__name__)


class PumpSelector:
    """اختيار المضخات من الكتالوج"""
    
    def __init__(self):
        self.catalog = self._load_catalog()
    
    def _load_catalog(self):
        """تحميل الكتالوج"""
        path = os.path.join(os.path.dirname(__file__), '..', 'data', 'pumps_catalog.json')
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"فشل تحميل الكتالوج: {e}")
            return {'manufacturers': {}}
    
    def find_matching_pumps(self, flow_gpm: float, pressure_bar: float):
        """
        البحث عن مضخات مناسبة
        
        Args:
            flow_gpm: التدفق المطلوب (GPM)
            pressure_bar: الضغط المطلوب (bar)
            
        Returns:
            list: المضخات المناسبة
        """
        matches = []
        
        for manufacturer, data in self.catalog.get('manufacturers', {}).items():
            for pump in data.get('pumps', []):
                # المضخة مناسبة إذا كان تدفقها ≥ 90% من المطلوب
                # وضغطها ≥ المطلوب
                if (pump['flow_gpm'] >= flow_gpm * 0.9 and 
                    pump['pressure_bar'] >= pressure_bar):
                    matches.append({
                        'manufacturer': manufacturer,
                        'model': pump['model'],
                        'type': pump['type'],
                        'flow_gpm': pump['flow_gpm'],
                        'pressure_bar': pump['pressure_bar'],
                        'power_kw': pump['power_kw'],
                        'price_sar': pump['price_sar'],
                    })
        
        # ترتيب حسب السعر
        matches.sort(key=lambda x: x['price_sar'])
        
        return matches
    
    def print_recommendations(self, matches, required_flow, required_pressure):
        """طباعة التوصيات"""
        print(f"\n" + "=" * 60)
        print(f"🔧 المضخات المقترحة")
        print(f"   المطلوب: {required_flow:.0f} GPM @ {required_pressure:.1f} bar")
        print("=" * 60)
        
        if not matches:
            print("❌ لا توجد مضخات مناسبة")
            return
        
        for i, pump in enumerate(matches[:5], 1):
            print(f"\n{i}. {pump['manufacturer']} - {pump['model']}")
            print(f"   التدفق: {pump['flow_gpm']} GPM")
            print(f"   الضغط: {pump['pressure_bar']} bar")
            print(f"   القدرة: {pump['power_kw']} kW")
            print(f"   النوع: {pump['type']}")
            print(f"   السعر: {pump['price_sar']:,.0f} ريال")