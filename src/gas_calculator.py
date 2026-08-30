# src/gas_calculator.py - تحديث
"""
حاسبة أنظمة الإطفاء بالغاز
تدعم: CO2, FM-200, Novec 1230
"""

import math
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

from gas_data import GAS_COSTS


class GasSuppressionCalculator:
    """حاسبة أنظمة الإطفاء بالغاز"""
    
    GAS_PROPERTIES = {
        'FM-200': {
            'chemical_formula': 'C3HF7',
            'molecular_weight': 170.03,
            'density_liquid': 1.26,
            'specific_volume': 0.1269,
            'min_concentration': 7.9,
            'max_concentration': 10.5,
            'noael': 9.0,
            'loael': 10.5,
            'discharge_time': 10,
        },
        'Novec 1230': {
            'chemical_formula': 'C6F12O',
            'molecular_weight': 316.04,
            'density_liquid': 1.60,
            'specific_volume': 0.0713,
            'min_concentration': 4.2,
            'max_concentration': 5.9,
            'noael': 10.0,
            'loael': 12.0,
            'discharge_time': 10,
        },
        'CO2': {
            'chemical_formula': 'CO2',
            'molecular_weight': 44.01,
            'density_liquid': 0.77,
            'specific_volume': 0.505,
            'min_concentration': 34.0,
            'max_concentration': 75.0,
            'noael': None,
            'loael': None,
            'discharge_time': 60,
        }
    }
    
    # مناطق الحماية
    PROTECTION_AREAS = {
        'total_flooding': 'إغراق كامل للغرفة',
        'raised_floor': 'تحت الأرضية المرتفعة',
        'ceiling_void': 'فوق السقف المستعار',
        'combined': 'مشترك (أرضية + سقف + غرفة)',
    }
    
    def __init__(self):
        pass
    
    def calculate_agent_quantity(self, 
                                  gas_type: str,
                                  room_volume: float,
                                  protection_area: str = 'total_flooding',
                                  temperature_c: float = 21.0,
                                  altitude_m: float = 0,
                                  safety_factor: float = 1.1) -> Dict[str, Any]:
        """
        حساب كمية الغاز المطلوبة
        
        Args:
            gas_type: نوع الغاز
            room_volume: حجم المنطقة المحمية (م³)
            protection_area: منطقة الحماية
            temperature_c: درجة الحرارة
            altitude_m: الارتفاع عن سطح البحر
            safety_factor: عامل الأمان
        """
        if gas_type not in self.GAS_PROPERTIES:
            logger.error(f"غاز غير مدعوم: {gas_type}")
            return {}
        
        gas = self.GAS_PROPERTIES[gas_type]
        
        c = gas['min_concentration'] / 100.0
        s = gas['specific_volume']
        
        # تصحيح درجة الحرارة
        temperature_k = temperature_c + 273.15
        s_corrected = s * (temperature_k / 294.15)
        
        # تصحيح الارتفاع
        if altitude_m > 0:
            pressure_factor = math.exp(-altitude_m / 8500)
            s_corrected = s_corrected / pressure_factor
        
        # حجم إضافي حسب منطقة الحماية
        volume_factor = self._get_volume_factor(protection_area)
        effective_volume = room_volume * volume_factor
        
        # حساب الوزن
        required_weight = (effective_volume * c) / (s_corrected * (1 - c))
        total_weight = required_weight * safety_factor
        
        # حساب الأسطوانات
        cylinders = self._calculate_cylinders(gas_type, total_weight)
        
        # حساب عدد الفوهات
        nozzles = self._calculate_nozzles(gas_type, effective_volume, protection_area)
        
        # حساب التكلفة
        cost = self.calculate_system_cost(gas_type, total_weight, cylinders, nozzles, protection_area)
        
        return {
            'gas_type': gas_type,
            'room_volume': room_volume,
            'effective_volume': round(effective_volume, 2),
            'protection_area': protection_area,
            'protection_area_arabic': self.PROTECTION_AREAS.get(protection_area, ''),
            'temperature_c': temperature_c,
            'altitude_m': altitude_m,
            'concentration': gas['min_concentration'],
            'required_weight_kg': round(required_weight, 2),
            'total_weight_kg': round(total_weight, 2),
            'cylinders': cylinders,
            'nozzles': nozzles,
            'discharge_time_sec': gas['discharge_time'],
            'safety_factor': safety_factor,
            'cost': cost,
        }
    
    def _get_volume_factor(self, protection_area: str) -> float:
        """عامل الحجم حسب منطقة الحماية"""
        factors = {
            'total_flooding': 1.0,       # كامل الغرفة
            'raised_floor': 0.5,         # نصف الحجم تقريباً (فوق الأرضية)
            'ceiling_void': 0.4,         # 40% من الحجم (فوق السقف)
            'combined': 1.3,             # زيادة 30% للمناطق المشتركة
        }
        return factors.get(protection_area, 1.0)
    
    def _calculate_cylinders(self, gas_type: str, total_weight: float) -> list:
        """حساب عدد وأحجام الأسطوانات"""
        cylinder_sizes = {
            'FM-200': [16, 32, 45, 64, 100, 150, 180],
            'Novec 1230': [16, 32, 45, 64, 100, 150],
            'CO2': [30, 45, 68, 100, 150],
        }
        
        sizes = cylinder_sizes.get(gas_type, [64])
        remaining = total_weight
        cylinders = []
        
        for size in sorted(sizes, reverse=True):
            count = int(remaining // size)
            if count > 0:
                cylinders.append({
                    'size_kg': size,
                    'count': count,
                    'total_kg': size * count
                })
                remaining -= size * count
        
        if remaining > 0:
            smallest = sorted(sizes)[0]
            cylinders.append({
                'size_kg': smallest,
                'count': 1,
                'total_kg': smallest
            })
        
        return cylinders
    
    def _calculate_nozzles(self, gas_type: str, volume: float, protection_area: str) -> int:
        """حساب عدد الفوهات المطلوبة"""
        # قواعد تقريبية
        nozzles_per_volume = {
            'FM-200': 50,      # فوهة لكل 50 م³
            'Novec 1230': 45,  # فوهة لكل 45 م³
            'CO2': 60,         # فوهة لكل 60 م³
        }
        
        base = nozzles_per_volume.get(gas_type, 50)
        
        # تعديل حسب منطقة الحماية
        if protection_area in ['raised_floor', 'ceiling_void']:
            base = base * 0.6  # فوهات أقل للمناطق الصغيرة
        
        nozzles = max(1, math.ceil(volume / base))
        return nozzles
    
    def calculate_system_cost(self, gas_type: str, total_weight: float, 
                               cylinders: list, nozzles: int, 
                               protection_area: str) -> Dict[str, Any]:
        """حساب تكلفة النظام"""
        costs = GAS_COSTS.get(gas_type, {})
        
        # تكلفة الغاز
        gas_cost = total_weight * costs.get('per_kg', 350)
        
        # تكلفة الأسطوانات
        cylinder_cost = 0
        for cylinder in cylinders:
            size = cylinder['size_kg']
            if size <= 32:
                unit_price = costs.get('cylinder_small', 8500)
            elif size <= 64:
                unit_price = costs.get('cylinder_medium', 15000)
            else:
                unit_price = costs.get('cylinder_large', 25000)
            cylinder_cost += unit_price * cylinder['count']
        
        # تكلفة الفوهات
        nozzle_cost = nozzles * costs.get('nozzle', 350)
        
        # لوحة تحكم
        panel_cost = costs.get('control_panel', 12000)
        
        # كواشف (افتراض 2 كاشف)
        detector_cost = 2 * costs.get('detector', 450)
        
        # مواسير (تقدير 15 متر)
        pipe_cost = 15 * costs.get('pipe_per_meter', 180)
        
        # إجمالي المواد
        material_cost = gas_cost + cylinder_cost + nozzle_cost + panel_cost + detector_cost + pipe_cost
        
        # تكلفة التركيب
        installation = material_cost * costs.get('installation_ratio', 0.30)
        
        # الإجمالي
        total_cost = material_cost + installation
        
        return {
            'gas_cost': round(gas_cost, 2),
            'cylinder_cost': round(cylinder_cost, 2),
            'nozzle_cost': round(nozzle_cost, 2),
            'panel_cost': panel_cost,
            'detector_cost': detector_cost,
            'pipe_cost': pipe_cost,
            'material_cost': round(material_cost, 2),
            'installation_cost': round(installation, 2),
            'total_cost': round(total_cost, 2),
        }
    
    def calculate_room_volume(self, length: float, width: float, height: float) -> float:
        """حساب حجم الغرفة"""
        return length * width * height
    
    def print_calculation(self, results: Dict[str, Any]):
        """طباعة النتائج"""
        if not results:
            return
        
        print("\n" + "=" * 60)
        print("🧯 حساب نظام الإطفاء بالغاز")
        print("=" * 60)
        print(f"نوع الغاز: {results['gas_type']}")
        print(f"منطقة الحماية: {results['protection_area_arabic']}")
        print(f"حجم الغرفة: {results['room_volume']:.2f} م³")
        print(f"الحجم الفعال: {results['effective_volume']:.2f} م³")
        print(f"درجة الحرارة: {results['temperature_c']}°C")
        print(f"التركيز: {results['concentration']}%")
        print(f"الوزن المطلوب: {results['required_weight_kg']} كجم")
        print(f"الوزن مع الأمان: {results['total_weight_kg']} كجم")
        print(f"عدد الفوهات: {results['nozzles']}")
        print(f"زمن التفريغ: {results['discharge_time_sec']} ثانية")
        
        print(f"\n📦 الأسطوانات:")
        for cylinder in results['cylinders']:
            print(f"  • {cylinder['count']} × {cylinder['size_kg']} كجم = {cylinder['total_kg']} كجم")
        
        cost = results.get('cost', {})
        if cost:
            print(f"\n💰 التكلفة:")
            print(f"  • الغاز: {cost['gas_cost']:,.2f} ريال")
            print(f"  • الأسطوانات: {cost['cylinder_cost']:,.2f} ريال")
            print(f"  • الفوهات: {cost['nozzle_cost']:,.2f} ريال")
            print(f"  • لوحة التحكم: {cost['panel_cost']:,.2f} ريال")
            print(f"  • التركيب: {cost['installation_cost']:,.2f} ريال")
            print(f"  • الإجمالي: {cost['total_cost']:,.2f} ريال")