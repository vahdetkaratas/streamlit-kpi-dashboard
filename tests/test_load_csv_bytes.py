from src.load import load_csv_from_bytes


def test_load_csv_from_bytes_roundtrip():
    raw = b"a,b\n1,2\n"
    df = load_csv_from_bytes(raw)
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 1
