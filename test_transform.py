# tests/test_transform.py
from pipelines.transform import parse_date

def test_parse_date_dd_mm_yyyy():
    d = parse_date("01/05/2024")
    assert d.year == 2024
    assert d.month == 5
    assert d.day == 1
