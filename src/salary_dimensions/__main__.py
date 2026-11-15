"""在终端运行：python -m salary_dimensions ..."""

import argparse
import json
from pathlib import Path
from .batch import parse_csv
from .parser import parse_salary


def main() -> None:
    parser = argparse.ArgumentParser(description="中文招聘薪资结构化解析工具")
    parser.add_argument("salary", nargs="?", help="如：20-35K·14薪")
    parser.add_argument("--input", help="CSV/XLSX 输入路径")
    parser.add_argument("--output", help="CSV/XLSX 输出路径")
    parser.add_argument("--column", default="salary", help="薪资字段列名，默认 salary")
    parser.add_argument("--sheet", help="Excel 工作表名，默认当前活动工作表")
    args = parser.parse_args()
    if args.input:
        if args.salary or not args.output:
            parser.error("批量模式需要 --input 和 --output，不能同时输入单条薪资")
        input_ext = Path(args.input).suffix.lower()
        output_ext = Path(args.output).suffix.lower()
        if input_ext != output_ext or input_ext not in (".csv", ".xlsx"):
            parser.error("输入和输出文件必须使用相同格式：.csv 或 .xlsx")
        if input_ext == ".xlsx":
            from .excel import parse_xlsx
            count = parse_xlsx(args.input, args.output, args.column, args.sheet)
        else:
            if args.sheet is not None:
                parser.error("--sheet 仅适用于 .xlsx 文件")
            count = parse_csv(args.input, args.output, args.column)
        print(f"已处理 {count} 条，输出：{args.output}")
    elif args.salary:
        print(json.dumps(parse_salary(args.salary), ensure_ascii=False, indent=2))
    else:
        parser.error("请提供单条薪资，或用 --input 和 --output 批量处理")


if __name__ == "__main__":
    main()
