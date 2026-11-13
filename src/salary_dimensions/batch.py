"""批量读取/输出 CSV。"""

from __future__ import annotations

import csv
from pathlib import Path
from .parser import parse_salary


def parse_csv(input_path: str | Path, output_path: str | Path, column: str = "salary") -> int:
    """将 CSV 中的薪资字段展开成多列，保留原列；返回处理行数。"""
    with open(input_path, "r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None or column not in reader.fieldnames:
            raise ValueError(f"输入 CSV 必须包含 {column!r} 列")
        original_columns = list(reader.fieldnames)
        # 不调用 pandas，读取一行处理一行，适合更大的文件。
        extra_columns = [k for k in parse_salary("").keys() if k != "raw"]
        if any(k in original_columns for k in extra_columns):
            raise ValueError("输入 CSV 已有解析结果同名列，请换用原始文件")
        count = 0
        with open(output_path, "w", encoding="utf-8-sig", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=original_columns + extra_columns)
            writer.writeheader()
            for row in reader:
                parsed = parse_salary(row[column] or "")
                row.update({k: v for k, v in parsed.items() if k != "raw"})
                writer.writerow(row)
                count += 1
    return count
