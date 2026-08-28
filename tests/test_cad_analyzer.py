echo import sys > tests\test_cad_analyzer.py
echo sys.path.insert(0, '../src') >> tests\test_cad_analyzer.py
echo from cad_reader import CADReader >> tests\test_cad_analyzer.py
echo def test_read_dxf(): >> tests\test_cad_analyzer.py
echo     reader = CADReader() >> tests\test_cad_analyzer.py
echo     assert reader is not None >> tests\test_cad_analyzer.py