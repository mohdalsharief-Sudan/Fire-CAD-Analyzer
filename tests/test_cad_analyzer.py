# tests/test_cad_analyzer.py
import pytest
from src.cad_reader import CADReader
from src.entity_extractor import EntityExtractor

def test_read_dxf_file():
    reader = CADReader()
    assert reader.read_file("tests/test_data/sample.dxf") == True
    
def test_extract_sprinklers():
    reader = CADReader()
    reader.read_file("tests/test_data/sample.dxf")
    
    extractor = EntityExtractor(reader.modelspace, reader.doc)
    entities = extractor.extract_all()
    
    assert len(entities['sprinklers']) > 0