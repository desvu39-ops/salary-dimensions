"""把简单的中文招聘薪资表达式解析为结构化字段。"""

from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, ROUND_HALF_UP

_AMOUNT_PATTERN = re.compile(
    r"^(?P<low>\d+(?:\.\d+)?)"
    r"(?P<low_unit>万元|千元|万|千|元|[kKwW])?"
    r"(?:(?:-|~|至|到)(?P<high>\d+(?:\.\d+)?)"
    r"(?P<high_unit>万元|千元|万|千|元|[kKwW])?)?$"
)
_MULTIPLIERS = {
    "元": Decimal(1),
    "k": Decimal(1000),
    "千": Decimal(1000),
    "千元": Decimal(1000),
    "w": Decimal(10000),
    "万": Decimal(10000),
    "万元": Decimal(10000),
}
_PERIOD_SUFFIXES = [
    ("/小时", "hour"), ("每小时", "hour"), ("/时", "hour"), ("时薪", "hour"),
    ("/天", "day"), ("/日", "day"), ("每天", "day"), ("日薪", "day"),
    ("/月", "month"), ("每月", "month"), ("月薪", "month"),
    ("/年", "year"), ("每年", "year"), ("年薪", "year"),
]
_PREFIXES = [
    ("月薪", "month"), ("年薪", "year"),
    ("日薪", "day"), ("时薪", "hour"),
    ("薪资", None), ("薪酬", None), ("工资", None),
]


def _base(raw: str, status: str, notes: str) -> dict:
    return {
        "raw": raw,
        "status": status,
        "pay_period": None,
        "min_amount": None,
        "max_amount": None,
        "currency": "CNY",
        "salary_months": None,
        "months_source": None,
        "annual_min": None,
        "annual_max": None,
        "notes": notes,
    }


def _to_yuan(number: str, unit: str) -> int:
    value = Decimal(number) * _MULTIPLIERS[unit.lower()]
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def parse_salary(raw: str) -> dict:
    """解析一条薪资表达式，不猜测缺失上限，不把日薪直接折算成年薪。

    已支持：10-20K、20-35K·14薪、年薪30万、300元/天、15K以上、面议。
    仅面向人民币和简单的固定薪资；复杂提成/奖金规则返回 unsupported。
    """
    if not isinstance(raw, str):
        raise TypeError("薪资输入必须是字符串，例如 '20-35K·14薪'")
    original = raw
    text = unicodedata.normalize("NFKC", raw).strip()
    text = re.sub(r"\s+", "", text)
    text = text.replace("－", "-").replace("—", "-").replace("–", "-").replace("～", "~")
    if not text:
        return _base(original, "invalid", "输入为空")
    if "面议" in text:
        return _base(original, "negotiable", "薪资面议，无确定金额")
    if any(word in text for word in ("提成", "绩效", "期权", "奖金", "股票", "股权", "补贴")):
        return _base(original, "unsupported", "含浮动薪酬或额外待遇，暂不自动估算")

    # 删除不会影响数额的注释性前缀；税前/税后不等于计算净收入。
    text = text.replace("税前", "")
    if "税后" in text:
        return _base(original, "unsupported", "税后工资涉及额外计算规则，暂不支持")
    prefix_period = None
    for prefix, period in _PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix):].lstrip(":：")
            prefix_period = period
            break

    # 先去掉“·14薪”等独立薪数说明。
    months = None
    months_match = re.search(r"[·*]?(\d{2})薪$", text)
    if months_match:
        months = int(months_match.group(1))
        text = text[:months_match.start()]
        if not 12 <= months <= 24:
            return _base(original, "invalid", "薪数应在12到24之间")
    elif "薪" in text:
        return _base(original, "unsupported", "无法识别薪数表达式")

    # 文本尾部的“以上”“起”“+”表示只有下限。
    lower_only = False
    for suffix in ("以上", "起", "+"):
        if text.endswith(suffix):
            text = text[:-len(suffix)]
            lower_only = True
            break

    suffix_period = None
    for suffix, period in _PERIOD_SUFFIXES:
        if text.endswith(suffix):
            text = text[:-len(suffix)]
            suffix_period = period
            break

    # 允许“15K/月以上”的顺序；不允许双重下限标记。
    if not lower_only:
        for suffix in ("以上", "起", "+"):
            if text.endswith(suffix):
                text = text[:-len(suffix)]
                lower_only = True
                break
    if prefix_period and suffix_period and prefix_period != suffix_period:
        return _base(original, "invalid", "前缀和后缀的计薪周期冲突")

    matched = _AMOUNT_PATTERN.fullmatch(text)
    if not matched:
        return _base(original, "unsupported", "未识别的薪资格式；请使用数字、金额单位及计薪周期")
    low_str, high_str = matched.group("low", "high")
    low_unit, high_unit = matched.group("low_unit", "high_unit")
    if high_str is not None and lower_only:
        return _base(original, "unsupported", "区间和“以上”同时出现，含义不明确")
    if not low_unit and not high_unit:
        # 仅当计薪周期明示且数值以元计时，才可安全按“元”理解。
        if not (prefix_period or suffix_period):
            return _base(original, "ambiguous", "缺少金额单位和计薪周期")
        low_unit = high_unit = "元"
    elif not low_unit:
        low_unit = high_unit
    elif not high_unit:
        high_unit = low_unit

    low = _to_yuan(low_str, low_unit)
    high = _to_yuan(high_str, high_unit) if high_str is not None else None
    if low <= 0 or (high is not None and (high <= 0 or high < low)):
        return _base(original, "invalid", "金额必须为正且最高金额不能低于最低金额")

    period = prefix_period or suffix_period
    notes = []
    if period is None and (months is not None or low_unit.lower() == "k"):
        period = "month"
        notes.append("按常见招聘表达习惯推断为月薪，请人工确认")
    if period is None:
        result = _base(original, "ambiguous", "无法确定计薪周期；请标明/月、/年或/天")
        result["min_amount"] = low
        result["max_amount"] = high if high is not None else (None if lower_only else low)
        return result
    if months is not None and period != "month":
        return _base(original, "invalid", "12薪/14薪仅允许与月薪搭配")

    result = _base(original, "parsed", "")
    result["pay_period"] = period
    result["min_amount"] = low
    result["max_amount"] = high if high is not None else (None if lower_only else low)
    if lower_only:
        notes.append("仅有薪资下限，不能推断最高金额")
    if period == "month":
        result["salary_months"] = months if months is not None else 12
        result["months_source"] = "explicit" if months is not None else "assumed"
        result["annual_min"] = low * result["salary_months"]
        if result["max_amount"] is not None:
            result["annual_max"] = result["max_amount"] * result["salary_months"]
        if months is None:
            notes.append("按12薪估算年薪，不代表实际发放薪数")
    elif period == "year":
        result["annual_min"] = low
        result["annual_max"] = result["max_amount"]
    else:
        notes.append("日薪/时薪缺少工作天数或工时，不计算年薪")
    result["notes"] = "；".join(notes)
    return result


def parse_many(salaries: list[str]) -> list[dict]:
    """逐条解析，返回字典列表。"""
    return [parse_salary(item) for item in salaries]
