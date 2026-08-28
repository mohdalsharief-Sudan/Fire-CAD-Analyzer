# src/report_generator.py
"""
توليد التقارير النصية و PDF
"""

import json
from typing import Dict, Any, List
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


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
        output_path = f"reports/fire_system_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
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
            fontSize=24,
            textColor=colors.HexColor('#1B4F72'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2874A6'),
            spaceBefore=20,
            spaceAfter=10
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            leading=14
        )
        
        # بناء المحتوى
        story = []
        
        # العنوان
        story.append(Paragraph("تقرير تحليل نظام مكافحة الحريق", title_style))
        story.append(Paragraph(f"ملف CAD: {self.file_path}", normal_style))
        story.append(Paragraph(f"تاريخ التحليل: {self.timestamp}", normal_style))
        story.append(Spacer(1, 20))
        
        # ملخص العناصر
        story.append(Paragraph("ملخص العناصر المستخرجة", heading_style))
        
        summary_data = [
            ['العنصر', 'العدد', 'ملاحظات'],
            ['الرشاشات', str(len(self.entities.get('sprinklers', []))), ''],
            ['المواسير', str(len(self.entities.get('pipes', []))), 
             f"الطول الكلي: {sum(p.get('length', 0) for p in self.entities.get('pipes', [])):.2f} م"],
            ['المضخات', str(len(self.entities.get('pumps', []))), ''],
            ['الخزانات', str(len(self.entities.get('tanks', []))), 
             f"الحجم الكلي: {sum(t.get('volume', 0) for t in self.entities.get('tanks', [])):.2f} م³"],
            ['الغرف', str(len(self.entities.get('rooms', []))), ''],
        ]
        
        summary_table = Table(summary_data, colWidths=[5*cm, 3*cm, 9*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B4F72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#EBF5FB')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2874A6')),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # نتائج التحقق
        story.append(Paragraph("نتائج التحقق من المعايير", heading_style))
        
        # مخالفات NFPA
        nfpa_violations = self.validation_results.get('nfpa', {}).get('violations', [])
        story.append(Paragraph(f"مخالفات NFPA: {len(nfpa_violations)}", normal_style))
        
        if nfpa_violations:
            for i, violation in enumerate(nfpa_violations, 1):
                severity_color = {
                    'critical': '#C0392B',
                    'high': '#E67E22',
                    'medium': '#F1C40F',
                    'low': '#27AE60'
                }.get(violation.get('severity', 'low'), '#27AE60')
                
                story.append(Paragraph(
                    f"<font color='{severity_color}'>• {violation.get('message', '')}</font>",
                    normal_style
                ))
        
        story.append(Spacer(1, 20))
        
        # مخالفات الكود السعودي
        saudi_violations = self.validation_results.get('saudi', {}).get('violations', [])
        story.append(Paragraph(f"مخالفات الكود السعودي: {len(saudi_violations)}", normal_style))
        
        if saudi_violations:
            for violation in saudi_violations:
                story.append(Paragraph(
                    f"• {violation.get('message', '')}",
                    normal_style
                ))
        
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