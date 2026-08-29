# src/cad_reader.py
"""
قارئ ملفات CAD المتخصص في أنظمة مكافحة الحريق
يدعم DXF مباشرة وDWG عن طريق التحويل
"""

import ezdxf
import os
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CADReader:
    """قارئ ملفات CAD لأنظمة مكافحة الحريق"""
    
    def __init__(self):
        self.doc = None
        self.modelspace = None
    
    def read_file(self, file_path: str) -> bool:
        """قراءة ملف CAD (DXF أو DWG)"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.dxf':
            return self._read_dxf(file_path)
        elif file_extension == '.dwg':
            return self._read_dwg(file_path)
        else:
            logger.error(f"صيغة غير مدعومة: {file_extension}")
            return False
    
    def _read_dxf(self, file_path: str) -> bool:
        """قراءة DXF مباشرة"""
        try:
            self.doc = ezdxf.readfile(file_path)
            self.modelspace = self.doc.modelspace()
            logger.info(f"تم قراءة ملف DXF بنجاح: {file_path}")
            return True
        except Exception as e:
            logger.error(f"فشل قراءة DXF: {e}")
            return False
    
    def _read_dwg(self, file_path: str) -> bool:
        """قراءة DWG - تحويل تلقائي ثم قراءة DXF"""
        logger.info(f"محاولة تحويل DWG إلى DXF: {file_path}")
        
        # إنشاء مجلدات مؤقتة للتحويل
        base_dir = os.path.dirname(file_path)
        input_dir = os.path.join(base_dir, "dwg_input")
        output_dir = os.path.join(base_dir, "dwg_output")
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # نسخ الملف إلى مجلد الإدخال
        import shutil
        file_name = os.path.basename(file_path)
        temp_dwg = os.path.join(input_dir, file_name)
        shutil.copy2(file_path, temp_dwg)
        
        output_name = os.path.splitext(file_name)[0]
        dxf_path = os.path.join(output_dir, output_name + ".dxf")
        
        # البحث عن ODA
        oda_paths = [
            r"C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe",
            r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe",
        ]
        
        for oda_path in oda_paths:
            if os.path.exists(oda_path):
                try:
                    # ODA: مجلد إدخال ≠ مجلد إخراج
                    cmd = [
                        oda_path,
                        input_dir,      # مجلد الإدخال
                        output_dir,     # مجلد الإخراج (مختلف!)
                        "ACAD2018",
                        "DXF",
                        "0",
                        "*.dwg",
                        ""
                    ]
                    
                    logger.info(f"تحويل من: {input_dir}")
                    logger.info(f"إلى: {output_dir}")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    
                    if os.path.exists(dxf_path):
                        logger.info(f"تم التحويل: {dxf_path}")
                        return self._read_dxf(dxf_path)
                    else:
                        logger.warning(f"stdout: {result.stdout}")
                        logger.warning(f"stderr: {result.stderr}")
                        
                except Exception as e:
                    logger.warning(f"فشل ODA: {e}")
        
        logger.error("فشل تحويل DWG")
        return False
    
    def check_dwg_support(self) -> bool:
        """التحقق من توفر محول DWG"""
        oda_paths = [
            r"C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe",
            r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe",
            r"C:\Program Files (x86)\ODA\ODAFileConverter\ODAFileConverter.exe",
        ]
        
        for path in oda_paths:
            if os.path.exists(path):
                logger.info(f"✅ محول DWG متوفر: {path}")
                return True
        
        logger.warning("⚠️ لا يوجد محول DWG")
        return False
    
    def get_document_info(self) -> Dict[str, Any]:
        """استخراج معلومات عامة عن الملف"""
        if not self.doc:
            return {}
        
        header = self.doc.header
        return {
            'dxf_version': self.doc.dxfversion,
            'units': header.get('$INSUNITS', 0),
            'layers': len(self.doc.layers),
            'entities': len(self.modelspace),
        }