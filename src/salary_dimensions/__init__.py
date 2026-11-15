"""Salary Dimensions：中文招聘薪资文本结构化工具。"""

from .parser import parse_many, parse_salary

__version__ = "0.3.0"
__all__ = ["parse_salary", "parse_many"]
