"""在终端运行：python -m salary_dimensions ..."""

import argparse
import json
from .batch import parse_csv
from .parser import parse_salary


def main() -> None:
    parser = argparse.ArgumentParser(description="中文招聘薪资结构化解析工具")
    parser.add_argument("salary", nargs="?", help="如：20-35K·14薪")
    parser.add_argument("--input", help="CSV输入路径")
    parser.add_argument("--output", help="CSV输出路径")
    parser.add_argument("--column", default="salary", help="薪资字段列名，默认salary")
    args = parser.parse_args()
    if args.input:
        if args.salary or not args.output:
            parser.error("批量模式需要 --input 和 --output，不能同时输入单条薪资")
        count = parse_csv(args.input, args.output, args.column)
        print(f"已处理 {count} 条，输出：{args.output}")
    elif args.salary:
        print(json.dumps(parse_salary(args.salary), ensure_ascii=False, indent=2))
    else:
        parser.error("请提供单条薪资，或用 --input 和 --output 批量处理")


if __name__ == "__main__":
    main()
