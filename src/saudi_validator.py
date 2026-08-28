# src/saudi_validator.py
"""
التحقق من التصميم مقابل الكود السعودي (SBC 801)
"""

import math
from typing import List, Dict, Any, Tuple
from utils.constants import SaudiCode


class SaudiCodeValidator:
    """مدقق الكود السعودي للحماية من الحريق"""
    
    def __init__(self, entities: Dict[str, List[Dict]]):
        self.entities = entities
        self.violations = []
        self.warnings = []
    
    def validate_all(self) -> Dict[str, List[Dict]]:
        """تشغيل جميع الفحوصات السعودية"""
        self.check_building_type_requirements()
        self.check_water_storage_duration()
        self.check_temperature_considerations()
        self.check_local_amendments()
        
        return {
            'violations': self.violations,
            'warnings': self.warnings
        }
    
    def check_building_type_requirements(self):
        """فحص متطلبات نوع المبنى"""
        sprinklers = self.entities.get('sprinklers', [])
        
        if not sprinklers:
            self.violations.append({
                'type': 'no_sprinkler_system',
                'severity': 'critical',
                'message': 'لا يوجد نظام رشاشات - الكود السعودي يتطلب نظام حماية مناسب',
                'standard': 'SBC 801'
            })
            return
        
        # فحص الحد الأدنى للتدفق
        building_type = self._detect_building_type()
        min_flow = SaudiCode.get_min_sprinkler_flow(building_type)
        
        # هنا يمكن إضافة فحوصات أكثر تفصيلاً
        self.warnings.append({
            'type': 'flow_requirement',
            'message': f'الحد الأدنى للتدفق المطلوب: {min_flow} GPM لنوع المبنى: {building_type}',
            'standard': 'SBC 801'
        })
    
    def check_water_storage_duration(self):
        """فحص مدة تخزين المياه"""
        tanks = self.entities.get('tanks', [])
        
        if not tanks:
            self.violations.append({
                'type': 'no_water_storage',
                'severity': 'critical',
                'message': f'لا يوجد خزان مياه - الكود السعودي يتطلب {SaudiCode.MIN_WATER_STORAGE} دقيقة تخزين على الأقل',
                'standard': 'SBC 801'
            })
            return
        
        # فحص السعة الكلية
        total_volume = sum(tank.get('volume', 0) for tank in tanks)
        
        if total_volume < 30:  # 30 متر مكعب كحد أدنى تقريبي
            self.violations.append({
                'type': 'insufficient_storage',
                'severity': 'high',
                'message': f'سعة التخزين غير كافية: {total_volume:.1f} متر مكعب',
                'standard': 'SBC 801'
            })
    
    def check_temperature_considerations(self):
        """فحص اعتبارات درجات الحرارة"""
        # في المملكة، درجات الحرارة العالية تؤثر على:
        # - ضغط النظام
        # - نوع المواد المستخدمة
        # - متطلبات العزل
        
        self.warnings.append({
            'type': 'temperature_note',
            'message': 'يجب مراعاة درجات الحرارة العالية في المملكة - تأكد من استخدام مواد مناسبة',
            'standard': 'SBC 801'
        })
    
    def check_local_amendments(self):
        """فحص المتطلبات المحلية الإضافية"""
        # متطلبات الدفاع المدني السعودي
        sprinklers = self.entities.get('sprinklers', [])
        pumps = self.entities.get('pumps', [])
        
        if sprinklers and not pumps:
            self.violations.append({
                'type': 'pump_requirement',
                'severity': 'high',
                'message': 'وجود رشاشات بدون مضخة - الدفاع المدني يتطلب مضخة حريق معتمدة',
                'standard': 'Saudi Civil Defense'
            })
        
        # فحص وجود خزان احتياطي
        tanks = self.entities.get('tanks', [])
        if len(tanks) < 2 and tanks:
            self.warnings.append({
                'type': 'single_tank',
                'message': 'يفضل وجود خزان احتياطي إضافي حسب متطلبات الدفاع المدني',
                'standard': 'Saudi Civil Defense'
            })
    
    def _detect_building_type(self) -> str:
        """محاولة تحديد نوع المبنى من العناصر"""
        # يمكن تحسين هذا لاحقاً بالذكاء الاصطناعي
        rooms = self.entities.get('rooms', [])
        
        if len(rooms) > 50:
            return 'high_rise'
        elif len(rooms) > 20:
            return 'commercial'
        elif len(rooms) > 5:
            return 'residential'
        else:
            return 'residential'