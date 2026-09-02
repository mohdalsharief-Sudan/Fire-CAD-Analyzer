# src/gui_interface.py
"""
واجهة رسومية لـ Fire-CAD-Analyzer
باستخدام Tkinter
"""

import sys
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext

sys.path.insert(0, os.path.dirname(__file__))

from cad_reader import CADReader
from entity_extractor import EntityExtractor
from nfpa_validator import NFPAValidator
from saudi_validator import SaudiCodeValidator
from cost_calculator import CostCalculator
from excel_exporter import ExcelExporter
from pricing_exporter import PricingExporter
from pipe_sizing import PipeSizing

class CADAnalyzerGUI:
    """واجهة رسومية لمحلل CAD"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Fire CAD Analyzer - نظام تحليل أنظمة مكافحة الحريق")
        self.root.geometry("800x600")
        self.root.configure(bg="#0f1626")
        
        # المتغيرات
        self.file_path = tk.StringVar()
        self.hazard_type = tk.StringVar(value="ordinary_hazard_g2")
        self.status_var = tk.StringVar(value="جاهز")
        
        # البيانات
        self.entities = None
        self.cost_summary = None
        
        self._build_ui()
    
    def _build_ui(self):
        """بناء الواجهة"""
        # العنوان
        title_frame = tk.Frame(self.root, bg="#1B4F72")
        title_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="🔥 Fire CAD Analyzer",
            font=("Arial", 24, "bold"),
            bg="#1B4F72",
            fg="white",
            padx=20,
            pady=15,
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="تحليل أنظمة مكافحة الحريق - حساب التكاليف - فحص المعايير",
            font=("Arial", 11),
            bg="#1B4F72",
            fg="#A8D5E5",
        )
        subtitle_label.pack(pady=(0, 10))
        
        # إطار اختيار الملف
        file_frame = tk.Frame(self.root, bg="#0f1626")
        file_frame.pack(fill="x", padx=10, pady=10)
        
        file_label = tk.Label(
            file_frame,
            text="ملف CAD:",
            font=("Arial", 11),
            bg="#0f1626",
            fg="white",
        )
        file_label.pack(side="left", padx=5)
        
        file_entry = tk.Entry(
            file_frame,
            textvariable=self.file_path,
            width=50,
            font=("Arial", 11),
        )
        file_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        browse_btn = tk.Button(
            file_frame,
            text="📁 استعراض",
            command=self._browse_file,
            bg="#2874A6",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor="hand2",
        )
        browse_btn.pack(side="left", padx=5)
        
        # إطار التصنيف
        hazard_frame = tk.Frame(self.root, bg="#0f1626")
        hazard_frame.pack(fill="x", padx=10, pady=10)
        
        hazard_label = tk.Label(
            hazard_frame,
            text="تصنيف المخاطر:",
            font=("Arial", 11),
            bg="#0f1626",
            fg="white",
        )
        hazard_label.pack(side="left", padx=5)
        
        hazard_options = {
            "خفيف (Light Hazard)": "light_hazard",
            "عادي 1 (OH1)": "ordinary_hazard_g1",
            "عادي 2 (OH2)": "ordinary_hazard_g2",
            "شديد 1 (EH1)": "extra_hazard_g1",
            "شديد 2 (EH2)": "extra_hazard_g2",
            "تلقائي": "auto",
        }
        
        hazard_combo = ttk.Combobox(
            hazard_frame,
            textvariable=self.hazard_type,
            values=list(hazard_options.keys()),
            width=25,
            font=("Arial", 10),
            state="readonly",
        )
        hazard_combo.current(2)  # OH2 افتراضياً
        hazard_combo.pack(side="left", padx=5)
                # إطار عناصر التدفق
        flow_frame = tk.Frame(self.root, bg="#0f1626")
        flow_frame.pack(fill="x", padx=10, pady=5)
        
        flow_label = tk.Label(
            flow_frame,
            text="عناصر التدفق:",
            font=("Arial", 11, "bold"),
            bg="#0f1626",
            fg="#3498DB",
        )
        flow_label.pack(side="left", padx=5)
        
        landing_label = tk.Label(flow_frame, text="Landing Valves:", font=("Arial", 10), bg="#0f1626", fg="white")
        landing_label.pack(side="left", padx=5)
        self.landing_valves = tk.Spinbox(flow_frame, from_=0, to=100, width=5, font=("Arial", 10))
        self.landing_valves.pack(side="left", padx=2)
        
        fhc_label = tk.Label(flow_frame, text="صناديق حريق:", font=("Arial", 10), bg="#0f1626", fg="white")
        fhc_label.pack(side="left", padx=5)
        self.hose_cabinets = tk.Spinbox(flow_frame, from_=0, to=100, width=5, font=("Arial", 10))
        self.hose_cabinets.pack(side="left", padx=2)
        
        hydrant_label = tk.Label(flow_frame, text="هيدرانت:", font=("Arial", 10), bg="#0f1626", fg="white")
        hydrant_label.pack(side="left", padx=5)
        self.hydrants = tk.Spinbox(flow_frame, from_=0, to=10, width=5, font=("Arial", 10))
        self.hydrants.pack(side="left", padx=2)
        # زر التحليل
        analyze_frame = tk.Frame(self.root, bg="#0f1626")
        analyze_frame.pack(fill="x", padx=10, pady=10)
        
        self.analyze_btn = tk.Button(
            analyze_frame,
            text="🚀 بدء التحليل",
            command=self._start_analysis,
            bg="#27AE60",
            fg="white",
            font=("Arial", 13, "bold"),
            padx=30,
            pady=10,
            cursor="hand2",
        )
        self.analyze_btn.pack()
        
        # إطار شريط التقدم
        progress_frame = tk.Frame(self.root, bg="#0f1626")
        progress_frame.pack(fill="x", padx=10, pady=10)
        
        self.progress = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            length=500,
            maximum=100,
            value=0,
        )
        self.progress.pack(side="left", padx=5, fill="x", expand=True)
        
        self.progress_label = tk.Label(
            progress_frame,
            text="0%",
            font=("Arial", 11, "bold"),
            bg="#0f1626",
            fg="#3498DB",
        )
        self.progress_label.pack(side="left", padx=5)
        
        # أزرار التصدير (تظهر بعد التحليل)
        export_frame = tk.Frame(self.root, bg="#0f1626")
        export_frame.pack(fill="x", padx=10, pady=5)
        
        self.excel_btn = tk.Button(
            export_frame,
            text="📊 Excel",
            command=self._export_excel,
            bg="#2874A6",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor="hand2",
            state="normal",
        )
        self.excel_btn.pack(side="left", padx=5)
        
        self.pricing_btn = tk.Button(
            export_frame,
            text="💰 Fire-Pricing",
            command=self._export_pricing,
            bg="#E67E22",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            cursor="hand2",
            state="normal",
        )
        self.pricing_btn.pack(side="left", padx=5)
        # منطقة النتائج
        result_frame = tk.Frame(self.root, bg="#0f1626")
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            width=80,
            height=20,
            font=("Consolas", 10),
            bg="#1a1a2e",
            fg="#e0e0e0",
            insertbackground="white",
        )
        self.result_text.pack(fill="both", expand=True)
        
        # شريط الحالة
        status_frame = tk.Frame(self.root, bg="#1B4F72")
        status_frame.pack(fill="x", side="bottom")
        
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 10),
            bg="#1B4F72",
            fg="white",
            padx=10,
            pady=5,
        )
        status_label.pack(side="left")
        
        
    
    def _browse_file(self):
        """اختيار ملف"""
        file_path = filedialog.askopenfilename(
            title="اختر ملف CAD",
            filetypes=[
                ("CAD Files", "*.dxf;*.dwg"),
                ("DXF Files", "*.dxf"),
                ("DWG Files", "*.dwg"),
            ]
        )
        if file_path:
            self.file_path.set(file_path)
    
    def _start_analysis(self):
        """بدء التحليل في خيط منفصل"""
        if not self.file_path.get():
            messagebox.showerror("خطأ", "الرجاء اختيار ملف CAD أولاً")
            return
        
        # تعطيل الزر
        self.analyze_btn.config(state="disabled")
        self.progress.start()
        self.status_var.set("جاري التحليل...")
        self.result_text.delete(1.0, tk.END)
        
        # تشغيل في خيط منفصل
        thread = threading.Thread(target=self._run_analysis, daemon=True)
        thread.start()
    
    def _run_analysis(self):
        """تنفيذ التحليل مع شريط التقدم"""
        try:
            # 10% - قراءة الملف
            self._update_progress(10, "قراءة الملف...")
            reader = CADReader()
            if not reader.read_file(self.file_path.get()):
                self._show_error("فشل قراءة الملف")
                return
            
            # 30% - استخراج العناصر
            self._update_progress(30, "استخراج العناصر...")
            extractor = EntityExtractor(reader.modelspace, reader.doc)
            self.entities = extractor.extract_all()
            
            # 50% - فحص المعايير
            self._update_progress(50, "فحص المعايير...")
            hazard_map = {
                "خفيف (Light Hazard)": "light_hazard",
                "عادي 1 (OH1)": "ordinary_hazard_g1",
                "عادي 2 (OH2)": "ordinary_hazard_g2",
                "شديد 1 (EH1)": "extra_hazard_g1",
                "شديد 2 (EH2)": "extra_hazard_g2",
                "تلقائي": None,
            }
            selected_hazard = self.hazard_type.get()
            hazard_type = hazard_map.get(selected_hazard, None)
            
            nfpa = NFPAValidator(self.entities, hazard_type)
            nfpa_results = nfpa.validate_all()
            
            saudi = SaudiCodeValidator(self.entities)
            saudi_results = saudi.validate_all()
            
            # 70% - حساب التكاليف
            self._update_progress(70, "حساب التكاليف...")
            cost_calc = CostCalculator(self.entities)
            self.cost_summary = cost_calc.calculate_all()
            
             # 80% - حساب المواسير والملحقات
            self._update_progress(80, "حساب المواسير والملحقات...")
            total_pipe_length = sum(
                pipe.get('length', 0) 
                for pipe in self.entities.get('pipes', [])
            )
            sprinkler_count = len(self.entities.get('sprinklers', []))
            
            pipe_calc = PipeSizing()
            self.pipe_results = pipe_calc.calculate_complete_piping(
                total_pipe_length_m=total_pipe_length,
                sprinkler_count=sprinkler_count,
                sprinkler_type='pendant',
            )
            
            # 85% - دمج تكاليف الملحقات
            self._update_progress(85, "دمج تكاليف الملحقات...")
            if self.pipe_results:
                # تكلفة الملحقات الكلية
                fittings_total = self.pipe_results['fittings']['total_cost']
                sprinkler_fittings_total = 0
                if self.pipe_results.get('sprinkler_fittings'):
                    sprinkler_fittings_total = self.pipe_results['sprinkler_fittings']['total_cost']
                
                # إضافة للتكلفة الإجمالية
                extra_cost = fittings_total + sprinkler_fittings_total
                self.cost_summary['total_material_cost'] += extra_cost
                self.cost_summary['total_cost'] += extra_cost * 1.85  # مع التركيب والهندسة

            
            # 90% - عرض النتائج
            self._update_progress(90, "عرض النتائج...")
            self._display_results(nfpa_results, saudi_results, cost_calc)
            
            # 100% - اكتمل
            self._update_progress(100, "اكتمل التحليل")
            self.root.after(0, self._enable_export_buttons)
            
        except Exception as e:
            self._show_error(f"خطأ: {e}")
        finally:
            self.root.after(0, self._finish_analysis)
            
    def _update_progress(self, value, status):
        """تحديث شريط التقدم"""
        self.root.after(0, self._set_progress, value, status)
    
    def _set_progress(self, value, status):
        """تحديث شريط التقدم في الواجهة"""
        self.progress['value'] = value
        self.progress_label.config(text=f"{value}%")
        self.status_var.set(status)    
    
    def _display_results(self, nfpa_results, saudi_results, cost_calc):
        """عرض النتائج"""
        lines = []
        lines.append("=" * 60)
        lines.append("📊 نتائج التحليل")
        lines.append("=" * 60)
        lines.append(f"• الرشاشات: {len(self.entities.get('sprinklers', []))}")
        lines.append(f"• المواسير: {len(self.entities.get('pipes', []))}")
        lines.append(f"• المضخات: {len(self.entities.get('pumps', []))}")
        lines.append(f"• أنظمة الغاز: {len(self.entities.get('gas_systems', []))}")
        
        # استخدام قيم الواجهة للأعداد
        fhc_display = int(self.hose_cabinets.get() or 0)
        landing_display = int(self.landing_valves.get() or 0)
        hydrant_display = int(self.hydrants.get() or 0)
        
        # ← أضف هذه الأسطر الثلاثة هنا
        lines.append(f"• صناديق الحريق: {fhc_display}")
        lines.append(f"• Landing Valves: {landing_display}")
        lines.append(f"• هيدرانت: {hydrant_display}")
        
        lines.append(f"• مخالفات NFPA: {len(nfpa_results.get('violations', []))}")
        lines.append(f"• مخالفات سعودي: {len(saudi_results.get('violations', []))}")
        lines.append("")
        lines.append("💰 التكاليف:")
        lines.append(f"• تكلفة المواد: {self.cost_summary['total_material_cost']:,.2f} ريال")
        lines.append(f"• تكلفة التركيب: {self.cost_summary['total_labor_cost']:,.2f} ريال")
        lines.append(f"• الإجمالي: {self.cost_summary['total_cost']:,.2f} ريال")
        if self.pipe_results:
            fittings_total = self.pipe_results['fittings']['total_cost']
            sprinkler_fittings_total = 0
            if self.pipe_results.get('sprinkler_fittings'):
                sprinkler_fittings_total = self.pipe_results['sprinkler_fittings']['total_cost']
            
            lines.append("")
            lines.append("📐 المواسير والملحقات:")
            lines.append(f"  • الخط الرئيسي: {self.pipe_results['diameters']['main']['diameter']} مم")
            lines.append(f"  • الفاقد في الضغط: {self.pipe_results['pressure_loss_bar']} bar")
            lines.append(f"  • ملحقات الخطوط: {fittings_total:,.2f} ريال")
            lines.append(f"  • ملحقات الرشاشات: {sprinkler_fittings_total:,.2f} ريال")
            lines.append(f"  • إجمالي الملحقات: {fittings_total + sprinkler_fittings_total:,.2f} ريال")
        self.root.after(0, self._update_text, "\n".join(lines))
        
                # حساب المضخة
        GPM_TO_LPM = 3.78541
        
        landing_count = int(self.landing_valves.get() or 0)
        fhc_count = int(self.hose_cabinets.get() or 0)
        hydrant_count = int(self.hydrants.get() or 0)
        
        # التدفق التصميمي
        sprinkler_flow_gpm = 26 * 12
        
        # صناديق الحريق (حد أقصى 2)
        fhc_flow_gpm = min(fhc_count, 2) * 50
        
        # Landing Valves أو Hydrant (ليس كلاهما)
        if landing_count > 0:
            landing_flow_gpm = min(landing_count, 2) * 250
            hydrant_flow_gpm = 0
        else:
            landing_flow_gpm = 0
            hydrant_flow_gpm = min(hydrant_count, 1) * 500
        
        total_flow_gpm = sprinkler_flow_gpm + fhc_flow_gpm + landing_flow_gpm + hydrant_flow_gpm
        total_flow_lpm = total_flow_gpm * GPM_TO_LPM
        
        # الضغط الكلي
        total_pressure = self.pipe_results['pressure_loss_bar'] + 1.4
        
        # قدرة المضخة
        pump_power_kw = (total_flow_lpm * total_pressure) / (600 * 0.75)
        pump_power_hp = pump_power_kw * 1.341
        
        lines.append("")
        lines.append("🔧 المضخة:")
        lines.append(f"  • التدفق: {total_flow_gpm:.2f} GPM")
        lines.append(f"  • الضغط: {total_pressure:.2f} bar ({total_pressure * 14.5038:.2f} PSI)")
        lines.append(f"  • القدرة: {pump_power_kw:.2f} kW ({pump_power_hp:.2f} HP)")
         
    def _update_text(self, text):
        """تحديث النص في الواجهة"""
        self.result_text.insert(tk.END, text)
    
    def _show_error(self, message):
        """عرض خطأ"""
        self.root.after(0, messagebox.showerror, "خطأ", message)
        self.root.after(0, self._update_text, f"❌ {message}")
    
    def _finish_analysis(self):
        """إنهاء التحليل"""
        self.progress.stop()
        self.analyze_btn.config(state="normal")
        self.status_var.set("اكتمل التحليل")
    
    def _enable_export_buttons(self):
        """تفعيل أزرار التصدير"""
        self.excel_btn.config(state="normal")
        self.pricing_btn.config(state="normal")
    
    def _export_excel(self):
        """تصدير Excel بقيم الواجهة"""
        if not self.cost_summary:
            messagebox.showwarning("تنبيه", "لا توجد بيانات للتصدير - قم بالتحليل أولاً")
            return
        
        # تحديث أعداد العناصر من الواجهة
        cost_summary_copy = self.cost_summary.copy()
        
        # تعديل عدد صناديق الحريق
        fhc_count = int(self.hose_cabinets.get() or 0)
        landing_count = int(self.landing_valves.get() or 0)
        hydrant_count = int(self.hydrants.get() or 0)
        
        for item in cost_summary_copy.get('items', []):
            if 'خزانات خرطوم' in item.get('item', ''):
                item['quantity'] = fhc_count
                item['subtotal'] = fhc_count * item.get('unit_price', 0)
        
        # إعادة حساب الإجمالي
        total_material = sum(item.get('subtotal', 0) for item in cost_summary_copy.get('items', []))
        cost_summary_copy['total_material_cost'] = total_material
        
        from datetime import datetime
        
        project_root = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(project_root, 'reports')
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"cost_estimate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join(output_dir, filename)
        
        exporter = ExcelExporter(cost_summary_copy, os.path.basename(self.file_path.get()))
        path = exporter.export(output_path)
        messagebox.showinfo("تم", f"تم الحفظ:\n{path}")
    
    def _export_pricing(self):
        """تصدير إلى Fire-Pricing بقيم الواجهة"""
        if not self.cost_summary or not self.entities:
            messagebox.showwarning("تنبيه", "لا توجد بيانات للتصدير - قم بالتحليل أولاً")
            return
        
        # تحديث الأعداد من الواجهة
        entities_copy = self.entities.copy()
        entities_copy['hose_cabinets'] = []  # نعيد إنشاؤها بالعدد الصحيح
        
        fhc_count = int(self.hose_cabinets.get() or 0)
        for i in range(fhc_count):
            entities_copy['hose_cabinets'].append({'type': 'hose_cabinet'})
        
        project_root = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(project_root, 'pricing_export')
        os.makedirs(output_dir, exist_ok=True)
        
        exporter = PricingExporter()
        path = exporter.export_for_fire_pricing(
            self.cost_summary,
            entities_copy,
            os.path.basename(self.file_path.get()),
            output_dir=output_dir
        )
        messagebox.showinfo("تم", f"تم التصدير:\n{path}")
    
    def run(self):
        """تشغيل الواجهة"""
        self.root.mainloop()


def main():
    """الدالة الرئيسية"""
    gui = CADAnalyzerGUI()
    gui.run()


if __name__ == "__main__":
    main()