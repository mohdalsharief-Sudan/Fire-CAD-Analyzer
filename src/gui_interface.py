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
        lines.append(f"• مخالفات NFPA: {len(nfpa_results.get('violations', []))}")
        lines.append(f"• مخالفات سعودي: {len(saudi_results.get('violations', []))}")
        lines.append("")
        lines.append("💰 التكاليف:")
        lines.append(f"• تكلفة المواد: {self.cost_summary['total_material_cost']:,.2f} ريال")
        lines.append(f"• تكلفة التركيب: {self.cost_summary['total_labor_cost']:,.2f} ريال")
        lines.append(f"• الإجمالي: {self.cost_summary['total_cost']:,.2f} ريال")
        
        self.root.after(0, self._update_text, "\n".join(lines))
    
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
        """تصدير Excel"""
        if not self.cost_summary:
            return
        
        exporter = ExcelExporter(self.cost_summary, os.path.basename(self.file_path.get()))
        path = exporter.export()
        messagebox.showinfo("تم", f"تم الحفظ:\n{path}")
    
    def _export_pricing(self):
        """تصدير إلى Fire-Pricing"""
        if not self.cost_summary or not self.entities:
            return
        
        exporter = PricingExporter()
        path = exporter.export_for_fire_pricing(
            self.cost_summary,
            self.entities,
            os.path.basename(self.file_path.get())
        )
        messagebox.showinfo("تم", f"تم التصدير:\n{path}\n\nيمكنك استيراده في Fire-Pricing")
    
    def run(self):
        """تشغيل الواجهة"""
        self.root.mainloop()


def main():
    """الدالة الرئيسية"""
    gui = CADAnalyzerGUI()
    gui.run()


if __name__ == "__main__":
    main()