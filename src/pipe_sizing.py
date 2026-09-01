# src/pipe_sizing.py
"""
حساب أقطار المواسير من ملف CAD مباشرة
مع تقدير الملحقات والفاقد في الضغط
وفقاً لمعايير NFPA 13
"""

import math
import json
import os
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class PipeSizing:
    """حاسبة أقطار المواسير والملحقات"""
    
    # جدول NFPA 13 - عدد الرشاشات لكل قطر (شجري)
    SPRINKLER_CAPACITY = [
        (25, 2),     # 1" = 2 رشاش
        (32, 3),     # 1¼" = 3 رشاش
        (40, 5),     # 1½" = 5 رشاش
        (50, 10),    # 2" = 10 رشاش
        (65, 20),    # 2½" = 20 رشاش
        (80, 40),    # 3" = 40 رشاش
        (100, 100),  # 4" = 100 رشاش
        (150, 250),  # 6" = 250 رشاش
        (200, 500),  # 8" = 500 رشاش
        (250, 1000), # 10" = 1000 رشاش
        (300, 2000), # 12" = 2000 رشاش
    ]
    
    # نسب الملحقات من طول الماسورة
    FITTINGS_RATIO = {
        'elbows': 0.10,    # كوع لكل 10 متر
        'tees': 0.05,      # تي لكل 20 متر
        'reducers': 0.02,  # نقاص لكل 50 متر
        'unions': 0.03,    # وصلة لكل 33 متر
    }
    
    # أسعار الملحقات (ريال) - قابلة للتحديث
    FITTINGS_COSTS = {
        25: {'elbow': 15, 'tee': 22, 'reducer': 18, 'union': 12},
        32: {'elbow': 20, 'tee': 30, 'reducer': 25, 'union': 15},
        40: {'elbow': 25, 'tee': 38, 'reducer': 32, 'union': 18},
        50: {'elbow': 35, 'tee': 52, 'reducer': 45, 'union': 25},
        65: {'elbow': 55, 'tee': 82, 'reducer': 70, 'union': 38},
        80: {'elbow': 75, 'tee': 112, 'reducer': 95, 'union': 50},
        100: {'elbow': 110, 'tee': 165, 'reducer': 140, 'union': 75},
        150: {'elbow': 220, 'tee': 330, 'reducer': 280, 'union': 150},
        200: {'elbow': 380, 'tee': 570, 'reducer': 480, 'union': 260},
        250: {'elbow': 600, 'tee': 900, 'reducer': 750, 'union': 400},
        300: {'elbow': 900, 'tee': 1350, 'reducer': 1100, 'union': 600},
    }
    
    # أسعار ملحقات الرشاشات (1" = 25 مم)
    SPRINKLER_FITTINGS_COSTS = {
        'tee_1x1x1': 22,
        'tee_1x1x0.5': 25,
        'elbow_1': 15,
        'reducer_1x0.5': 18,
    }
    
    def __init__(self):
        pass
    
    def calculate_diameter_by_sprinkler_count(self, sprinkler_count: int) -> int:
        """
        تحديد القطر حسب عدد الرشاشات (NFPA 13 - شجري)
        
        Args:
            sprinkler_count: عدد الرشاشات
            
        Returns:
            القطر (مم)
        """
        if sprinkler_count <= 0:
            return 25
        
        for diameter, capacity in self.SPRINKLER_CAPACITY:
            if sprinkler_count <= capacity:
                return diameter
        
        return 300
    
    def calculate_system_diameters(self, sprinkler_count: int) -> Dict[str, Any]:
        """
        حساب أقطار المنظومة حسب عدد الرشاشات
        
        Args:
            sprinkler_count: إجمالي عدد الرشاشات
            
        Returns:
            dict: أقطار كل قسم
        """
        # الخط الرئيسي - يغذي كل الرشاشات
        main_diameter = self.calculate_diameter_by_sprinkler_count(sprinkler_count)
        
        # الفروع - تقريباً نصف الرشاشات
        branch_count = sprinkler_count // 2
        branch_diameter = self.calculate_diameter_by_sprinkler_count(branch_count)
        
        # خطوط الرشاشات - فرع يغذي 10 رشاشات
        line_count = min(10, max(2, sprinkler_count // 10))
        line_diameter = self.calculate_diameter_by_sprinkler_count(line_count)
        
        return {
            'main': {
                'sprinklers': sprinkler_count,
                'diameter': main_diameter,
            },
            'branches': {
                'sprinklers': branch_count,
                'diameter': branch_diameter,
            },
            'sprinkler_lines': {
                'sprinklers': line_count,
                'diameter': line_diameter,
            },
        }
    
    def estimate_fittings(self, pipe_length_m: float, diameter_mm: int) -> Dict[str, Any]:
        """
        تقدير عدد الملحقات من طول الماسورة
        
        Args:
            pipe_length_m: طول الماسورة (متر)
            diameter_mm: القطر (مم)
            
        Returns:
            dict: عدد وتكلفة الملحقات
        """
        # عدد الملحقات
        elbows = max(1, int(pipe_length_m * self.FITTINGS_RATIO['elbows']))
        tees = max(1, int(pipe_length_m * self.FITTINGS_RATIO['tees']))
        reducers = max(0, int(pipe_length_m * self.FITTINGS_RATIO['reducers']))
        unions = max(1, int(pipe_length_m * self.FITTINGS_RATIO['unions']))
        
        # أسعار الملحقات
        costs = self.FITTINGS_COSTS.get(diameter_mm, self.FITTINGS_COSTS[50])
        
        elbow_cost = elbows * costs['elbow']
        tee_cost = tees * costs['tee']
        reducer_cost = reducers * costs['reducer']
        union_cost = unions * costs['union']
        
        total = elbow_cost + tee_cost + reducer_cost + union_cost
        
        return {
            'diameter_mm': diameter_mm,
            'pipe_length_m': pipe_length_m,
            'elbows': {'count': elbows, 'unit_cost': costs['elbow'], 'total': elbow_cost},
            'tees': {'count': tees, 'unit_cost': costs['tee'], 'total': tee_cost},
            'reducers': {'count': reducers, 'unit_cost': costs['reducer'], 'total': reducer_cost},
            'unions': {'count': unions, 'unit_cost': costs['union'], 'total': union_cost},
            'total_cost': total,
        }
    
    def calculate_sprinkler_fittings(self, 
                                      sprinkler_count: int,
                                      sprinkler_type: str = 'pendant') -> Dict[str, Any]:
        """
        حساب ملحقات الرشاشات بدقة
        
        Args:
            sprinkler_count: عدد الرشاشات
            sprinkler_type: نوع الرشاش (pendant/upright)
            
        Returns:
            dict: عدد وتكلفة الملحقات
        """
        if sprinkler_type == 'upright':
            tees = sprinkler_count
            elbows = max(1, sprinkler_count // 10)
            reducers = sprinkler_count
        else:
            tees = sprinkler_count
            elbows = sprinkler_count * 2
            reducers = sprinkler_count
        
        costs = self.SPRINKLER_FITTINGS_COSTS
        
        tee_cost = tees * costs.get('tee_1x1x0.5', 25)
        elbow_cost = elbows * costs.get('elbow_1', 15)
        reducer_cost = reducers * costs.get('reducer_1x0.5', 18)
        
        return {
            'sprinkler_type': sprinkler_type,
            'sprinkler_count': sprinkler_count,
            'tees': {'count': tees, 'unit_cost': costs.get('tee_1x1x0.5', 25), 'total': tee_cost},
            'elbows': {'count': elbows, 'unit_cost': costs.get('elbow_1', 15), 'total': elbow_cost},
            'reducers': {'count': reducers, 'unit_cost': costs.get('reducer_1x0.5', 18), 'total': reducer_cost},
            'total_cost': tee_cost + elbow_cost + reducer_cost,
        }
    
    def calculate_pressure_loss(self, 
                                 diameter_mm: int,
                                 length_m: float,
                                 material: str = 'steel') -> float:
        """
        حساب الفاقد في الضغط - طريقة مبسطة واقعية
        
        Args:
            diameter_mm: القطر (مم)
            length_m: الطول (متر)
            material: المادة
            
        Returns:
            الفاقد (bar)
        """
        if diameter_mm <= 0 or length_m <= 0:
            return 0.0
        
        # الفاقد التقريبي (bar/30م) حسب القطر
        loss_factors = {
            25: 0.30,
            32: 0.22,
            40: 0.15,
            50: 0.10,
            65: 0.07,
            80: 0.05,
            100: 0.03,
            150: 0.015,
            200: 0.008,
            250: 0.004,
            300: 0.002,
        }
        
        closest = min(loss_factors.keys(), key=lambda x: abs(x - diameter_mm))
        factor = loss_factors[closest]
        
        pressure_loss = (length_m / 30) * factor
        
        return round(pressure_loss, 4)
    
    def calculate_complete_piping(self,
                                   total_pipe_length_m: float,
                                   sprinkler_count: int = 0,
                                   sprinkler_type: str = 'pendant',
                                   material: str = 'steel') -> Dict[str, Any]:
        """
        حساب كامل للمواسير والملحقات والضغط
        
        Args:
            total_pipe_length_m: إجمالي طول المواسير (متر)
            sprinkler_count: عدد الرشاشات
            sprinkler_type: نوع الرشاش (pendant/upright)
            material: مادة المواسير
            
        Returns:
            dict: نتائج شاملة
        """
        # 1. أقطار حسب عدد الرشاشات
        diameters = self.calculate_system_diameters(sprinkler_count)
        
        # 2. ملحقات الخطوط (للخط الرئيسي)
        main_diameter = diameters['main']['diameter']
        fittings = self.estimate_fittings(total_pipe_length_m, main_diameter)
        
        # 3. الفاقد في الضغط (على أقسام)
        main_length = total_pipe_length_m * 0.3
        branch_length = total_pipe_length_m * 0.4
        sprinkler_length = total_pipe_length_m * 0.3
        
        main_pressure = self.calculate_pressure_loss(
            diameters['main']['diameter'],
            main_length,
            material
        )
        
        branch_pressure = self.calculate_pressure_loss(
            diameters['branches']['diameter'],
            branch_length,
            material
        )
        
        sprinkler_pressure = self.calculate_pressure_loss(
            diameters['sprinkler_lines']['diameter'],
            sprinkler_length,
            material
        )
        
        pressure_loss = round(main_pressure + branch_pressure + sprinkler_pressure, 4)
        
        # 4. ملحقات الرشاشات
        sprinkler_fittings = None
        if sprinkler_count > 0:
            sprinkler_fittings = self.calculate_sprinkler_fittings(
                sprinkler_count, sprinkler_type
            )
        
        return {
            'diameters': diameters,
            'fittings': fittings,
            'sprinkler_fittings': sprinkler_fittings,
            'pressure_loss_bar': pressure_loss,
            'material': material,
        }
    
    def print_results(self, results: Dict[str, Any]):
        """طباعة النتائج"""
        if not results:
            return
        
        print("\n" + "=" * 60)
        print("📐 حساب المواسير والملحقات")
        print("=" * 60)
        
        print(f"\nأقطار المنظومة (NFPA 13 - شجري):")
        for section, data in results['diameters'].items():
            print(f"  • {section}: {data['diameter']} مم (يغذي {data['sprinklers']} رشاش)")
        
        fittings = results['fittings']
        print(f"\nملحقات الخطوط (للقطر {fittings['diameter_mm']} مم):")
        print(f"  • أكواع: {fittings['elbows']['count']} × {fittings['elbows']['unit_cost']} = {fittings['elbows']['total']} ريال")
        print(f"  • تيهات: {fittings['tees']['count']} × {fittings['tees']['unit_cost']} = {fittings['tees']['total']} ريال")
        print(f"  • نقاصات: {fittings['reducers']['count']} × {fittings['reducers']['unit_cost']} = {fittings['reducers']['total']} ريال")
        print(f"  • وصلات: {fittings['unions']['count']} × {fittings['unions']['unit_cost']} = {fittings['unions']['total']} ريال")
        print(f"  • الإجمالي: {fittings['total_cost']} ريال")
        
        sprinkler_fittings = results.get('sprinkler_fittings')
        if sprinkler_fittings:
            print(f"\nملحقات الرشاشات ({sprinkler_fittings['sprinkler_type']}):")
            print(f"  • تيهات: {sprinkler_fittings['tees']['count']} × {sprinkler_fittings['tees']['unit_cost']} = {sprinkler_fittings['tees']['total']} ريال")
            print(f"  • أكواع: {sprinkler_fittings['elbows']['count']} × {sprinkler_fittings['elbows']['unit_cost']} = {sprinkler_fittings['elbows']['total']} ريال")
            print(f"  • نقاصات: {sprinkler_fittings['reducers']['count']} × {sprinkler_fittings['reducers']['unit_cost']} = {sprinkler_fittings['reducers']['total']} ريال")
            print(f"  • الإجمالي: {sprinkler_fittings['total_cost']} ريال")
        
        print(f"\nالضغط:")
        print(f"  • الفاقد الكلي: {results['pressure_loss_bar']} bar")
        
        print("=" * 60)


if __name__ == "__main__":
    """اختبار سريع"""
    calc = PipeSizing()
    
    results = calc.calculate_complete_piping(
        total_pipe_length_m=4992.61,
        sprinkler_count=1086,
        sprinkler_type='pendant',
        material='steel'
    )
    
    calc.print_results(results)