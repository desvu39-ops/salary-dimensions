from io import BytesIO

import pytest
from openpyxl import Workbook, load_workbook
from salary_dimensions.excel import parse_xlsx, parse_xlsx_bytes


def _create_source(path):
    wb = Workbook()
    ws = wb.active
    ws.title = "招聘数据"
    ws.append(["job_id", "company", "salary"])
    ws.append(["001", "甲公司", "20-35K·14薪"])
    ws.append(["002", "乙公司", "薪资面议"])
    ws.append(["003", "丙公司", "=1+1"])
    ws.append([None, None, None])
    wb.create_sheet("说明").append(["其他内容"])
    wb.save(path)


def test_xlsx_roundtrip_and_column_types(tmp_path):
    source = tmp_path / "source.xlsx"
    output = tmp_path / "result.xlsx"
    _create_source(source)
    assert parse_xlsx(source, output, column="salary", sheet="招聘数据") == 3
    book = load_workbook(output, data_only=True)
    ws = book.active
    headers = [cell.value for cell in ws[1]]
    assert ws.max_row == 4
    assert ws.cell(2, 1).value == "001"
    assert ws.cell(2, headers.index("annual_min") + 1).value == 280000
    assert ws.cell(3, headers.index("status") + 1).value == "negotiable"
    assert ws.freeze_panes == "A2"
    book.close()
    # 不修改原始文件
    book = load_workbook(source)
    assert book.sheetnames == ["招聘数据", "说明"]
    assert book.active.max_column == 3
    book.close()


def test_parse_in_memory(tmp_path):
    source = tmp_path / "in.xlsx"
    _create_source(source)
    payload, count = parse_xlsx_bytes(source.read_bytes())
    assert count == 3
    parsed = load_workbook(BytesIO(payload))
    assert parsed.active.max_row == 4
    parsed.close()


def test_input_output_same_file_is_rejected(tmp_path):
    p = tmp_path / "a.xlsx"
    _create_source(p)
    with pytest.raises(ValueError, match="覆盖"):
        parse_xlsx(p, p)


def test_missing_column_and_sheet(tmp_path):
    a, b = tmp_path / "a.xlsx", tmp_path / "b.xlsx"
    _create_source(a)
    with pytest.raises(ValueError, match="找不到薪资列"):
        parse_xlsx(a, b, column="工资收入")
    with pytest.raises(ValueError, match="不存在"):
        parse_xlsx(a, b, sheet="不存在")


def test_formula_text_not_executable_in_output(tmp_path):
    source = tmp_path / "a.xlsx"
    _create_source(source)
    # 通过 data_only 读取源公式，无缓存时为空；不会复制可执行公式到输出。
    output = tmp_path / "b.xlsx"
    parse_xlsx(source, output)
    wb = load_workbook(output)
    for row in wb.active.iter_rows(min_row=2):
        assert not any(c.data_type == "f" for c in row)
    wb.close()


def test_duplicate_columns_rejected(tmp_path):
    src = tmp_path / "duplicate.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(["salary", "salary"])
    ws.append(["10K", "20K"])
    wb.save(src)
    with pytest.raises(ValueError, match="重复"):
        parse_xlsx(src, tmp_path / "out.xlsx")
