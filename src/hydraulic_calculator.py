# src/hydraulic_calculator.py
"""
الحسابات الهيدروليكية لأنظمة مكافحة الحريق
وفقاً لمعايير NFPA 13 و NFPA 14
"""

import math
import logging

logger = logging.getLogger(__name__)


class HydraulicCalculator:
    """حاسبة هيدروليكية لأنظمة الرشاشات والخراطيم"""
    
    def __init__(self):
        self.GPM_TO_LPM = 3.78541
    
    # ========== التدفقات ==========
    
    def calculate_sprinkler_flow(self, density_mm_per_min: float, area_m2: float) -> float:
        """
        حساب تدفق الرشاشات
        Q = Density × Area
        
        Args:
            density_mm_per_min: الكثافة (مم/دقيقة)
            area_m2: المساحة التصميمية (م²)
            
        Returns:
            التدفق (L/min)
        """
        return density_mm_per_min * area_m2
    
    def calculate_total_flow(self, 
                              sprinkler_flow: float,
                              landing_valves: int = 0,
                              hydrants: int = 0,
                              hose_cabinets: int = 0) -> dict:
        """
        حساب التدفق الكلي مع الحدود القصوى حسب NFPA 14
        
        Args:
            sprinkler_flow: تدفق الرشاشات (L/min)
            landing_valves: عدد الـ Landing Valves (الحد الأقصى 2)
            hydrants: عدد الهيدرانت (الحد الأقصى 1)
            hose_cabinets: عدد صناديق الحريق (الحد الأقصى 2)
            
        Returns:
            dict: نتائج التدفقات
        """
        # الحدود القصوى حسب NFPA 14
        max_hose_cabinets = min(max(hose_cabinets, 0), 2)
        max_landing_valves = min(max(landing_valves, 0), 2)
        max_hydrants = min(max(hydrants, 0), 1)
        
        # التدفقات
        hose_cabinet_flow = max_hose_cabinets * 50 * self.GPM_TO_LPM
        landing_flow = max_landing_valves * 250 * self.GPM_TO_LPM
        hydrant_flow = max_hydrants * 500 * self.GPM_TO_LPM
        
        total_flow = sprinkler_flow + hose_cabinet_flow + landing_flow + hydrant_flow
        
        return {
            'sprinkler_flow_lpm': round(sprinkler_flow, 2),
            'hose_cabinet_flow_lpm': round(hose_cabinet_flow, 2),
            'hose_cabinets_designed': max_hose_cabinets,
            'landing_flow_lpm': round(landing_flow, 2),
            'landing_valves_designed': max_landing_valves,
            'hydrant_flow_lpm': round(hydrant_flow, 2),
            'hydrants_designed': max_hydrants,
            'total_flow_lpm': round(total_flow, 2),
            'total_flow_gpm': round(total_flow / self.GPM_TO_LPM, 2),
        }
    
    # ========== فقدان الضغط ==========
    
    def hazen_williams_pressure_loss(self, 
                                      flow_lpm: float,
                                      pipe_diameter_mm: float,
                                      pipe_length_m: float,
                                      c_factor: float = 120) -> float:
        """
        معادلة Hazen-Williams لفقدان الضغط
        
        Args:
            flow_lpm: التدفق (لتر/دقيقة)
            pipe_diameter_mm: قطر الماسورة (مم)
            pipe_length_m: طول الماسورة (متر)
            c_factor: معامل Hazen-Williams (120 للفولاذ الأسود)
            
        Returns:
            فقدان الضغط (bar)
        """
        if flow_lpm <= 0 or pipe_diameter_mm <= 0:
            return 0.0
        
        # تحويل الوحدات
        flow_m3s = flow_lpm / 60000  # m³/s
        diameter_m = pipe_diameter_mm / 1000  # m
        
        # معادلة Hazen-Williams
        pressure_loss_pa = (
            (6.05e5 * (flow_m3s ** 1.85)) /
            ((c_factor ** 1.85) * (diameter_m ** 4.87))
        ) * pipe_length_m
        
        # تحويل إلى bar
        pressure_loss_bar = pressure_loss_pa / 100000
        
        return round(pressure_loss_bar, 4)
    
    def calculate_pump_curve(self, 
                              design_flow_lpm: float,
                              design_pressure_bar: float) -> dict:
        """
        حساب نقاط منحنى المضخة حسب NFPA 20
        
        Args:
            design_flow_lpm: التدفق التصميمي (L/min)
            design_pressure_bar: الضغط التصميمي (bar)
            
        Returns:
            dict: نقاط المنحنى
        """
        return {
            'shutoff_pressure_bar': round(design_pressure_bar * 1.20, 2),
            'design_point': {
                'flow_lpm': round(design_flow_lpm, 2),
                'pressure_bar': design_pressure_bar,
            },
            'overload_point': {
                'flow_lpm': round(design_flow_lpm * 1.50, 2),
                'pressure_bar': round(design_pressure_bar * 0.65, 2),
            },
        }
    
    
    # ========== الضغط الارتفاعي ==========
    
    def elevation_pressure(self, height_m: float) -> float:
        """
        الضغط الارتفاعي
        1 متر = 0.0981 bar
        
        Args:
            height_m: الارتفاع (متر)
            
        Returns:
            الضغط (bar)
        """
        return round(height_m * 0.0981, 4)
    
    # ========== الضغط الكلي ==========
    
    def calculate_total_pressure(self,
                                  friction_loss_bar: float,
                                  elevation_height_m: float,
                                  residual_pressure_bar: float = 1.4) -> float:
        """
        الضغط الكلي المطلوب من المضخة
        
        Args:
            friction_loss_bar: فقدان الاحتكاك (bar)
            elevation_height_m: ارتفاع أعلى نقطة (متر)
            residual_pressure_bar: الضغط المتبقي (1.4 bar للرشاشات)
            
        Returns:
            الضغط الكلي (bar)
        """
        elevation = self.elevation_pressure(elevation_height_m)
        total = friction_loss_bar + elevation + residual_pressure_bar
        
        return round(total, 2)
    
    # ========== قدرة المضخة ==========
    
    def calculate_pump_power(self, 
                              flow_lpm: float,
                              pressure_bar: float,
                              efficiency: float = 0.75) -> float:
        """
        قدرة المضخة بالكيلوواط
        
        P = Q × P / (600 × η)
        
        حيث:
        Q = التدفق (L/min)
        P = الضغط (bar)
        η = الكفاءة
        """
        if flow_lpm <= 0 or pressure_bar <= 0:
            return 0.0
        
        power_kw = (flow_lpm * pressure_bar) / (600 * efficiency)
        
        return round(power_kw, 2)
    
    # ========== حجم الخزان ==========
    
    def calculate_tank_volume(self,
                               flow_lpm: float,
                               duration_min: int = 30) -> float:
        """
        حجم خزان المياه
        V = Q × t / 1000
        
        Args:
            flow_lpm: التدفق (لتر/دقيقة)
            duration_min: مدة التشغيل (دقيقة)
            
        Returns:
            الحجم (م³)
        """
        volume_m3 = (flow_lpm * duration_min) / 1000
        return round(volume_m3, 2)
    
    # ========== اختيار قطر الماسورة ==========
    
    def select_pipe_diameter(self, flow_lpm: float, max_velocity: float = 3.0) -> int:
        """
        اختيار قطر الماسورة المناسب
        
        Args:
            flow_lpm: التدفق (لتر/دقيقة)
            max_velocity: السرعة القصوى (م/ث)
            
        Returns:
            القطر (مم)
        """
        if flow_lpm <= 0:
            return 25
        
        flow_m3s = flow_lpm / 60000
        area_m2 = flow_m3s / max_velocity
        diameter_m = math.sqrt(4 * area_m2 / math.pi)
        diameter_mm = diameter_m * 1000
        
        # التقريب لأقرب قطر قياسي
        standard_diameters = [25, 32, 40, 50, 65, 80, 100, 150, 200, 250, 300]
        
        for d in standard_diameters:
            if d >= diameter_mm:
                return d
        
        return 300
    
    # ========== حساب شامل ==========
    
    def calculate_complete_system(self,
                                   density: float,
                                   design_area: float,
                                   landing_valves: int = 0,
                                   hydrants: int = 0,
                                   hose_cabinets: int = 0,
                                   pipe_length_m: float = 100,
                                   elevation_m: float = 10,
                                   duration_min: int = 30) -> dict:
        """
        حساب شامل للنظام
        
        Args:
            density: الكثافة (مم/دقيقة)
            design_area: المساحة التصميمية (م²)
            landing_valves: عدد Landing Valves
            hydrants: عدد الهيدرانت
            hose_cabinets: عدد صناديق الحريق
            pipe_length_m: طول الماسورة الرئيسية (متر)
            elevation_m: ارتفاع أعلى نقطة (متر)
            duration_min: مدة التشغيل (دقيقة)
        """
        
        # 1. تدفق الرشاشات
        sprinkler_flow = self.calculate_sprinkler_flow(density, design_area)
        
        # 2. التدفق الكلي (مع الحدود القصوى)
        flow_results = self.calculate_total_flow(
            sprinkler_flow, landing_valves, hydrants, hose_cabinets
        )
        
        # 3. قطر الماسورة الرئيسية
        main_pipe_diameter = self.select_pipe_diameter(flow_results['total_flow_lpm'])
        
        # 4. فقدان الضغط
        friction_loss = self.hazen_williams_pressure_loss(
            flow_results['total_flow_lpm'],
            main_pipe_diameter,
            pipe_length_m
        )
        
        # 5. الضغط الكلي
        total_pressure = self.calculate_total_pressure(
            friction_loss, elevation_m
        )
        
        # 6. قدرة المضخة
        pump_power = self.calculate_pump_power(
            flow_results['total_flow_lpm'],
            total_pressure
        )
        
        # 7. حجم الخزان
        tank_volume = self.calculate_tank_volume(
            flow_results['total_flow_lpm'],
            duration_min
        )
        
              
              
        # 8. منحنى المضخة
        pump_curve = self.calculate_pump_curve(
            flow_results['total_flow_lpm'],
            total_pressure
        )
        
        return {
            'flows': flow_results,
            'main_pipe_diameter_mm': main_pipe_diameter,
            'friction_loss_bar': friction_loss,
            'elevation_loss_bar': self.elevation_pressure(elevation_m),
            'total_pressure_bar': total_pressure,
            'pump_power_kw': pump_power,
            'tank_volume_m3': tank_volume,
            'pump_curve': pump_curve,  # ← جديد
        }
    
    # ========== طباعة النتائج ==========
    
    def print_results(self, results: dict):
        """طباعة النتائج"""
        if not results:
            return
        
        flows = results['flows']
        
        print("\n" + "=" * 60)
        print("💧 الحسابات الهيدروليكية")
        print("=" * 60)
        
        print(f"\n📊 التدفقات:")
        print(f"  • الرشاشات: {flows['sprinkler_flow_lpm']:.2f} L/min ({flows['sprinkler_flow_lpm']/self.GPM_TO_LPM:.2f} GPM)")
        print(f"  • صناديق الحريق ({flows['hose_cabinets_designed']} من أصل الحد الأقصى 2): {flows['hose_cabinet_flow_lpm']:.2f} L/min")
        print(f"  • Landing Valves ({flows['landing_valves_designed']} من أصل الحد الأقصى 2): {flows['landing_flow_lpm']:.2f} L/min")
        print(f"  • الهيدرانت ({flows['hydrants_designed']} من أصل الحد الأقصى 1): {flows['hydrant_flow_lpm']:.2f} L/min")
        print(f"  • التدفق الكلي: {flows['total_flow_lpm']:.2f} L/min ({flows['total_flow_gpm']:.2f} GPM)")
        
        print(f"\n📐 الماسورة الرئيسية: {results['main_pipe_diameter_mm']} مم")
        
        print(f"\n📊 الضغوط:")
        print(f"  • فقدان الاحتكاك: {results['friction_loss_bar']} bar")
        print(f"  • الضغط الارتفاعي: {results['elevation_loss_bar']} bar")
        print(f"  • الضغط الكلي المطلوب: {results['total_pressure_bar']} bar")
        
        # منحنى المضخة هنا (بعد الضغوط)
        pump_curve = results.get('pump_curve', {})
        if pump_curve:
            print(f"\n📈 منحنى المضخة (NFPA 20):")
            print(f"  • عند الإغلاق (0 GPM): {pump_curve['shutoff_pressure_bar']} bar")
            print(f"  • النقطة التصميمية ({pump_curve['design_point']['flow_lpm']} L/min): {pump_curve['design_point']['pressure_bar']} bar")
            print(f"  • عند 150% ({pump_curve['overload_point']['flow_lpm']} L/min): {pump_curve['overload_point']['pressure_bar']} bar")
        
        print(f"\n🔧 قدرة المضخة: {results['pump_power_kw']} كيلوواط")
        print(f"\n💧 حجم الخزان: {results['tank_volume_m3']} م³")
        print("=" * 60)