# src/nfpa_validator.py
"""
التحقق من التصميم مقابل معايير NFPA 13
"""

import math
from typing import List, Dict, Any, Tuple
from utils.constants import NFPA13


class NFPAValidator:
    """مدقق معايير NFPA 13"""
    
    def __init__(self, entities: Dict[str, List[Dict]]):
        self.entities = entities
        self.violations = []
        self.warnings = []
    
    def validate_all(self) -> Dict[str, List[Dict]]:
        """تشغيل جميع الفحوصات"""
        self.check_sprinkler_spacing()
        self.check_wall_distance()
        self.check_coverage_area()
        self.check_pipe_sizes()
        self.check_pump_presence()
        self.check_water_supply()
        
        return {
            'violations': self.violations,
            'warnings': self.warnings
        }
    
    def check_sprinkler_spacing(self):
            """فحص التباعد بين الرشاشات المتجاورة فقط"""
            sprinklers = self.entities.get('sprinklers', [])
            hazard_type = self._determine_hazard_type()
            max_spacing = NFPA13.MAX_SPACING.get(hazard_type, 4.6)
            
            # تجميع الرشاشات حسب المنطقة (Z)
            zones = {}
            for i, sprinkler in enumerate(sprinklers):
                z = round(sprinkler['position'][2], 1)  # تجميع حسب الارتفاع
                if z not in zones:
                    zones[z] = []
                zones[z].append((i, sprinkler))
            
            # فحص التباعد داخل كل منطقة فقط
            for zone, zone_sprinklers in zones.items():
                for i in range(len(zone_sprinklers)):
                    for j in range(i + 1, len(zone_sprinklers)):
                        idx1, sprinkler1 = zone_sprinklers[i]
                        idx2, sprinkler2 = zone_sprinklers[j]
                        
                        distance = self._calculate_distance(
                            sprinkler1['position'],
                            sprinkler2['position']
                        )
                        
                        # فقط إذا كانا قريبين نسبياً (أقل من ضعف الحد الأقصى)
                        if distance <= max_spacing * 3:
                            if distance > max_spacing:
                                self.violations.append({
                                    'type': 'spacing_violation',
                                    'severity': 'medium',
                                    'message': f'التباعد بين الرشاشات يتجاوز الحد الأقصى: {distance:.2f} متر',
                                    'sprinklers': [idx1, idx2],
                                    'distance': distance,
                                    'max_allowed': max_spacing,
                                    'standard': 'NFPA 13'
                                })
                                break  # يكفي مخالفة واحدة لكل رشاش
    
    def check_wall_distance(self):
        """فحص المسافة من الجدران"""
        sprinklers = self.entities.get('sprinklers', [])
        walls = self.entities.get('walls', [])
        
        if not walls:
            self.warnings.append({
                'type': 'no_walls',
                'message': 'لم يتم العثور على جدران في الرسم - تم تخطي فحص المسافة من الجدران'
            })
            return
        
        for sprinkler in sprinklers:
            min_distance = self._calculate_min_wall_distance(sprinkler['position'], walls)
            
            if min_distance > NFPA13.MAX_WALL_DISTANCE:
                self.violations.append({
                    'type': 'wall_distance_violation',
                    'severity': 'medium',
                    'message': f'المسافة من الجدار تتجاوز الحد الأقصى: {min_distance:.2f} متر',
                    'position': sprinkler['position'],
                    'standard': 'NFPA 13'
                })
    
    def check_coverage_area(self):
        """فحص منطقة التغطية لكل رشاش"""
        sprinklers = self.entities.get('sprinklers', [])
        rooms = self.entities.get('rooms', [])
        hazard_type = self._determine_hazard_type()
        max_coverage = NFPA13.MAX_COVERAGE.get(hazard_type, 12.1)
        
        if rooms and sprinklers:
            for room in rooms:
                room_area = room['area']
                sprinklers_in_room = self._count_sprinklers_in_polygon(
                    sprinklers,
                    room['points']
                )
                
                if sprinklers_in_room > 0:
                    coverage_per_sprinkler = room_area / sprinklers_in_room
                    
                    if coverage_per_sprinkler > max_coverage:
                        self.violations.append({
                            'type': 'coverage_violation',
                            'severity': 'high',
                            'message': f'مساحة التغطية لكل رشاش تتجاوز الحد: {coverage_per_sprinkler:.2f} متر مربع',
                            'area': room_area,
                            'sprinkler_count': sprinklers_in_room,
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
                    'message': f'قطر الماسورة غير مقبول: {diameter} مم (الحد الأدنى 25 مم)',
                    'standard': 'NFPA 13'
                })
            elif diameter not in NFPA13.PIPE_DIAMETERS:
                self.warnings.append({
                    'type': 'non_standard_pipe',
                    'message': f'قطر الماسورة غير قياسي: {diameter} مم',
                    'standard': 'NFPA 13'
                })
    
    def check_pump_presence(self):
        """فحص وجود مضخة الحريق"""
        pumps = self.entities.get('pumps', [])
        
        if not pumps:
            self.violations.append({
                'type': 'no_fire_pump',
                'severity': 'critical',
                'message': 'لم يتم العثور على مضخة حريق في الرسم',
                'standard': 'NFPA 20'
            })
    
    def check_water_supply(self):
        """فحص مصدر المياه"""
        tanks = self.entities.get('tanks', [])
        
        if tanks:
            total_volume = sum(tank['volume'] for tank in tanks)
            min_volume = 30  # متر مكعب (تقريبي)
            
            if total_volume < min_volume:
                self.violations.append({
                    'type': 'insufficient_water_supply',
                    'severity': 'high',
                    'message': f'سعة الخزان غير كافية: {total_volume:.1f} متر مكعب',
                    'standard': 'NFPA 13'
                })
        else:
            self.warnings.append({
                'type': 'no_water_tank',
                'message': 'لم يتم العثور على خزان مياه - قد يكون مصدر المياه خارجي'
            })
    
    def _determine_hazard_type(self) -> str:
        """تحديد نوع المخاطر من خصائص الرسم"""
        sprinklers = self.entities.get('sprinklers', [])
        
        # إذا كان هناك أنظمة غاز FM-200، فالمخاطر أعلى
        gas_systems = self.entities.get('gas_systems', [])
        if gas_systems:
            return 'extra_hazard'
        
        # فحص معامل K للرشاشات
        if sprinklers:
            k_factors = [s.get('k_factor', 5.6) for s in sprinklers]
            avg_k = sum(k_factors) / len(k_factors)
            
            if avg_k >= 11.2:
                return 'extra_hazard'
            elif avg_k >= 8.0:
                return 'ordinary_hazard'
        
        return 'ordinary_hazard'
    
    def _calculate_distance(self, point1: Tuple[float, float, float], 
                           point2: Tuple[float, float, float]) -> float:
        """حساب المسافة بين نقطتين"""
        return math.sqrt(
            (point2[0] - point1[0])**2 + 
            (point2[1] - point1[1])**2 + 
            (point2[2] - point1[2])**2
        )
    
    def _calculate_min_wall_distance(self, point: Tuple[float, float, float], 
                                    walls: List[Dict]) -> float:
        """حساب أقرب مسافة إلى جدار"""
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
    
    def _count_sprinklers_in_polygon(self, sprinklers: List[Dict], 
                                    polygon_points: List[Tuple[float, float]]) -> int:
        """عد الرشاشات داخل مضلع (غرفة)"""
        from shapely.geometry import Point, Polygon
        
        polygon = Polygon(polygon_points)
        count = 0
        
        for sprinkler in sprinklers:
            point = Point(sprinkler['position'][0], sprinkler['position'][1])
            if polygon.contains(point):
                count += 1
        
        return count