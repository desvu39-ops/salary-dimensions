"""Salary Dimensions Streamlit 网页入口。"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
from salary_dimensions.excel import parse_xlsx_bytes
from salary_dimensions.parser import parse_salary

_STATUS = {
    "parsed": "解析成功", "negotiable": "薪资面议",
    "invalid": "输入无效", "unsupported": "暂不支持",
    "ambiguous": "信息不明确",
}
_PERIOD = {"month": "月薪", "year": "年薪", "day": "日薪", "hour": "时薪"}

def format_amount(value):
    """格式化人民币金额；None 显示为横线。"""
    return "—" if value is None else f"¥{value:,.0f}"

def format_annual_range(low, high):
    """格式化年薪区间，不猜测未知上限。"""
    if low is None and high is None:
        return "—"
    if low is not None and high is None:
        return f"≥ {format_amount(low)}"
    if low == high:
        return format_amount(low)
    return f"{format_amount(low)} ～ {format_amount(high)}"

def status_label(status):
    return _STATUS.get(status or "", "未知状态")

def period_label(period):
    return _PERIOD.get(period or "", "未确定")

def get_workbook_options(data: bytes) -> dict[str, list[str]]:
    """读取上传工作簿的工作表和首行列名。"""
    from openpyxl import load_workbook
    book = load_workbook(BytesIO(data), read_only=True, data_only=True)
    try:
        result = {}
        for ws in book.worksheets:
            row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), None)
            result[ws.title] = (
                [str(v).strip() if v is not None else "" for v in row]
                if row is not None else []
            )
        return result
    finally:
        book.close()

def parse_uploaded_excel(data: bytes, column="salary", sheet=None):
    """调用 v0.2 Excel 核心函数，返回新 Excel 字节和处理行数。"""
    return parse_xlsx_bytes(data, column=column, sheet=sheet)

def main():
    """启动 Streamlit 网页；Streamlit 仅在启动网页时导入。"""
    import streamlit as st

    st.set_page_config(page_title="Salary Dimensions", page_icon="💼", layout="wide")
    st.title("💼 Salary Dimensions")
    st.subheader("智能中文招聘薪资解析工作台")
    st.caption("输入一条薪资文本，或上传招聘 Excel，自动生成结构化薪资字段。")

    tab_one, tab_excel, tab_help = st.tabs(
        ["🔎 单条薪资解析", "📊 Excel 批量解析", "📖 使用说明"]
    )

    with tab_one:
        st.markdown("### 单条薪资解析")
        raw = st.text_input(
            "请输入招聘网站上的薪资文本",
            value="20-35K·14薪",
            placeholder="例如：20-35K·14薪、月薪8000-12000元、年薪30万",
        )
        if st.button("解析薪资", type="primary"):
            if not raw.strip():
                st.warning("请先输入薪资文本。")
            else:
                result = parse_salary(raw)
                status = result.get("status")
                if status == "parsed":
                    st.success(status_label(status))
                elif status in {"negotiable", "ambiguous", "unsupported"}:
                    st.info(status_label(status))
                else:
                    st.warning(status_label(status))
                c1, c2, c3 = st.columns(3)
                c1.metric("计薪周期", period_label(result.get("pay_period")))
                c2.metric("最低金额", format_amount(result.get("min_amount")))
                c3.metric("最高金额", format_amount(result.get("max_amount")))
                c4, c5, c6 = st.columns(3)
                c4.metric(
                    "薪数",
                    f'{result["salary_months"]} 薪'
                    if result.get("salary_months") is not None else "—",
                )
                c5.metric("预计年薪下限", format_amount(result.get("annual_min")))
                c6.metric("预计年薪上限", format_amount(result.get("annual_max")))
                if result.get("notes"):
                    st.caption(f"说明：{result['notes']}")
                with st.expander("查看完整解析字段"):
                    st.json(result)
        with st.expander("试试这些输入"):
            st.code("20-35K·14薪\n月薪8000-12000元\n年薪30万\n300-500元/天\n15K以上\n薪资面议")

    with tab_excel:
        st.markdown("### Excel 批量解析")
        st.write("上传 .xlsx 文件，选择工作表和薪资列，生成可下载的新 Excel。")
        uploaded = st.file_uploader("选择招聘 Excel 文件", type=["xlsx"])
        if uploaded is not None:
            data = uploaded.getvalue()
            try:
                options = get_workbook_options(data)
            except Exception as exc:
                st.error(f"无法读取 Excel：{exc}")
            else:
                sheets = list(options)
                if not sheets:
                    st.error("工作簿中没有可读取的工作表。")
                else:
                    sheet = st.selectbox("选择工作表", sheets)
                    headers = [h for h in options[sheet] if h]
                    if not headers:
                        st.error("所选工作表第一行没有有效列名。")
                    else:
                        default = headers.index("salary") if "salary" in headers else 0
                        column = st.selectbox("选择薪资所在列", headers, index=default)
                        if st.button("开始解析并生成 Excel", type="primary"):
                            try:
                                output, count = parse_uploaded_excel(data, column, sheet)
                            except Exception as exc:
                                st.error(f"Excel 解析失败：{exc}")
                            else:
                                st.success(f"处理完成，共解析 {count} 条数据。")
                                name = f"{Path(uploaded.name).stem}_parsed.xlsx"
                                st.download_button(
                                    "下载解析结果 Excel",
                                    data=output,
                                    file_name=name,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    type="primary",
                                )
                                st.info(
                                    "输出只包含所选工作表的数据值和解析字段；"
                                    "不覆盖原文件，也不保留原表样式、图表、图片和公式。"
                                )

    with tab_help:
        st.markdown("### 支持的薪资表达式")
        st.markdown(
            "| 输入示例 | 解析方式 |\n|---|---|\n"
            "| `20-35K·14薪` | 月薪 20,000～35,000 元，14 薪 |\n"
            "| `月薪8000-12000元` | 月薪区间 |\n"
            "| `年薪30万` | 年薪 300,000 元 |\n"
            "| `300-500元/天` | 日薪，不自动折算年薪 |\n"
            "| `15K以上` | 只记录下限 |\n"
            "| `薪资面议` | 标记为 negotiable |"
        )
        st.warning(
            "没有明确薪数的月薪按 12 薪估算；日薪/时薪不自动折算成年薪。"
            "提成、奖金、股权等复杂薪酬暂不自动估算。"
        )
        st.caption("网页调用原有 Python 解析函数。本地运行时，文件在本机应用进程中处理。")

if __name__ == "__main__":
    main()
