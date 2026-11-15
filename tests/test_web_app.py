from io import BytesIO
from openpyxl import Workbook, load_workbook
from salary_dimensions.web_app import (
    format_amount, format_annual_range, get_workbook_options,
    parse_uploaded_excel, period_label, status_label,
)

def _sample_xlsx():
    book = Workbook()
    ws = book.active
    ws.title = "招聘数据"
    ws.append(["job_id", "company", "salary"])
    ws.append(["001", "甲公司", "20-35K·14薪"])
    ws.append(["002", "乙公司", "薪资面议"])
    output = BytesIO()
    book.save(output)
    book.close()
    return output.getvalue()

def test_format_amount():
    assert format_amount(20000) == "¥20,000"
    assert format_amount(None) == "—"

def test_format_annual_range():
    assert format_annual_range(280000, 490000) == "¥280,000 ～ ¥490,000"
    assert format_annual_range(180000, None) == "≥ ¥180,000"
    assert format_annual_range(None, None) == "—"

def test_status_and_period_labels():
    assert status_label("parsed") == "解析成功"
    assert status_label("negotiable") == "薪资面议"
    assert period_label("month") == "月薪"
    assert period_label(None) == "未确定"

def test_get_workbook_options():
    assert get_workbook_options(_sample_xlsx())["招聘数据"] == [
        "job_id", "company", "salary"
    ]

def test_parse_uploaded_excel():
    payload, count = parse_uploaded_excel(
        _sample_xlsx(), column="salary", sheet="招聘数据"
    )
    assert count == 2
    book = load_workbook(BytesIO(payload), data_only=True)
    ws = book.active
    headers = [cell.value for cell in ws[1]]
    assert ws.cell(2, headers.index("annual_min") + 1).value == 280000
    assert ws.cell(3, headers.index("status") + 1).value == "negotiable"
    book.close()
