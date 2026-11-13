# 零基础开发、运行、测试与 GitHub 发布手册（Windows 10）

## 0. 目标

这是一个**可以安装的 Python 功能包**，不是一次性脚本。完成后展示：
1. 单条文本 `20-35K·14薪` 自动解析成金额、薪数和预计年薪。
2. 通过 CSV 批量处理十几条招聘薪资文本并在 Excel 中查看。
3. 自动测试全部通过，GitHub 上能看到每次推送的测试结果。

**技能学习顺序：** 字符串 `str` → 条件判断 `if` → 函数 `def` → 字典 `dict` → 正则 `re` → 文件 `csv` → 测试 `pytest` → Git/GitHub。

## 1. 准备环境

- Windows 10 或 11。
- Python 3.10+：在 PowerShell 或 CMD 输入 `python --version`，确认版本。
- VS Code：建议安装 Python 扩展（可选）。
- Git：`git --version`。若没有 Git，下载 [Git for Windows](https://git-scm.com/downloads/win)。
- 一个 GitHub 账号。

本手册默认项目放在 `D:\gongzuo\pythonxunlianying_2611\salary-dimensions`。实际路径不同就替换这一行。

## 2. 解压并安装

**不要把虚拟环境提交到 GitHub。**

1. 将压缩包解压到自己的工作目录，文件夹重命名为 `salary-dimensions`。
2. 在该文件夹空白处打开终端，或手动输入：

```powershell
cd D:\gongzuo\pythonxunlianying_2611\salary-dimensions
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

`venv` 是隔离依赖的虚拟环境；`-e` 是**可编辑安装**，修改源代码后通常不需要重新安装；`.[dev]` 同时装入 pytest。

本教程不用 `Activate.ps1`，因此一般不会遇到 PowerShell 脚本执行策略问题。

> 若 `python` 不是有效命令，试试 `py -3.10 --version`，并将上面的创建命令改为 `py -3.10 -m venv .venv`。若 pip 安装报网络错误，需要先确认能访问包索引，或配置可信的校园镜像；不要随意关闭安全验证。

## 3. 第一次运行

### 3.1 单条薪资

```powershell
.\.venv\Scripts\python.exe -m salary_dimensions "20-35K·14薪"
```

输出 JSON 字典，其中 `annual_min` 应为 `280000`，`annual_max` 应为 `490000`。

### 3.2 自己用函数

在项目根目录创建 `my_demo.py`：

```python
from salary_dimensions import parse_salary

result = parse_salary("月薪9000-15000元·13薪")
print("解析状态：", result["status"])
print("最低年薪：", result["annual_min"])
print("最高年薪：", result["annual_max"])
```

执行：

```powershell
.\.venv\Scripts\python.exe my_demo.py
```

### 3.3 批量 CSV

```powershell
.\.venv\Scripts\python.exe -m salary_dimensions --input examples/salaries.csv --output results.csv
```

用 Excel 打开 `results.csv`，查看新增的 `min_amount`、`max_amount`、`annual_min`、`annual_max`、`status` 列。

## 4. 按阶段学习和完善项目

| 阶段 | 要掌握的知识 | 具体改动 | 验收标准 |
|---|---|---|---|
| 第一阶段 | `if`、`str`、`dict`、函数 | 读懂 `parser.py` 的返回值和分支 | 单条薪资可解析 |
| 第二阶段 | `re` 正则、`Decimal` | 支持范围、不同单位及 13/14 薪 | 普通格式的预期金额正确 |
| 第三阶段 | 异常情况、返回状态 | 测试“面议”“以上”“提成”“错误区间” | 不伪造缺失字段 |
| 第四阶段 | `csv`、文件路径、列表 | 批量导入导出样例 | 输出结果能被 Excel 打开 |
| 第五阶段 | `pytest` | 增加 5 条自己收集的测试数据 | 所有测试通过 |
| 第六阶段 | `pyproject.toml`、Git | 可编辑安装、提交 GitHub | 其他人可运行并看到 Actions 通过 |

**建议自己动手完成的二次改动**：
- 增加 `100-200元/小时` 的测试。
- 让 `15K起` 和 `15K以上` 拥有一致的最低金额。
- 在文档中解释 `months_source=assumed` 是什么。
- 尝试添加 `2.5万/月` 的测试。
- 用真实但不包含隐私的公开招聘薪资文本补充样本。

不要直接修改测试期望值来让失败的测试通过；应检查解析逻辑是否合理。

## 5. 三类核心文件怎么读

### `src/salary_dimensions/parser.py`

负责把输入的薪资表达式处理为字典。初学者重点阅读：

- `_base()`：初始化字段与解析状态，防止遗漏键。
- `_to_yuan()`：把不同单位换算成人民币元。
- `parse_salary()`：主体流程（清洗 → 特殊情况 → 单位 → 数额 → 年薪）。
- `parse_many()`：列表批量解析；这是对 `parse_salary()` 的重复调用。

### `src/salary_dimensions/batch.py`

使用 Python 内置 `csv` 模块读写文件；核心方法 `parse_csv()`，每读一行就调用 `parse_salary()`，不需要 pandas。

### `tests/test_parser.py`

使用 `@pytest.mark.parametrize`：一条规则可以用多种输入验证。注意把预期结果与实际结果比较，而不是只检查程序有没有运行。

## 6. 测试命令

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

若希望看更详细的测试结果：

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

如果出现 `ModuleNotFoundError: No module named salary_dimensions`，请确认是在**项目根目录**，并已执行 `pip install -e ".[dev]"`。

## 7. 上传到 GitHub（第一次）

1. 在 GitHub 网站点击右上角 `+` → `New repository`。
2. 仓库名填 `salary-dimensions`，选择 `Public`（如果老师允许公开），简介填 `Chinese salary text parser in Python`。
3. **不要勾选**网页创建 README、.gitignore 或 LICENSE，本地项目已有这些文件。
4. 点击 `Create repository`，保留网页上的 HTTPS 地址。
5. 在项目根目录执行（将 `YOUR_USERNAME` 改成自己的 GitHub 用户名）：

```powershell
git --version
git init -b main
git add .
git status
git commit -m "feat: initial salary parser with tests"
git remote add origin https://github.com/YOUR_USERNAME/salary-dimensions.git
git remote -v
git push -u origin main
```

第一次 `git commit` 可能提示设置身份；按提示操作（下列姓名和邮箱需换成你自己的 Git 公开提交身份）：

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

然后重新运行 `git commit ...`。上传时如弹出浏览器，按 Git 凭据管理器提示登录；GitHub 账号密码通常不能直接作为 Git HTTPS 密码使用。

**安全检查：** 推送前核对 `git status`，确保 `.venv`、密钥、私人求职数据和账号凭据不会上传。

### GitHub 上验证

进入仓库 → `Actions` → `Python tests` → 打开最新的运行记录。每次 push 后会在 GitHub 的 Linux 环境用 Python 3.10 与 3.13 运行测试。看到绿色成功标记表示自动测试通过。

### 以后更新代码

```powershell
git add .
git commit -m "test: add more salary cases"
git push
```

不要反复执行 `git init` 或 `git remote add origin`。

## 8. 交作业准备

建议展示顺序（3～5分钟）：

1. 说明问题：同一薪资金额在不同网站有不同写法，不方便分析。
2. 现场演示 `20-35K·14薪`、`年薪30万`、`面议`、`15K以上`。
3. 打开 `examples/salaries.csv`，用命令导出 `results.csv`。
4. 展示 `pytest` 全部通过。
5. 打开 GitHub，讲解 README、代码结构与自动测试。
6. 强调限制：12薪只是默认估算、日薪不自动换算年薪、不支持复杂提成。

**验收清单：**
- [ ] 外部程序能执行 `from salary_dimensions import parse_salary`
- [ ] 解析 20-35K·14薪 得到 28万～49万预计税前年薪
- [ ] 面议不输出捏造金额
- [ ] 15K以上保留空白上限
- [ ] 批量文件可被 Excel 正常打开
- [ ] 自动测试本地通过
- [ ] GitHub 上传成功，Actions 通过
- [ ] README 说明约定与不支持场景
- [ ] `pyproject.toml`、`LICENSE` 中的姓名等占位符已检查和替换

## 9. 进阶功能规划

- **V0.2 Excel**：`openpyxl` 导入与导出 xlsx；不要求用户先转成 CSV。
- **V0.3 薪酬构成**：识别固定薪、奖金、提成等字段，但需明确计算约束。
- **V0.4 准确率评估**：收集一份 100 条人工标注集，统计正确解析、误判和未解析的比例。
- **V1.0 PyPI**：确认项目包名在 PyPI 可用，学习构建 wheel、TestPyPI 和 Trusted Publishing；不要随意复用已有包名。

常用官方文档：[Python Packaging User Guide](https://packaging.python.org/en/latest/) · [GitHub 上传本地仓库](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github) · [GitHub Python Actions](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)
