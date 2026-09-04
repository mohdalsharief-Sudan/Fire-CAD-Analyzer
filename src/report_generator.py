# src/report_generator.py
"""
توليد التقارير النصية و PDF
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import arabic_reshaper
from bidi.algorithm import get_display


# تسجيل خط يدعم العربية
FONT_PATH = None
for path in [
    r"C:\Windows\Fonts\tahoma.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\calibri.ttf",
]:
    if os.path.exists(path):
        FONT_PATH = path
        break

if FONT_PATH:
    pdfmetrics.registerFont(TTFont('ArabicFont', FONT_PATH))
    ARABIC_FONT = 'ArabicFont'
else:
    ARABIC_FONT = 'Helvetica'


def ar(text):
    """تحويل النص العربي للعرض الصحيح"""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except:
        return str(text)


class ReportGenerator:
    """مولد التقارير"""
    
    def __init__(self, file_path: str, entities: Dict[str, List[Dict]], 
                 validation_results: Dict[str, Any], document_info: Dict[str, Any]):
        self.file_path = file_path
        self.entities = entities
        self.validation_results = validation_results
        self.document_info = document_info
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_json_report(self) -> Dict[str, Any]:
        """توليد تقرير JSON"""
        report = {
            'metadata': {
                'file': self.file_path,
                'analyzed_at': self.timestamp,
                'document_info': self.document_info
            },
            'entities_summary': {
                'sprinklers': {
                    'count': len(self.entities.get('sprinklers', [])),
                    'items': self.entities.get('sprinklers', [])
                },
                'pipes': {
                    'count': len(self.entities.get('pipes', [])),
                    'total_length': sum(p.get('length', 0) for p in self.entities.get('pipes', [])),
                    'items': self.entities.get('pipes', [])
                },
                'pumps': {
                    'count': len(self.entities.get('pumps', [])),
                    'items': self.entities.get('pumps', [])
                },
                'tanks': {
                    'count': len(self.entities.get('tanks', [])),
                    'total_volume': sum(t.get('volume', 0) for t in self.entities.get('tanks', [])),
                    'items': self.entities.get('tanks', [])
                },
                'rooms': {
                    'count': len(self.entities.get('rooms', [])),
                    'items': self.entities.get('rooms', [])
                }
            },
            'validation': self.validation_results,
            'summary': self._generate_summary()
        }
        
        return report
    
    def generate_pdf_report(self) -> str:
        """توليد تقرير PDF احترافي"""
        # حفظ في المجلد الرئيسي reports/
        reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        output_path = os.path.join(reports_dir, f"fire_system_analysis_{...}.pdf")
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # الأنماط
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=ARABIC_FONT,
            fontSize=22,
            textColor=colors.HexColor('#1B4F72'),
            alignment=TA_RIGHT,
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=ARABIC_FONT,
            fontSize=16,
            textColor=colors.HexColor('#2874A6'),
            spaceBefore=20,
            spaceAfter=10
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=ARABIC_FONT,
            fontSize=10,
            leading=14
        )
        
        # بناء المحتوى - كل النصوص تمر عبر ar()
        story = []
        
        # العنوان
        story.append(Paragraph(ar("تقرير تحليل نظام مكافحة الحريق"), title_style))
        story.append(Paragraph(ar(f"ملف CAD: {self.file_path}"), normal_style))
        story.append(Paragraph(ar(f"تاريخ التحليل: {self.timestamp}"), normal_style))
        story.append(Spacer(1, 20))
        
        # ملخص العناصر
        story.append(Paragraph(ar("ملخص العناصر المستخرجة"), heading_style))
        
        summary_data = [
            [ar('العنصر'), ar('العدد'), ar('ملاحظات')],
            [ar('الرشاشات'), str(len(self.entities.get('sprinklers', []))), ''],
            [ar('المواسير'), str(len(self.entities.get('pipes', []))), 
             ar(f"الطول الكلي: {sum(p.get('length', 0) for p in self.entities.get('pipes', [])):.2f} م")],
            [ar('المضخات'), str(len(self.entities.get('pumps', []))), ''],
            [ar('الخزانات'), str(len(self.entities.get('tanks', []))), 
             ar(f"الحجم الكلي: {sum(t.get('volume', 0) for t in self.entities.get('tanks', [])):.2f} م³")],
            [ar('الغرف'), str(len(self.entities.get('rooms', []))), ''],
        ]
        
        summary_table = Table(summary_data, colWidths=[5*cm, 3*cm, 9*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B4F72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), ARABIC_FONT),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#EBF5FB')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2874A6')),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # نتائج التحقق
        story.append(Paragraph(ar("نتائج التحقق من المعايير"), heading_style))
        
        # مخالفات NFPA
        nfpa_violations = self.validation_results.get('nfpa', {}).get('violations', [])
        story.append(Paragraph(ar(f"مخالفات NFPA: {len(nfpa_violations)}"), normal_style))
        
        if nfpa_violations:
            for violation in nfpa_violations[:20]:  # أول 20 فقط
                severity_color = {
                    'critical': '#C0392B',
                    'high': '#E67E22',
                    'medium': '#F1C40F',
                    'low': '#27AE60'
                }.get(violation.get('severity', 'low'), '#27AE60')
                
                story.append(Paragraph(
                    ar(f"• {violation.get('message', '')}"),
                    normal_style
                ))
        
        story.append(Spacer(1, 20))
        
        # مخالفات الكود السعودي
        saudi_violations = self.validation_results.get('saudi', {}).get('violations', [])
        story.append(Paragraph(ar(f"مخالفات الكود السعودي: {len(saudi_violations)}"), normal_style))
        
        if saudi_violations:
            for violation in saudi_violations:
                story.append(Paragraph(ar(f"• {violation.get('message', '')}"), normal_style))
        
        # بناء PDF
        doc.build(story)
        
        return output_path
    
    def _generate_summary(self) -> Dict[str, Any]:
        """توليد ملخص سريع"""
        return {
            'total_components': sum(
                len(self.entities.get(key, [])) 
                for key in ['sprinklers', 'pipes', 'pumps', 'tanks']
            ),
            'total_violations': (
                len(self.validation_results.get('nfpa', {}).get('violations', [])) +
                len(self.validation_results.get('saudi', {}).get('violations', []))
            ),
            'system_complete': (
                len(self.entities.get('sprinklers', [])) > 0 and
                len(self.entities.get('pipes', [])) > 0 and
                len(self.entities.get('pumps', [])) > 0
            )
        }
        
    def generate_comprehensive_pdf(self, 
                                    entities_summary: Dict,
                                    cost_summary: Dict,
                                    pipe_results: Dict,
                                    pump_results: Dict,
                                    tank_results: Dict = None,
                                    output_path: str = None) -> str:
        """
        توليد تقرير PDF شامل
        
        Args:
            entities_summary: ملخص العناصر
            cost_summary: التكاليف
            pipe_results: نتائج المواسير
            pump_results: نتائج المضخة
            
        Returns:
            str: مسار الملف
        """
        if not output_path:
            reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            output_path = os.path.join(reports_dir, f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
                # الأنماط
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CompTitle',
            parent=styles['Heading1'],
            fontName=ARABIC_FONT,
            fontSize=22,
            textColor=colors.HexColor('#1B4F72'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CompHeading',
            parent=styles['Heading2'],
            fontName=ARABIC_FONT,
            fontSize=16,
            textColor=colors.HexColor('#2874A6'),
            alignment=TA_RIGHT,
            spaceBefore=20,
            spaceAfter=10
        )
        normal_style = ParagraphStyle(
            'CompNormal',
            parent=styles['Normal'],
            fontName=ARABIC_FONT,
            fontSize=10,
            leading=14,
            alignment=TA_RIGHT
        )
        story = []
        
        # العنوان
        story.append(Paragraph(ar("تقرير شامل - نظام مكافحة الحريق"), title_style))
        story.append(Spacer(1, 20))
                # جدول العناصر
        story.append(Paragraph(ar("تفاصيل العناصر المستخرجة"), heading_style))
        
        items_data = [
            [ar('العنصر'), ar('العدد')],
            [ar('الرشاشات'), str(entities_summary.get('sprinklers', 0))],
            [ar('المواسير'), str(entities_summary.get('pipes', 0))],
            [ar('المضخات'), str(entities_summary.get('pumps', 0))],
            [ar('أنظمة الغاز'), str(entities_summary.get('gas_systems', 0))],
            [ar('صناديق الحريق'), str(entities_summary.get('hose_cabinets', 0))],
            [ar('Landing Valves'), str(entities_summary.get('landing_valves', 0))],
            [ar('الهيدرانت'), str(entities_summary.get('hydrants', 0))],
        ]
        
        items_table = Table(items_data, colWidths=[8*cm, 8*cm])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B4F72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), ARABIC_FONT),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#EBF5FB')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2874A6')),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 20))
        
        # 1. نتائج التحليل
        story.append(Paragraph(ar("1. نتائج التحليل"), heading_style))
        story.append(Paragraph(ar(f"• الرشاشات: {entities_summary.get('sprinklers', 0)}"), normal_style))
        story.append(Paragraph(ar(f"• المواسير: {entities_summary.get('pipes', 0)}"), normal_style))
        story.append(Paragraph(ar(f"• المضخات: {entities_summary.get('pumps', 0)}"), normal_style))
        story.append(Spacer(1, 10))
        
        # 2. حساب المضخة
        if pump_results:
            story.append(Paragraph(ar("2. حساب المضخة"), heading_style))
            story.append(Paragraph(ar(f"• التدفق: {pump_results.get('total_flow_gpm', 0)} GPM"), normal_style))
            story.append(Paragraph(ar(f"• الضغط: {pump_results.get('total_pressure_bar', 0)} bar"), normal_style))
            story.append(Paragraph(ar(f"• القدرة: {pump_results.get('pump_power_kw', 0)} kW"), normal_style))
            story.append(Spacer(1, 10))
        
        # 3. الخزان
        if tank_results:
            story.append(Paragraph(ar("حساب الخزان"), heading_style))
            story.append(Paragraph(ar(f"• الحجم: {tank_results.get('volume_m3', 0)} م³"), normal_style))
            story.append(Paragraph(ar(f"• مع الاحتياطي: {tank_results.get('volume_with_reserve_m3', 0)} م³"), normal_style))
            story.append(Paragraph(ar(f"• المدة: {tank_results.get('duration_min', 30)} دقيقة"), normal_style))
            story.append(Spacer(1, 10))
            
        # 4. المواسير والملحقات
        if pipe_results:
            story.append(Paragraph(ar("3. المواسير والملحقات"), heading_style))
            for section, data in pipe_results['diameters'].items():
                story.append(Paragraph(ar(f"• {section}: {data['diameter']} مم"), normal_style))
            story.append(Paragraph(ar(f"• الفاقد في الضغط: {pipe_results['pressure_loss_bar']} bar"), normal_style))
            story.append(Spacer(1, 10))
        
        # جدول التكاليف
        if cost_summary:
            story.append(Paragraph(ar("5. التكاليف"), heading_style))                   
            cost_data = [[ar('البند'), ar('التكلفة (ريال)')]]
            for item in cost_summary.get('items', [])[:20]:  # أول 20 بند
                cost_data.append([
                    ar(item.get('item', '')),
                    f"{item.get('subtotal', 0):,.2f}"
                ])
            
            cost_table = Table(cost_data, colWidths=[10*cm, 6*cm])
            cost_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B4F72')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), ARABIC_FONT),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#EBF5FB')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2874A6')),
            ]))
            
            story.append(cost_table)
            doc.build(story)
        return output_path    