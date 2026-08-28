# src/cad_reader.py
"""
قارئ ملفات CAD المتخصص في أنظمة مكافحة الحريق
يدعم ملفات DXF مباشرة وDWG عن طريق التحويل
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
        self.entities = {
            'sprinklers': [],
            'pipes': [],
            'pumps': [],
            'valves': [],
            'tanks': [],
            'rooms': [],
            'walls': [],
            'texts': [],
            'blocks': [],
            'unknown': []
        }
        
    def read_file(self, file_path: str) -> bool:
        """
        قراءة ملف CAD (DXF مباشرة أو DWG بالتحويل)
        
        Args:
            file_path: مسار الملف
            
        Returns:
            bool: نجاح القراءة
        """
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.dxf':
            return self._read_dxf(file_path)
        elif file_extension == '.dwg':
            return self._read_dwg(file_path)
        else:
            logger.error(f"صيغة ملف غير مدعومة: {file_extension}")
            return False
    
    def _read_dxf(self, file_path: str) -> bool:
        """قراءة ملف DXF مباشرة"""
        try:
            self.doc = ezdxf.readfile(file_path)
            self.modelspace = self.doc.modelspace()
            logger.info(f"تم قراءة ملف DXF بنجاح: {file_path}")
            return True
        except Exception as e:
            logger.error(f"فشل قراءة ملف DXF: {e}")
            return False
    
    def _read_dwg(self, file_path: str) -> bool:
        """
        قراءة ملف DWG عن طريق تحويله إلى DXF
        يتطلب برنامج ODA File Converter أو LibreCAD
        """
        # محاولة العثور على محول DWG إلى DXF
        converters = [
            'ODAFileConverter',  # ODA File Converter
            'dwg2dxf',          # LibreCAD
            'dwgread',          # LibreDWG
        ]
        
        for converter in converters:
            try:
                # محاولة استخدام المحول
                output_path = file_path.replace('.dwg', '.dxf')
                cmd = [converter, file_path, output_path]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and os.path.exists(output_path):
                    logger.info(f"تم تحويل DWG إلى DXF باستخدام {converter}")
                    return self._read_dxf(output_path)
            except FileNotFoundError:
                continue
            except Exception as e:
                logger.warning(f"فشل التحويل باستخدام {converter}: {e}")
        
        logger.error("لم يتم العثور على محول DWG. يرجى تثبيت ODA File Converter")
        return False
    
    def get_document_info(self) -> Dict[str, Any]:
        """استخراج معلومات عامة عن الملف"""
        if not self.doc:
            return {}
        
        header = self.doc.header
        return {
            'dxf_version': self.doc.dxfversion,
            'units': header.get('$INSUNITS', 0),
            'created': header.get('$TDCREATE', 'غير معروف'),
            'modified': header.get('$TDUPDATE', 'غير معروف'),
            'layers': len(self.doc.layers),
            'entities': len(self.modelspace),
        }