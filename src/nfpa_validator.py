# src/nfpa_validator.py
"""
التحقق من التصميم مقابل معايير NFPA 13
"""

import math
import logging
from typing import List, Dict, Any, Tuple
from utils.constants import NFPA13
from hazard_classifier import HazardClassifier

logger = logging.getLogger(__name__)


class NFPAValidator:
    """مدقق معايير NFPA 13"""
    
    def __init__(self, entities, hazard_type=None):
        self.entities = entities
        self.violations = []
        self.warnings = []
        
        # تصنيف المخاطر
        self.classifier = HazardClassifier(entities)
        
        if hazard_type:
            self.hazard_type = self.classifier.classify_manual(hazard_type)
        else:
            self.hazard_type = self.classifier.classify_auto()
        
        logger.info(f"تصنيف المخاطر: {self.hazard_type}")
    
    def validate_all(self):
        """تشغيل جميع الفحوصات"""
        self.check_coverage_area()
        self.check_wall_distance()
        self.check_pipe_sizes()
        self.check_pump_presence()
        self.check_water_supply()
        
        return {
            'violations': self.violations,
            'warnings': self.warnings,
            'hazard_type': self.hazard_type,
            'hazard_info': self.classifier.get_info(),
        }
    
    def check_coverage_area(self):
        """فحص مساحة التغطية لكل رشاش"""
        sprinklers = self.entities.get('sprinklers', [])
        max_coverage = NFPA13.MAX_COVERAGE.get(self.hazard_type, 12.1)
        
        # تجميع حسب Z
        zones = {}
        for sprinkler in sprinklers:
            z = round(sprinkler['position'][2], 1)
            if z not in zones:
                zones[z] = []
            zones[z].append(sprinkler)
        
        for zone, zone_sprinklers in zones.items():
            for sprinkler in zone_sprinklers:
                coverage = self._calculate_sprinkler_coverage(sprinkler, zone_sprinklers)
                
                if coverage > max_coverage:
                    self.violations.append({
                        'type': 'coverage_violation',
                        'severity': 'high',
                        'message': f'مساحة تغطية الرشاش تتجاوز الحد: {coverage:.2f} م² (الحد: {max_coverage} م²)',
                        'position': sprinkler['position'],
                        'coverage': coverage,
                        'max_allowed': max_coverage,
                        'standard': 'NFPA 13'
                    })
    
    def _calculate_sprinkler_coverage(self, sprinkler, all_sprinklers):
        """حساب مساحة التغطية الفعلية"""
        distances = []
        
        for other in all_sprinklers:
            if other is sprinkler:
                continue
            d = self._calculate_distance(sprinkler['position'], other['position'])
            if d < 10:
                distances.append(d)
        
        if not distances:
            return 0
        
        distances.sort()
        nearest = distances[:4]
        
        if len(nearest) < 4:
            nearest = nearest + [nearest[-1]] * (4 - len(nearest))
        
        avg_distance = sum(nearest) / len(nearest)
        coverage = avg_distance ** 2
        
        return coverage
    
    def check_wall_distance(self):
        """فحص المسافة من الجدران"""
        sprinklers = self.entities.get('sprinklers', [])
        walls = self.entities.get('walls', [])
        
        if not walls:
            self.warnings.append({
                'type': 'no_walls',
                'message': 'لم يتم العثور على جدران - تم تخطي فحص المسافة'
            })
            return
        
        for sprinkler in sprinklers:
            min_distance = self._calculate_min_wall_distance(sprinkler['position'], walls)
            if min_distance > NFPA13.MAX_WALL_DISTANCE:
                self.violations.append({
                    'type': 'wall_distance_violation',
                    'severity': 'medium',
                    'message': f'المسافة من الجدار: {min_distance:.2f} متر',
                    'standard': 'NFPA 13'
                })
    
    def check_pipe_sizes(self):
        """فحص أقطار المواسير"""
        pipes = self.entities.get('pipes', [])
        
        for pipe in pipes:
            diameter = pipe.get('diameter', 0)
            if diameter < 25:
                self.violations.append({
                    'type': 'pipe_size_violation',
                    'severity': 'high',
                    'message': f'قطر الماسورة غير مقبول: {diameter} مم',
                    'standard': 'NFPA 13'
                })
    
    def check_pump_presence(self):
        """فحص وجود مضخة"""
        pumps = self.entities.get('pumps', [])
        if not pumps:
            self.violations.append({
                'type': 'no_fire_pump',
                'severity': 'critical',
                'message': 'لم يتم العثور على مضخة حريق',
                'standard': 'NFPA 20'
            })
    
    def check_water_supply(self):
        """فحص مصدر المياه"""
        tanks = self.entities.get('tanks', [])
        if not tanks:
            self.warnings.append({
                'type': 'no_water_tank',
                'message': 'لم يتم العثور على خزان مياه'
            })
    
    def _determine_hazard_type(self):
        """محدد نوع المخاطر"""
        return self.hazard_type
    
    def _calculate_distance(self, point1, point2):
        """حساب المسافة"""
        return math.sqrt(
            (point2[0] - point1[0])**2 +
            (point2[1] - point1[1])**2 +
            (point2[2] - point1[2])**2
        )
    
    def _calculate_min_wall_distance(self, point, walls):
        """حساب أقرب مسافة لجدار"""
        from shapely.geometry import Point, LineString
        
        p = Point(point[0], point[1])
        min_distance = float('inf')
        
        for wall in walls:
            if 'start' in wall and 'end' in wall:
                line = LineString([
                    (wall['start'][0], wall['start'][1]),
                    (wall['end'][0], wall['end'][1])
                ])
                distance = p.distance(line)
                min_distance = min(min_distance, distance)
        
        return min_distance if min_distance != float('inf') else 0