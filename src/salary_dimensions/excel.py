"""可选的 .xlsx 批量解析模块（需要 openpyxl）。

读取原始数据，生成新工作簿；不覆盖原文件，不保留原始格式/公式。
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from .parser import parse_salary


def _load_workbook(source: str | Path | BinaryIO):
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise RuntimeError('Excel 功能需要 openpyxl：python -m pip install -e ".[excel]"') from exc
    return load_workbook(source, read_only=True, data_only=True)


def _parse_workbook(input_book, column: str, sheet: str | None):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    if sheet is None:
        source = input_book.active
    else:
        if sheet not in input_book.sheetnames:
            raise ValueError(f"工作表 {sheet!r} 不存在；可选：{', '.join(input_book.sheetnames)}")
        source = input_book[sheet]

    rows = source.iter_rows(values_only=True)
    raw_head = next(rows, None)
    if raw_head is None:
        raise ValueError("输入工作表为空，至少需要一行列名")
    headers = [str(value).strip() if value is not None else "" for value in raw_head]
    if not all(headers) or len(set(headers)) != len(headers):
        raise ValueError("第一行列名不得为空或重复")
    if column not in headers:
        raise ValueError(f"找不到薪资列 {column!r}；现有列：{', '.join(headers)}")

    added = [name for name in parse_salary("") if name != "raw"]
    collisions = set(headers).intersection(added)
    if collisions:
        raise ValueError(f"输入表已经含有解析结果列 {', '.join(sorted(collisions))}，请使用未解析的原始表")

    result_book = Workbook()
    target = result_book.active
    target.title = "薪资解析结果"
    target.append(headers + added)
    salary_index = headers.index(column)
    count = 0
    for raw_values in rows:
        values = list(raw_values[:len(headers)])
        values += [None] * (len(headers) - len(values))
        if all(value is None or value == "" for value in values):
            continue
        salary = values[salary_index]
        parsed = parse_salary("" if salary is None else str(salary))
        target.append(values + [parsed[name] for name in added])
        # 用户提供的文本可能以 '=' 开头：确保它是普通文本，不当作公式执行。
        for cell in target[target.max_row]:
            if isinstance(cell.value, str) and cell.value.startswith("="):
                cell.data_type = "s"
        count += 1

    # 只做基础表格美化，避免引入过多依赖。
    for cell in target[1]:
        cell.fill = PatternFill("solid", fgColor="24466C")
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(wrap_text=True)
    target.freeze_panes = "A2"
    target.auto_filter.ref = target.dimensions
    for index, name in enumerate(headers + added, 1):
        target.column_dimensions[get_column_letter(index)].width = min(max(len(name) + 4, 14), 28)
        if name in {"min_amount", "max_amount", "annual_min", "annual_max"}:
            for row in target.iter_rows(min_row=2, min_col=index, max_col=index):
                row[0].number_format = '#,##0'
    return result_book, count


def parse_xlsx(
    input_path: str | Path,
    output_path: str | Path,
    column: str = "salary",
    sheet: str | None = None,
) -> int:
    """解析 Excel 单个工作表并保存为新的 xlsx；返回有效数据行数。

    只拷贝值；不会保留源表样式、图表、图片或公式。
    """
    source, dest = Path(input_path), Path(output_path)
    if source.suffix.lower() != ".xlsx" or dest.suffix.lower() != ".xlsx":
        raise ValueError("输入和输出都必须是 .xlsx 文件")
    if source.resolve() == dest.resolve():
        raise ValueError("输出路径不能与输入路径相同，以免覆盖原始数据")
    book = _load_workbook(source)
    try:
        parsed, count = _parse_workbook(book, column, sheet)
        parsed.save(dest)
        return count
    finally:
        book.close()


def parse_xlsx_bytes(data: bytes, column: str = "salary", sheet: str | None = None) -> tuple[bytes, int]:
    """网页上传场景：Excel bytes -> (新 Excel bytes, 处理行数)。"""
    book = _load_workbook(BytesIO(data))
    try:
        parsed, count = _parse_workbook(book, column, sheet)
        output = BytesIO()
        parsed.save(output)
        return output.getvalue(), count
    finally:
        book.close()
