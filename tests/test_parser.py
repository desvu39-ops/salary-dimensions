"""pytest 自动测试：普通、区间、边界与不支持输入。"""

import pytest
from salary_dimensions import parse_many, parse_salary


@pytest.mark.parametrize("raw,period,low,high,annual_low,annual_high", [
    ("20-35K·14薪", "month", 20000, 35000, 280000, 490000),
    ("月薪8000-12000元", "month", 8000, 12000, 96000, 144000),
    ("年薪30万", "year", 300000, 300000, 300000, 300000),
    ("300-500元/天", "day", 300, 500, None, None),
    ("15K以上", "month", 15000, None, 180000, None),
    ("1.2-1.8万/月", "month", 12000, 18000, 144000, 216000),
    ("3.5K/月", "month", 3500, 3500, 42000, 42000),
    ("10K~20K·13薪", "month", 10000, 20000, 130000, 260000),
    ("１０Ｋ－２０Ｋ／月", "month", 10000, 20000, 120000, 240000),
    ("时薪50元", "hour", 50, 50, None, None),
    ("8千-1万元/月", "month", 8000, 10000, 96000, 120000),
    ("20k-30k*14薪", "month", 20000, 30000, 280000, 420000),
])
def test_success(raw, period, low, high, annual_low, annual_high):
    row = parse_salary(raw)
    assert row["status"] == "parsed"
    assert row["pay_period"] == period
    assert (row["min_amount"], row["max_amount"]) == (low, high)
    assert (row["annual_min"], row["annual_max"]) == (annual_low, annual_high)


def test_month_source():
    assert parse_salary("20-35K·14薪")["months_source"] == "explicit"
    assert parse_salary("10K/月")["months_source"] == "assumed"


@pytest.mark.parametrize("raw,status", [
    ("面议", "negotiable"),
    ("薪资面议", "negotiable"),
    ("", "invalid"),
    ("25K-20K", "invalid"),
    ("10K-20K·30薪", "invalid"),
    ("月薪20K/年", "invalid"),
    ("20K+提成", "unsupported"),
    ("10K-20K·13-15薪", "unsupported"),
    ("500元/周", "unsupported"),
    ("每月一万元", "unsupported"),
    ("30万", "ambiguous"),
    ("1234", "ambiguous"),
    ("10K-20K以上", "unsupported"),
])
def test_nonstandard(raw, status):
    assert parse_salary(raw)["status"] == status


def test_batch_in_memory():
    results = parse_many(["10K/月", "年薪30万"])
    assert [r["pay_period"] for r in results] == ["month", "year"]


def test_no_double_income_for_day():
    row = parse_salary("300元/天")
    assert row["salary_months"] is None and row["annual_min"] is None


def test_wrong_python_type():
    with pytest.raises(TypeError):
        parse_salary(20000)
