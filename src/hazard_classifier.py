# src/hazard_classifier.py
"""
تصنيف المخاطر لأنظمة الرشاشات
"""

import logging

logger = logging.getLogger(__name__)


class HazardClassifier:
    """تصنيف المخاطر"""
    
    def __init__(self, entities=None):
        self.entities = entities or {}
        self.hazard_type = None
        self.classification_reason = None
    
    def classify_auto(self) -> str:
        """تصنيف تلقائي"""
        reasons = []
        
        gas_systems = self.entities.get('gas_systems', [])
        if len(gas_systems) > 0:
            reasons.append(f"وجود {len(gas_systems)} نظام إطفاء بالغاز")
            self.hazard_type = 'extra_hazard_g2'
            self.classification_reason = "، ".join(reasons)
            return self.hazard_type
        
        sprinklers = self.entities.get('sprinklers', [])
        if sprinklers:
            k_factors = [s.get('k_factor', 5.6) for s in sprinklers if s.get('k_factor', 0) > 0]
            if k_factors:
                avg_k = sum(k_factors) / len(k_factors)
                if avg_k >= 11.2:
                    reasons.append(f"متوسط معامل K = {avg_k:.1f}")
                    self.hazard_type = 'extra_hazard_g1'
                elif avg_k >= 8.0:
                    reasons.append(f"متوسط معامل K = {avg_k:.1f}")
                    self.hazard_type = 'ordinary_hazard_g2'
                else:
                    reasons.append(f"متوسط معامل K = {avg_k:.1f}")
                    self.hazard_type = 'ordinary_hazard_g1'
            else:
                reasons.append("معامل K غير محدد")
                self.hazard_type = 'ordinary_hazard_g1'
        else:
            reasons.append("لا توجد رشاشات")
            self.hazard_type = 'light_hazard'
        
        self.classification_reason = "، ".join(reasons)
        return self.hazard_type
    
    def classify_manual(self, hazard_type: str) -> str:
        """تصنيف يدوي"""
        valid_types = [
            'light_hazard',
            'ordinary_hazard_g1',
            'ordinary_hazard_g2',
            'extra_hazard_g1',
            'extra_hazard_g2',
        ]
        
        hazard_type = hazard_type.lower().strip()
        
        aliases = {
            'light': 'light_hazard',
            'lh': 'light_hazard',
            'oh1': 'ordinary_hazard_g1',
            'ordinary1': 'ordinary_hazard_g1',
            'oh2': 'ordinary_hazard_g2',
            'ordinary2': 'ordinary_hazard_g2',
            'eh1': 'extra_hazard_g1',
            'extra1': 'extra_hazard_g1',
            'eh2': 'extra_hazard_g2',
            'extra2': 'extra_hazard_g2',
        }
        
        if hazard_type in aliases:
            hazard_type = aliases[hazard_type]
        
        if hazard_type in valid_types:
            self.hazard_type = hazard_type
            self.classification_reason = "تصنيف يدوي من المستخدم"
        else:
            logger.warning(f"تصنيف غير معروف: {hazard_type} - استخدام OH2")
            self.hazard_type = 'ordinary_hazard_g2'
            self.classification_reason = f"تصنيف {hazard_type} غير معروف - استخدام OH2"
        
        return self.hazard_type
    
    def get_info(self):
        """معلومات التصنيف"""
        from utils.constants import NFPA13
        
        return {
            'hazard_type': self.hazard_type,
            'reason': self.classification_reason,
            'max_coverage': NFPA13.MAX_COVERAGE.get(self.hazard_type, 12.1),
            'max_spacing': NFPA13.MAX_SPACING.get(self.hazard_type, 4.6),
            'density': NFPA13.DENSITY.get(self.hazard_type, 6.0),
        }
    
    def get_arabic_name(self) -> str:
        """الاسم العربي"""
        names = {
            'light_hazard': 'خفيف الخطورة (Light Hazard)',
            'ordinary_hazard_g1': 'عادي الخطورة - مجموعة 1 (OH1)',
            'ordinary_hazard_g2': 'عادي الخطورة - مجموعة 2 (OH2)',
            'extra_hazard_g1': 'شديد الخطورة - مجموعة 1 (EH1)',
            'extra_hazard_g2': 'شديد الخطورة - مجموعة 2 (EH2)',
        }
        return names.get(self.hazard_type, self.hazard_type)