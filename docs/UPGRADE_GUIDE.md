# Salary Dimensions 进阶开发教程（Windows CMD / PowerShell）

> 本项目的三个版本可以逐步安装：v0.2 Excel → v0.3 网页 → v0.4 税后年收入估算。
> 升级前建议先 `git status`、`git add .`、`git commit -m "backup: before upgrade"`，避免覆盖你已经修改过的源码。

## 版本 v0.2：Excel 导入导出

### 目的

新增 `src/salary_dimensions/excel.py`，依赖 `openpyxl`。读取一张 Excel 工作表的 `salary` 列，保留其他列的值，把解析字段写到新的 `.xlsx` 文件。**不覆盖输入文件。**

### 安装

进入包含 `pyproject.toml` 的项目根目录，运行：

```cmd
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

### 跑通演示

```cmd
.\.venv\Scripts\python.exe -m salary_dimensions --input examples\salaries.xlsx --output parsed_salaries.xlsx --sheet 招聘数据 --column salary
.\.venv\Scripts\python.exe -m pytest -q
```

打开 `parsed_salaries.xlsx`，查看新增的 `status`、`annual_min`、`annual_max` 列。示例 Excel 包含 12 条工资记录。

### 自己学什么

1. 打开 `src/salary_dimensions/excel.py`，寻找 `parse_xlsx()`。
2. 找到 `load_workbook()`：它读入 Excel；找到 `Workbook()`：它创建新 Excel。
3. 理解 `for raw_values in rows` 如何遍历每条招聘记录。
4. 到 `tests/test_excel.py` 添加一条新的异常输入测试。

### 边界条件

- 默认解析活动工作表，也可通过 `--sheet` 选择工作表。
- 输出只保留**单个选中工作表的数据值**以及新增解析结果；不保留原样式、图表、图片、公式和其他工作表。
- 公式单元格以保存时缓存值读取；若未缓存则视为空。不能把它当作 Excel 公式计算引擎。
- 自动忽略完全空白的行，不会覆盖原始文件。
- 已存在解析结果同名列时会报错，防止重复解析。

