import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cad_reader import CADReader
from entity_extractor import EntityExtractor


def test_cad_reader_init():
    """اختبار إنشاء قارئ CAD"""
    reader = CADReader()
    assert reader is not None
    assert reader.doc is None
    assert reader.modelspace is None


def test_entity_extractor_init():
    """اختبار إنشاء مستخرج العناصر"""
    import ezdxf
    
    doc = ezdxf.new()
    msp = doc.modelspace()
    
    extractor = EntityExtractor(msp, doc)
    assert extractor is not None
    assert extractor.unit_conversion > 0