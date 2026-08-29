# src/main.py
"""
البرنامج الرئيسي لتحليل ملفات CAD لأنظمة مكافحة الحريق
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

# إضافة مسار src إلى sys.path
sys.path.insert(0, os.path.dirname(__file__))

from cad_reader import CADReader
from entity_extractor import EntityExtractor
from nfpa_validator import NFPAValidator
from saudi_validator import SaudiCodeValidator
from report_generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FireCADAnalyzer:
    """المحلل الرئيسي لملفات CAD"""
    
    def __init__(self):
        self.reader = CADReader()
        self.extractor = None
        self.entities = {}
        self.validation_results = {}
    
    def analyze_file(self, file_path: str, hazard_type: str = None, output_dir: str = "reports") -> Dict[str, Any]:
        """
        تحليل ملف CAD كامل
        
        Args:
            file_path: مسار ملف CAD
            hazard_type: تصنيف المخاطر (light, oh1, oh2, eh1, eh2) - اختياري
            output_dir: مجلد التقارير الناتجة
            
        Returns:
            Dict: نتائج التحليل الكاملة
        """
        logger.info(f"بدء تحليل الملف: {file_path}")
        
        # 1. قراءة الملف
        if not self.reader.read_file(file_path):
            logger.error("فشل قراءة الملف")
            return {}
        
        # 2. استخراج العناصر
        self.extractor = EntityExtractor(
            self.reader.modelspace,
            self.reader.doc
        )
        self.entities = self.extractor.extract_all()
        
        # 3. التحقق من المعايير
        nfpa_validator = NFPAValidator(self.entities, hazard_type)
        self.validation_results['nfpa'] = nfpa_validator.validate_all()
        
        saudi_validator = SaudiCodeValidator(self.entities)
        self.validation_results['saudi'] = saudi_validator.validate_all()
        
        # 4. توليد التقارير
        report_generator = ReportGenerator(
            file_path=file_path,
            entities=self.entities,
            validation_results=self.validation_results,
            document_info=self.reader.get_document_info()
        )
        
        # إنشاء مجلد التقارير
        Path(output_dir).mkdir(exist_ok=True)
        
        json_report = report_generator.generate_json_report()
        pdf_report = report_generator.generate_pdf_report()
        
        # حفظ التقارير
        json_path = Path(output_dir) / "analysis_report.json"
        pdf_path = Path(output_dir) / "analysis_report.pdf"
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"تم حفظ التقرير النصي: {json_path}")
        logger.info(f"تم حفظ التقرير الكامل: {pdf_path}")
        
        return {
            'entities': self.entities,
            'validation': self.validation_results,
            'reports': {
                'json': str(json_path),
                'pdf': str(pdf_path)
            }
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """الحصول على ملخص سريع للتحليل"""
        return {
            'total_sprinklers': len(self.entities.get('sprinklers', [])),
            'total_pipes': len(self.entities.get('pipes', [])),
            'total_length_pipes': sum(
                pipe['length'] for pipe in self.entities.get('pipes', [])
            ),
            'total_pumps': len(self.entities.get('pumps', [])),
            'total_tanks': len(self.entities.get('tanks', [])),
            'total_rooms': len(self.entities.get('rooms', [])),
            'violations': {
                'nfpa': len(self.validation_results.get('nfpa', {}).get('violations', [])),
                'saudi': len(self.validation_results.get('saudi', {}).get('violations', [])),
            }
        }


def main():
    """الدالة الرئيسية"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='محلل ملفات CAD لأنظمة مكافحة الحريق'
    )
    parser.add_argument(
        'file_path',
        help='مسار ملف CAD (DXF أو DWG)'
    )
    parser.add_argument(
        '--output', '-o',
        default='reports',
        help='مجلد التقارير الناتجة (افتراضياً: reports)'
    )
    parser.add_argument(
        '--hazard',
        default=None,
        help='تصنيف المخاطر (light, oh1, oh2, eh1, eh2)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='عرض معلومات تفصيلية'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    analyzer = FireCADAnalyzer()
    
    try:
        results = analyzer.analyze_file(
            args.file_path,
            hazard_type=args.hazard,
            output_dir=args.output
        )
        
        if results:
            print("\n" + "="*60)
            print("📊 ملخص التحليل")
            print("="*60)
            
            summary = analyzer.get_summary()
            
            print(f"✅ تم تحليل الملف بنجاح")
            print(f"🔹 عدد الرشاشات: {summary['total_sprinklers']}")
            print(f"🔹 عدد المواسير: {summary['total_pipes']}")
            print(f"🔹 إجمالي طول المواسير: {summary['total_length_pipes']:.2f} متر")
            print(f"🔹 عدد المضخات: {summary['total_pumps']}")
            print(f"🔹 عدد الخزانات: {summary['total_tanks']}")
            print(f"🔹 عدد الغرف: {summary['total_rooms']}")
            print(f"\n⚠️ المخالفات:")
            print(f"   - NFPA: {summary['violations']['nfpa']} مخالفة")
            print(f"   - الكود السعودي: {summary['violations']['saudi']} مخالفة")
            print(f"\n📁 التقارير:")
            print(f"   - JSON: {results['reports']['json']}")
            print(f"   - PDF: {results['reports']['pdf']}")
            
    except Exception as e:
        logger.error(f"خطأ في التحليل: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()