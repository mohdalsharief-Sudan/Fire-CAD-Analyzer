# src/gas_interface.py
"""
واجهة تفاعلية لحساب أنظمة الإطفاء بالغاز
"""

import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(__file__))

from gas_calculator import GasSuppressionCalculator


class GasInterface:
    """واجهة تفاعلية لنظام الإطفاء بالغاز"""
    
    def __init__(self):
        self.calc = GasSuppressionCalculator()
    
    def run(self):
        """تشغيل الواجهة التفاعلية"""
        self._print_header()
        
        while True:
            print("\n" + "=" * 60)
            print("🧯 حاسبة أنظمة الإطفاء بالغاز")
            print("=" * 60)
            print("1. حساب نظام جديد")
            print("2. حساب غرفة من مخطط CAD (المساحة + الارتفاع)")
            print("3. خروج")
            print("-" * 60)
            
            choice = input("اختر (1-3): ").strip()
            
            if choice == '1':
                self._calculate_manual()
            elif choice == '2':
                self._calculate_from_cad()
            elif choice == '3':
                print("👋 وداعاً!")
                break
            else:
                print("❌ اختيار غير صحيح!")
    
    def _print_header(self):
        """طباعة العنوان"""
        print("=" * 60)
        print("🧯 نظام حساب الإطفاء بالغاز")
        print("   FM-200 | Novec 1230 | CO2")
        print("=" * 60)
    
    def _select_gas_type(self) -> str:
        """اختيار نوع الغاز"""
        print("\nاختر نوع الغاز:")
        print("1. FM-200 (الأكثر شيوعاً)")
        print("2. Novec 1230 (صديق للبيئة)")
        print("3. CO2 (اقتصادي)")
        
        while True:
            choice = input("اختر (1-3): ").strip()
            if choice == '1':
                return 'FM-200'
            elif choice == '2':
                return 'Novec 1230'
            elif choice == '3':
                return 'CO2'
            else:
                print("❌ اختيار غير صحيح!")
    
    def _select_protection_area(self) -> str:
        """اختيار منطقة الحماية"""
        print("\nاختر منطقة الحماية:")
        print("1. إغراق كامل للغرفة")
        print("2. تحت الأرضية المرتفعة")
        print("3. فوق السقف المستعار")
        print("4. مشترك (أرضية + سقف + غرفة)")
        
        while True:
            choice = input("اختر (1-4): ").strip()
            if choice == '1':
                return 'total_flooding'
            elif choice == '2':
                return 'raised_floor'
            elif choice == '3':
                return 'ceiling_void'
            elif choice == '4':
                return 'combined'
            else:
                print("❌ اختيار غير صحيح!")
    
    def _get_room_dimensions(self) -> Dict[str, float]:
        """إدخال أبعاد الغرفة"""
        print("\nأدخل أبعاد الغرفة:")
        print("(يمكنك الإدخال: 4*4*3 أو كل بعد منفصل)")
        
        # محاولة قراءة سريعة
        quick = input("الأبعاد (طول*عرض*ارتفاع): ").strip()
        
        if '*' in quick:
            parts = quick.split('*')
            if len(parts) == 3:
                try:
                    length = float(parts[0])
                    width = float(parts[1])
                    height = float(parts[2])
                    if all(x > 0 for x in [length, width, height]):
                        return {'length': length, 'width': width, 'height': height}
                except ValueError:
                    pass
        
        # إدخال منفصل
        while True:
            try:
                length = float(input("الطول (متر): "))
                if length > 0:
                    break
            except ValueError:
                print("خطأ!")
        
        while True:
            try:
                width = float(input("العرض (متر): "))
                if width > 0:
                    break
            except ValueError:
                print("خطأ!")
        
        while True:
            try:
                height = float(input("الارتفاع (متر): "))
                if height > 0:
                    break
            except ValueError:
                print("خطأ!")
        
        return {'length': length, 'width': width, 'height': height}
    
    def _get_temperature(self) -> float:
        """إدخال درجة الحرارة"""
        while True:
            try:
                temp = input("درجة الحرارة (مئوية) [افتراضي 21]: ").strip()
                if temp == '':
                    return 21.0
                temp = float(temp)
                if -10 <= temp <= 60:
                    return temp
                print("❌ درجة حرارة غير منطقية!")
            except ValueError:
                print("❌ أدخل رقماً صحيحاً!")
    
    def _get_altitude(self) -> float:
        """إدخال الارتفاع عن سطح البحر"""
        while True:
            try:
                alt = input("الارتفاع عن سطح البحر (متر) [افتراضي 650]: ").strip()
                if alt == '':
                    return 650.0
                alt = float(alt)
                if 0 <= alt <= 3000:
                    return alt
                print("❌ ارتفاع غير منطقي!")
            except ValueError:
                print("❌ أدخل رقماً صحيحاً!")
    
    def _get_safety_factor(self) -> float:
        """إدخال عامل الأمان"""
        while True:
            try:
                factor = input("عامل الأمان [افتراضي 1.1]: ").strip()
                if factor == '':
                    return 1.1
                factor = float(factor)
                if 1.0 <= factor <= 1.5:
                    return factor
                print("❌ عامل أمان غير منطقي (1.0 - 1.5)!")
            except ValueError:
                print("❌ أدخل رقماً صحيحاً!")
    
    def _calculate_manual(self):
        """حساب يدوي كامل"""
        gas_type = self._select_gas_type()
        protection_area = self._select_protection_area()
        dimensions = self._get_room_dimensions()
        temperature = self._get_temperature()
        altitude = self._get_altitude()
        safety_factor = self._get_safety_factor()
        
        # حساب الحجم
        room_volume = self.calc.calculate_room_volume(
            dimensions['length'],
            dimensions['width'],
            dimensions['height']
        )
        
        print(f"\n📐 حجم الغرفة: {room_volume:.2f} م³")
        
        # الحساب
        results = self.calc.calculate_agent_quantity(
            gas_type=gas_type,
            room_volume=room_volume,
            protection_area=protection_area,
            temperature_c=temperature,
            altitude_m=altitude,
            safety_factor=safety_factor
        )
        
        # طباعة النتائج
        self.calc.print_calculation(results)
        
        # حفظ؟
        self._ask_save(results)
    
    def _calculate_from_cad(self):
        """حساب من مخطط CAD (المساحة + الارتفاع اليدوي)"""
        print("\n📐 حساب من مخطط CAD")
        print("(المساحة من المخطط + الارتفاع يدوي)")
        
        gas_type = self._select_gas_type()
        protection_area = self._select_protection_area()
        
        # إدخال المساحة
        while True:
            try:
                area = float(input("\nمساحة الغرفة من المخطط (متر مربع): "))
                if area > 0:
                    break
                print("❌ يجب أن يكون أكبر من صفر!")
            except ValueError:
                print("❌ أدخل رقماً صحيحاً!")
        
        # إدخال الارتفاع
        while True:
            try:
                height = float(input("ارتفاع الغرفة (متر): "))
                if height > 0:
                    break
                print("❌ يجب أن يكون أكبر من صفر!")
            except ValueError:
                print("❌ أدخل رقماً صحيحاً!")
        
        temperature = self._get_temperature()
        altitude = self._get_altitude()
        safety_factor = self._get_safety_factor()
        
        # حساب الحجم
        room_volume = area * height
        print(f"\n📐 حجم الغرفة: {room_volume:.2f} م³")
        
        # الحساب
        results = self.calc.calculate_agent_quantity(
            gas_type=gas_type,
            room_volume=room_volume,
            protection_area=protection_area,
            temperature_c=temperature,
            altitude_m=altitude,
            safety_factor=safety_factor
        )
        
        # طباعة النتائج
        self.calc.print_calculation(results)
        
        # حفظ؟
        self._ask_save(results)
    
    def _ask_save(self, results: Dict[str, Any]):
        """سؤال المستخدم عن الحفظ"""
        if not results:
            return
        
        print("\n" + "-" * 60)
        save = input("هل تريد حفظ النتيجة؟ (y/n): ").strip().lower()
        
        if save == 'y':
            self._save_results(results)
    
    def _save_results(self, results: Dict[str, Any]):
        """حفظ النتائج إلى ملف"""
        import json
        from datetime import datetime
        
        reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = f"gas_calculation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ تم الحفظ: {filepath}")


def main():
    """الدالة الرئيسية"""
    interface = GasInterface()
    interface.run()


if __name__ == "__main__":
    main()