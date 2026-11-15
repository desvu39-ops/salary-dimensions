# Salary Dimensions — 智能中文薪资解析工具包（v0.2 Excel）

将招聘网站里的非标准薪资文本转换成便于表格、数据库和分析使用的字段。**Python 3.10+，核心功能仅使用标准库**。

## 安装（Windows PowerShell 或 CMD）

```powershell
cd D:\gongzuo\pythonxunlianying_2611\salary-dimensions
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

如果在其他目录，请将第一行改成自己的实际路径；无需激活虚拟环境。

## 快速体验

```powershell
.\.venv\Scripts\python.exe -m salary_dimensions "20-35K·14薪"
```

或在 Python 中导入：

```python
from salary_dimensions import parse_salary, parse_many

one = parse_salary("20-35K·14薪")
print(one["annual_min"], one["annual_max"])  # 280000 490000

many = parse_many(["月薪8000-12000元", "年薪30万", "薪资面议"])
for row in many:
    print(row["raw"], row["status"], row["pay_period"])
```

### 批量转换 CSV

```powershell
.\.venv\Scripts\python.exe -m salary_dimensions --input examples/salaries.csv --output results.csv
```

在 Excel 中打开 `results.csv` 即可查看结果。CSV 使用 `utf-8-sig`，便于 Windows Excel 阅读中文。

## 功能表

| 输入文本 | 结果摘要 |
|---|---|
| `20-35K·14薪` | 月薪 20,000～35,000 元；14薪；年薪 280,000～490,000 元 |
| `月薪8000-12000元` | 月薪 8,000～12,000 元；缺少薪数时按 12薪估算 |
| `年薪30万` | 年薪 300,000 元 |
| `300-500元/天` | 日薪 300～500 元；不自动折成年薪 |
| `15K以上` | 月薪最低 15,000 元；最高金额未知 |
| `薪资面议` | status = negotiable |
| `20K+提成` | status = unsupported（复杂薪酬结构） |
| `25K-20K` | status = invalid（金额区间错误） |
| `30万` | status = ambiguous（计薪周期不明确） |

### 输出字段

| 字段 | 解释 |
|---|---|
| `raw` | 原始薪资字符串 |
| `status` | `parsed`、`negotiable`、`invalid`、`unsupported`、`ambiguous` |
| `pay_period` | `month` / `year` / `day` / `hour` / `None` |
| `min_amount` | 当前计薪周期内的最低金额（人民币元） |
| `max_amount` | 当前计薪周期内的最高金额；下限型薪资为空 |
| `currency` | `CNY`（本工具第一版只处理人民币） |
| `salary_months` | 适用于月薪；缺省时按12薪估算 |
| `months_source` | `explicit`（明确指定）或 `assumed`（假设） |
| `annual_min`、`annual_max` | 预计税前年薪的上下界；日薪/时薪留空 |
| `notes` | 推断和异常情况的提示 |

**重要边界：**
- 没有明确薪数的月薪以 **12薪作估算假设**，并标为 `assumed`；不是保证薪资。
- `15K以上` 只给出下限，**不会伪造上限**。
- `300元/天`、`时薪50元` 不计算年薪，因为缺少工作天数/工时。
- `20K+提成`、奖金、股权等复杂薪酬目前标为 `unsupported`。
- 仅处理**单条薪资表达式**，尚不对完整招聘段落做抽取，也不支持美元和税后工资。
- 当没有计薪单位且推断依据不足（如 `30万`），状态为 `ambiguous`，待人工确认。
- 金额是按输入字符串和规则的计算结果，不是招聘真实报价核验。

## 目录说明

```text
salary-dimensions/
├─ src/salary_dimensions/
│  ├─ __init__.py     # 供外部 import 的接口
│  ├─ parser.py       # 核心：清洗、解析、换算、异常状态
│  ├─ batch.py        # 批量读写 CSV
│  └─ __main__.py     # 命令行入口
├─ examples/salaries.csv   # 12条演示输入
├─ examples/output_sample.csv  # 示例输出
├─ tests/
│  ├─ test_parser.py  # 解析逻辑测试
│  └─ test_batch.py   # 批处理测试
├─ docs/BEGINNER_GUIDE.md  # 零基础操作说明、开发阶段与 GitHub 发布
├─ .github/workflows/tests.yml  # GitHub Actions 自动测试
├─ pyproject.toml      # 项目打包信息
├─ .gitignore          # 排除本地环境和生成结果
├─ LICENSE             # MIT 授权（发布前修改姓名）
└─ README.md
```

## 运行测试

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## GitHub 发布

请阅读 [零基础开发和发布手册](docs/BEGINNER_GUIDE.md)。本项目已经包含 `.github/workflows/tests.yml`；上传到 GitHub 后，Push 和 Pull Request 可自动测试 Python 3.10 与 3.13。

## 后续扩展

- V0.2：Excel 读取/写入（`openpyxl`），命令行参数自定义默认薪数。
- V0.3：识别整段招聘文字中的薪资信息、提成的单独字段、不同币种；评估覆盖率和误判率。
- V1.0：文档、测试覆盖率、稳定接口、可选 PyPI 发布。

欢迎通过 GitHub Issues 提交无法解析的薪资表达式（请勿包含个人信息）。


## v0.2：直接读取 Excel

```cmd
.\.venv\Scripts\python.exe -m salary_dimensions --input examples\salaries.xlsx --output parsed_salaries.xlsx --sheet 招聘数据 --column salary
```

使用 `openpyxl`，依赖已包含在 `.[dev]` 中；普通用户可以单独安装 `.[excel]`。输出表只包含选中工作表的数据值和解析字段，**不保留原始单元格样式/图表/公式**，且不允许覆盖输入文件。
详细说明见 [升级操作手册](docs/UPGRADE_GUIDE.md)。
