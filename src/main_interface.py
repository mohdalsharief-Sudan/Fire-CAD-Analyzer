# src/main_interface.py
"""
الواجهة الموحدة لنظام Fire CAD Analyzer
تجمع: تحليل CAD + أنظمة الغاز + الحسابات الهيدروليكية + التكاليف
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from cad_reader import CADReader
from entity_extractor import EntityExtractor
from nfpa_validator import NFPAValidator
from saudi_validator import SaudiCodeValidator
from cost_calculator import CostCalculator
from gas_calculator import GasSuppressionCalculator
from hydraulic_calculator import HydraulicCalculator
from integrated_report import IntegratedReport
from excel_exporter import ExcelExporter
from pricing_exporter import PricingExporter

class MainInterface:
    """الواجهة الموحدة"""
    
    def __init__(self):
        self.integrated_report = IntegratedReport()
        self.gas_calculator = GasSuppressionCalculator()
        self.hydraulic_calculator = HydraulicCalculator()
        self.gas_results = []       # قائمة نتائج الغاز
        self.hydraulic_result = None
        self.cad_result = None
    
    def run(self):
        """تشغيل الواجهة"""
        self._print_banner()
        
        while True:
            print("\n" + "=" * 60)
            print("🏗️ Fire CAD Analyzer - القائمة الرئيسية")
            print("=" * 60)
            print("1. 📁 تحليل ملف CAD (رشاشات + تكاليف)")
            print("2. 🧯 حساب نظام إطفاء بالغاز")
            print("3. 💧 الحسابات الهيدروليكية")
            print("4. 📊 التقرير الموحد النهائي")
            print("5. خروج")
            print("-" * 60)
            
            choice = input("اختر (1-5): ").strip()
            
            if choice == '1':
                self._analyze_cad()
            elif choice == '2':
                self._calculate_gas()
            elif choice == '3':
                self._calculate_hydraulic()
            elif choice == '4':
                self._show_integrated_report()
            elif choice == '5':
                print("👋 وداعاً!")
                break
            else:
                print("❌ اختيار غير صحيح!")
    
    def _print_banner(self):
        """طباعة العنوان"""
        print("=" * 60)
        print("🏗️ Fire CAD Analyzer - نظام متكامل")
        print("   تحليل CAD | أنظمة الغاز | هيدروليكي | تسعير")
        print("=" * 60)
    
    def _analyze_cad(self):
        """تحليل ملف CAD"""
        print("\n📁 تحليل ملف CAD")
        file_path = input("مسار الملف: ").strip().strip('"')
        
        if not os.path.exists(file_path):
            print("❌ الملف غير موجود!")
            return
        
        # تصنيف المخاطر
        print("\nاختر تصنيف المخاطر:")
        print("1. Light Hazard (خفيف)")
        print("2. Ordinary Hazard G1 (عادي 1)")
        print("3. Ordinary Hazard G2 (عادي 2)")
        print("4. Extra Hazard G1 (شديد 1)")
        print("5. Extra Hazard G2 (شديد 2)")
        print("6. تلقائي")
        
        hazard_map = {
            '1': 'light_hazard',
            '2': 'ordinary_hazard_g1',
            '3': 'ordinary_hazard_g2',
            '4': 'extra_hazard_g1',
            '5': 'extra_hazard_g2',
            '6': None,
        }
        
        hazard_choice = input("اختر (1-6): ").strip()
        hazard_type = hazard_map.get(hazard_choice, 'ordinary_hazard_g2')
        
        print("\n⏳ جاري التحليل...")
        
        try:
            # قراءة الملف
            reader = CADReader()
            if not reader.read_file(file_path):
                print("❌ فشل قراءة الملف")
                return
            
            # استخراج العناصر
            extractor = EntityExtractor(reader.modelspace, reader.doc)
            entities = extractor.extract_all()
            
            # فحص NFPA
            nfpa_validator = NFPAValidator(entities, hazard_type)
            nfpa_results = nfpa_validator.validate_all()
            
            # فحص سعودي
            saudi_validator = SaudiCodeValidator(entities)
            saudi_results = saudi_validator.validate_all()
            
            # حساب التكاليف
            cost_calculator = CostCalculator(entities)
            cost_summary = cost_calculator.calculate_all()
            
            # حفظ في التقرير الموحد
            self.cad_result = {
                'entities': entities,
                'nfpa': nfpa_results,
                'saudi': saudi_results,
                'costs': cost_summary,
            }
            
            self.integrated_report.add_cad_costs(cost_summary)
            
            # عرض النتائج
            self._display_cad_results(entities, nfpa_results, saudi_results)
            cost_calculator.print_summary()
            
            # تصدير Excel؟
            self._ask_export_excel(cost_summary, os.path.basename(file_path))
            
            # تصدير إلى Fire-Pricing
            self._ask_export_pricing(cost_summary, entities, os.path.basename(file_path))
            
        except Exception as e:
            print(f"❌ خطأ: {e}")
    
    def _ask_export_pricing(self, cost_summary, entities, project_name):
        """سؤال عن التصدير إلى Fire-Pricing"""
        export = input("\nتصدير إلى Fire-Pricing؟ (y/n): ").strip().lower()
        if export == 'y':
            exporter = PricingExporter()
            path = exporter.export_for_fire_pricing(
                cost_summary, entities, project_name
            )
            print(f"✅ تم التصدير: {path}")
            print("📋 يمكنك الآن استيراد هذا الملف في Fire-Pricing")
    
    def _display_cad_results(self, entities, nfpa_results, saudi_results):
        """عرض نتائج CAD"""
        print("\n📊 نتائج تحليل CAD:")
        print(f"  • الرشاشات: {len(entities.get('sprinklers', []))}")
        print(f"  • المواسير: {len(entities.get('pipes', []))}")
        print(f"  • المضخات: {len(entities.get('pumps', []))}")
        print(f"  • أنظمة الغاز: {len(entities.get('gas_systems', []))}")
        print(f"  • مخالفات NFPA: {len(nfpa_results.get('violations', []))}")
        print(f"  • مخالفات سعودي: {len(saudi_results.get('violations', []))}")
    
    def _ask_export_excel(self, cost_summary, project_name):
        """سؤال عن تصدير Excel"""
        export = input("\nتصدير Excel؟ (y/n): ").strip().lower()
        if export == 'y':
            exporter = ExcelExporter(cost_summary, project_name)
            path = exporter.export()
            print(f"✅ تم الحفظ: {path}")
    
    def _calculate_gas(self):
        """حساب نظام الغاز"""
        print("\n🧯 حساب نظام الغاز")
        
        # نوع الغاز
        print("\nاختر نوع الغاز:")
        print("1. FM-200")
        print("2. Novec 1230")
        print("3. CO2")
        gas_map = {'1': 'FM-200', '2': 'Novec 1230', '3': 'CO2'}
        gas_choice = input("اختر (1-3): ").strip()
        gas_type = gas_map.get(gas_choice, 'FM-200')
        
        # منطقة الحماية
        print("\nاختر منطقة الحماية:")
        print("1. إغراق كامل")
        print("2. تحت الأرضية")
        print("3. فوق السقف المستعار")
        print("4. مشترك")
        area_map = {
            '1': 'total_flooding',
            '2': 'raised_floor',
            '3': 'ceiling_void',
            '4': 'combined',
        }
        area_choice = input("اختر (1-4): ").strip()
        protection_area = area_map.get(area_choice, 'total_flooding')
        
        # الأبعاد
        print("\nأدخل الأبعاد (طول*عرض*ارتفاع):")
        dims = input("الأبعاد: ").strip()
        parts = dims.split('*')
        if len(parts) != 3:
            print("❌ صيغة خاطئة! استخدم: 5*4*3")
            return
        
        try:
            length = float(parts[0])
            width = float(parts[1])
            height = float(parts[2])
        except ValueError:
            print("❌ أرقام غير صحيحة!")
            return
        
        # الحساب
        room_volume = self.gas_calculator.calculate_room_volume(length, width, height)
        
        results = self.gas_calculator.calculate_agent_quantity(
            gas_type=gas_type,
            room_volume=room_volume,
            protection_area=protection_area,
            temperature_c=21,
            altitude_m=650,
            safety_factor=1.1
        )
        
        # حفظ
        self.gas_results.append(results)
        self.gas_calculator.print_calculation(results)
        # إضافة للتقرير الموحد
        from integrated_report import IntegratedReport
        if not hasattr(self, 'integrated_report'):
            self.integrated_report = IntegratedReport()
        self.integrated_report.add_gas_calculation(results)
        
    def _calculate_hydraulic(self):
        """الحسابات الهيدروليكية"""
        print("\n💧 الحسابات الهيدروليكية")
        
        try:
            # التصنيف
            print("\nاختر التصنيف:")
            print("1. Light Hazard (2.0 mm/min)")
            print("2. OH1 (4.0 mm/min)")
            print("3. OH2 (6.0 mm/min)")
            print("4. EH1 (8.0 mm/min)")
            print("5. EH2 (12.0 mm/min)")
            
            density_map = {
                '1': 2.0, '2': 4.0, '3': 6.0, '4': 8.0, '5': 12.0
            }
            density_choice = input("اختر (1-5): ").strip()
            density = density_map.get(density_choice, 6.0)
            
            # المساحة التصميمية
            area = float(input("المساحة التصميمية (م²): "))
            
            # عدد العناصر
            landing = int(input("عدد Landing Valves: ") or 0)
            hydrants = int(input("عدد الهيدرانت: ") or 0)
            cabinets = int(input("عدد صناديق الحريق: ") or 0)
            
            # المسافة
            length = float(input("طول الماسورة الرئيسية (متر): ") or 100)
            elevation = float(input("ارتفاع أعلى نقطة (متر): ") or 10)
            duration = int(input("مدة التشغيل (دقيقة) [30]: ") or 30)
            
            # الحساب
            self.hydraulic_result = self.hydraulic_calculator.calculate_complete_system(
                density=density,
                design_area=area,
                landing_valves=landing,
                hydrants=hydrants,
                hose_cabinets=cabinets,
                pipe_length_m=length,
                elevation_m=elevation,
                duration_min=duration
            )
            
            self.hydraulic_calculator.print_results(self.hydraulic_result)
                        # إضافة تكلفة تقديرية للمضخة والخزان للتقرير
            if self.hydraulic_result:
                pump_cost = self.hydraulic_result['pump_power_kw'] * 800  # 800 ريال/كيلوواط
                tank_cost = self.hydraulic_result['tank_volume_m3'] * 1500  # 1500 ريال/م³
                
                self.integrated_report.add_manual_item(
                    f"مضخة حريق ({self.hydraulic_result['pump_power_kw']} kW)",
                    1, pump_cost
                )
                self.integrated_report.add_manual_item(
                    f"خزان مياه ({self.hydraulic_result['tank_volume_m3']} م³)",
                    1, tank_cost
                )
        except ValueError:
            print("❌ أدخل أرقاماً صحيحة!")
        except Exception as e:
            print(f"❌ خطأ: {e}")
    
    def _show_integrated_report(self):
        """عرض التقرير الموحد"""
        self.integrated_report.print_summary()
        
        # حفظ؟
        save = input("\nحفظ التقرير؟ (y/n): ").strip().lower()
        if save == 'y':
            path = self.integrated_report.save_json()
            print(f"✅ تم الحفظ: {path}")


def main():
    """الدالة الرئيسية"""
    interface = MainInterface()
    interface.run()


if __name__ == "__main__":
    main()