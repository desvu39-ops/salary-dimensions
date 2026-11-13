import csv
import pytest
from salary_dimensions.batch import parse_csv


def test_csv_roundtrip(tmp_path):
    source = tmp_path / "in.csv"
    target = tmp_path / "out.csv"
    with source.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=["id", "salary"])
        writer.writeheader()
        writer.writerows([{"id": "1", "salary": "20-35K·14薪"}, {"id": "2", "salary": "面议"}])
    assert parse_csv(source, target) == 2
    with target.open(encoding="utf-8-sig", newline="") as fp:
        rows = list(csv.DictReader(fp))
    assert rows[0]["salary"] == "20-35K·14薪"
    assert rows[0]["annual_min"] == "280000"
    assert rows[1]["status"] == "negotiable"


def test_missing_column(tmp_path):
    source, target = tmp_path / "in.csv", tmp_path / "out.csv"
    source.write_text("id,not_salary\n1,abc\n", encoding="utf-8")
    with pytest.raises(ValueError, match="salary"):
        parse_csv(source, target)
