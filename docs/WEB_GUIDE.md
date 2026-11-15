# Salary Dimensions v0.3 网页交互升级指南

## 新增功能
- 单条薪资解析：展示计薪周期、金额区间、薪数和预计年薪。
- Excel 批量解析：上传 `.xlsx`，选择工作表和薪资列，下载解析后的新工作簿。
- 使用说明：展示支持格式和计算边界。

网页直接调用现有的 `parse_salary()` 和 `parse_xlsx_bytes()`，不复制薪资识别规则。

## Windows CMD 安装
在项目根目录（能看到 `pyproject.toml`）运行：

```cmd
.\.venv\Scripts\python.exe -m pip install -e ".[dev,web]"
```

如果没有 `.venv`，先运行：

```cmd
python -m venv .venv
```

## 启动网页

```cmd
.\.venv\Scripts\python.exe -m streamlit run src\salary_dimensions\web_app.py
```

CMD 会显示本地地址，通常是：

```text
http://localhost:8501
```

复制到浏览器打开。停止网页时回到 CMD 按 `Ctrl + C`。

## 自动测试

```cmd
.\.venv\Scripts\python.exe -m pytest -q
```

v0.2 有 37 项测试，本补丁新增 5 项；如果本地 v0.2 与 GitHub 版本一致，预期总计 42 项通过。

GitHub Actions 原来安装 `.[dev]` 即可运行测试，因为测试导入网页模块时不会加载 Streamlit。只有启动网页时才需要安装 `.[web]`。

## 提交 GitHub

本地测试通过后：

```cmd
git status
git add .
git commit -m "feat: add Streamlit web interface"
git push
```

## 注意事项
- 这是本地网页，不是公网部署的网站。
- 关闭运行 Streamlit 的 CMD 窗口，网页服务就会停止。
- Excel 输出只保留所选工作表的数据值和解析字段，不保留原始样式、图表、图片、公式和其他工作表。
- 不要把包含个人信息或公司敏感数据的招聘表上传到不可信的公开网站。
