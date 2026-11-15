# Salary Dimensions — 智能中文薪资解析工具包（v0.3 Web）

把招聘信息中的 `20-35K·14薪`、`年薪30万`、`300-500元/天` 等非标准薪资表达式转换成**可分析的结构化数据**。

**当前版本：v0.3.0** · **Python 3.10+** · 核心解析仅依赖 Python 标准库；Excel 和网页使用可选依赖 `openpyxl`、`streamlit`。

## ✨ 功能一览

| 功能 | 说明 | 版本 |
| --- | --- | --- |
| 薪资文本解析 | 识别人民币金额、范围、月薪/年薪/日薪/时薪、13/14 薪 | v0.1 |
| 可靠的异常标记 | 识别面议、歧义、无效区间、不支持的复杂薪酬 | v0.1 |
| Python API 与命令行 | `parse_salary()` / `parse_many()` / `python -m salary_dimensions` | v0.1 |
| CSV 批处理 | 读取薪资列，保留原列并追加解析字段 | v0.1 |
| Excel 导入导出 | 解析 `.xlsx`，选择工作表和薪资列，导出新文件 | v0.2 |
| **Streamlit 网页** | **输入薪资、查看结果、上传并下载 Excel** | **v0.3** |
| 税后收入估算 | 尚未实现，计划在后续版本加入 | 规划中 |

### 解析示例

| 输入文本 | 结果摘要 |
| --- | --- |
| `20-35K·14薪` | 月薪 20,000–35,000 元；14 薪；预计税前年薪 280,000–490,000 元 |
| `月薪8000-12000元` | 月薪 8,000–12,000 元；默认按 12 薪估算 |
| `年薪30万` | 年薪 300,000 元 |
| `300-500元/天` | 日薪 300–500 元；不计算年薪 |
| `15K以上` | 仅有月薪下限 15,000 元；不猜测上限 |
| `薪资面议` | `status = negotiable` |
| `20K+提成` | `status = unsupported` |
| `25K-20K` | `status = invalid` |
| `30万` | `status = ambiguous`（计薪周期不明确） |

> **计算约定：** 没有明确薪数的月薪按 **12 薪估算**，并标记 `months_source = assumed`；结果是按输入规则推算的**税前估算金额**，并非对招聘报价的真实性核验。

## 🚀 安装（Windows CMD / PowerShell）

如果已将项目克隆或下载到本机，请进入**含有 `pyproject.toml` 的项目根目录**：

```cmd
cd /d D:\gongzuo\pythonxunlianying_2611\salary-dimensions
```

第一次安装时创建虚拟环境：

```cmd
python -m venv .venv
```

安装完整的 v0.3 网页和开发依赖：

```cmd
.\.venv\Scripts\python.exe -m pip install -e ".[dev,web]"
```

不同使用场景的可选依赖如下（表中的命令省略了解释器前缀）：

| 命令 | 用途 |
| --- | --- |
| `pip install -e .` | 仅核心解析和 CSV |
| `pip install -e ".[excel]"` | 核心解析 + Excel |
| `pip install -e ".[web]"` | 核心解析 + Excel + Streamlit 网页 |
| `pip install -e ".[dev,web]"` | 以上功能 + pytest 测试工具 |

推荐在 Windows 上始终使用 `\.venv\Scripts\python.exe -m pip`（命令开头还需加 `.`）运行安装，避免把依赖安装到错误的 Python 环境。`-e` 表示可编辑安装，方便修改本地源码。

## 🌐 v0.3：启动网页

在项目根目录执行：

```cmd
.\.venv\Scripts\python.exe -m streamlit run src\salary_dimensions\web_app.py
```

浏览器打开 **http://localhost:8501**（如果端口已被占用，以终端实际显示的地址为准）。

网页包含三个标签页：

1. **单条薪资解析**：输入 `20-35K·14薪`，查看计薪周期、金额上下限、薪数和预计年薪，可展开查看完整字段。
2. **Excel 批量解析**：上传 `.xlsx` 文件，选择工作表和薪资列，点击解析后下载新 Excel。
3. **使用说明**：查看常见薪资格式、计算规则及处理边界。

网页直接复用 `parse_salary()` 和 `parse_xlsx_bytes()`，**没有另写一套薪资算法**。

**注意：** 当前是运行在自己电脑上的**本地 Web 应用**，还没有部署到公共互联网。停止运行 Streamlit 的命令行程序（`Ctrl+C`）后，网页服务也会停止。详见 [`docs/WEB_GUIDE.md`](docs/WEB_GUIDE.md)。

## 🐍 Python API

```python
from salary_dimensions import parse_salary, parse_many

row = parse_salary("20-35K·14薪")
print(row["min_amount"])     # 20000
print(row["max_amount"])     # 35000
print(row["salary_months"])  # 14
print(row["annual_min"])     # 280000
print(row["annual_max"])     # 490000

rows = parse_many(["年薪30万", "15K以上", "薪资面议"])
for item in rows:
    print(item["raw"], item["status"])
```

`parse_salary("20-35K·14薪")` 返回的主要字段示例：

```python
{
    "raw": "20-35K·14薪",
    "status": "parsed",
    "pay_period": "month",
    "min_amount": 20000,
    "max_amount": 35000,
    "currency": "CNY",
    "salary_months": 14,
    "months_source": "explicit",
    "annual_min": 280000,
    "annual_max": 490000,
    "notes": "按常见招聘表达习惯推断为月薪，请人工确认"
}
```

## 🖥️ 命令行、CSV 和 Excel

**单条薪资：**

```cmd
.\.venv\Scripts\python.exe -m salary_dimensions "20-35K·14薪"
```

**CSV 批量解析：**

```cmd
.\.venv\Scripts\python.exe -m salary_dimensions --input examples\salaries.csv --output results.csv
```

**Excel 批量解析：**

```cmd
.\.venv\Scripts\python.exe -m salary_dimensions --input examples\salaries.xlsx --output parsed_salaries.xlsx --sheet 招聘数据 --column salary
```

| 参数 | 含义 |
| --- | --- |
| `--input` | 输入 `.csv` 或 `.xlsx` 路径 |
| `--output` | 输出路径；要求与输入扩展名一致 |
| `--sheet` | 要解析的 Excel 工作表；CSV 不使用该选项 |
| `--column` | 薪资列名，默认 `salary` |

**Excel 导出限制：** 输出仅包含选中工作表的数据值和新增解析字段，不会覆盖输入文件；**不保留**原工作簿的样式、图片、图表、公式及其他工作表。

## 📋 输出字段

| 字段 | 含义 |
| --- | --- |
| `raw` | 原始输入文本（单条 Python API 输出中包含） |
| `status` | `parsed` / `negotiable` / `invalid` / `unsupported` / `ambiguous` |
| `pay_period` | `month` / `year` / `day` / `hour` / `None` |
| `min_amount`、`max_amount` | 当前计薪周期的最低、最高金额（人民币元） |
| `currency` | 当前仅支持 `CNY` |
| `salary_months` | 月薪对应的薪数；未明确时按 12 薪估算 |
| `months_source` | `explicit` 表示明确指定；`assumed` 表示估算 |
| `annual_min`、`annual_max` | 预计税前年薪的上下限 |
| `notes` | 假设、歧义、错误及其他说明 |

### 重要边界

- `15K以上` 只给下限，不为其虚构最高金额。
- 日薪/时薪缺少工作天数或工时，不直接折成年薪。
- 提成、奖金、绩效和股权等复杂薪酬暂标记为 `unsupported`。
- `30万` 等缺少计薪周期的文本可能返回 `ambiguous`，需要人工确认。
- 当前**不提供税后收入或个税估算**；将在 v0.4 规划实现。
- 工具处理的是**单条薪资表达式**，并非任意招聘长段落的完整 NLP 信息抽取。

## 📁 项目结构

```text
salary-dimensions/
├── src/salary_dimensions/
│   ├── __init__.py       # 公共 API、版本号
│   ├── parser.py         # 核心解析、换算和状态判断
│   ├── batch.py          # CSV 批处理
│   ├── excel.py          # Excel 批处理（v0.2）
│   ├── web_app.py        # Streamlit 网页（v0.3）
│   └── __main__.py       # 命令行入口
├── tests/
│   ├── test_parser.py
│   ├── test_batch.py
│   ├── test_excel.py
│   └── test_web_app.py
├── examples/
│   ├── salaries.csv
│   └── salaries.xlsx
├── docs/
│   ├── BEGINNER_GUIDE.md
│   ├── UPGRADE_GUIDE.md
│   └── WEB_GUIDE.md
├── .github/workflows/tests.yml
├── pyproject.toml
├── LICENSE
└── README.md
```

## ✅ 自动测试与 GitHub

在项目根目录运行：

```cmd
.\.venv\Scripts\python.exe -m pytest -q
```

v0.3 在 v0.2 的解析、CSV、Excel 测试基础上新增网页辅助函数测试。自动测试不能完全替代浏览器实际操作，网页上传、下载功能也应手动验收。

GitHub Actions 配置在 [`.github/workflows/tests.yml`](.github/workflows/tests.yml)，可在仓库 **Actions** 页面查看运行结果。

## 📌 版本记录

| 版本 | 功能 |
| --- | --- |
| **v0.1** | 单条薪资解析、Python API、CSV、自动测试 |
| **v0.2** | Excel 读取/导出、工作表和薪资列选择 |
| **v0.3（当前）** | Streamlit 网页、单条解析展示、Excel 上传下载 |
| **v0.4（计划）** | 中国大陆税后收入估算，逐步增加个人社保、公积金及个税参数 |

## 📄 许可证与反馈

采用 MIT 许可证，详见 [`LICENSE`](LICENSE)。欢迎通过 [GitHub Issues](https://github.com/desvu39-ops/salary-dimensions/issues) 提交**脱敏后**的解析样例或建议，不要上传包含个人信息的原始招聘数据。

项目地址：https://github.com/desvu39-ops/salary-dimensions

本项目为 Python 学习实践，重点展示**字符串处理、正则表达式、函数封装、文件读写、自动测试及网页交互**。
