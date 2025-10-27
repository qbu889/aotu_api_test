# 自动化测试框架

一个基于 PyTest 的轻量级 API 自动化测试项目，支持用例以 YAML/Excel 维护，内置日志与 HTML 报告，开箱即用的 Excel→YAML 导入流程。

## 功能概览

- 用例数据驱动：支持 YAML 主用例，Excel 批量导入/合并
- 两种运行模式：交互式/自动导入模式（CI/CD 友好）
- 测试报告：pytest-html 生成自包含 HTML 报告
- 日志：按时间自动切分，控制台与文件双通道
- 可扩展：数据生成、断言器、导入策略均可按需扩展

---

## 项目结构

```
aotu_api_test/
├── base/                      # 基础能力：请求封装、断言、日志
├── config/                    # 全局配置（BASE_URL、目录等）
├── data/
│   ├── test_cases.yaml        # 主用例文件（测试读取的数据源）
│   ├── excel_cases/           # Excel 用例目录（导入入口）
│   │   └── test_case_template.xlsx
│   └── templates/             # Excel 模板
├── logs/                      # 运行日志
├── reports/                   # HTML 测试报告
├── TestCase/                  # PyTest 测试集合（按模块划分）
│   └── API/test_api.py
├── utils/
│   ├── yaml_utils.py          # YAML/动态数据处理
│   └── data_import/           # 导入框架（Excel→YAML）
│       ├── import_manager.py
│       ├── excel_importer.py
│       ├── yaml_handler.py
│       └── base_importer.py
├── scripts/
│   └── cleanup.py             # 缓存/日志/报告清理脚本
├── run.py                     # 入口脚本（集成导入与执行）
├── requirements.txt
└── EXCEL_IMPORT_GUIDE.md      # Excel 导入使用说明（本 README 已整合核心内容）
```

---

## 环境要求

- Python 3.9+（已在 3.12 验证）
- Windows/ macOS/ Linux（本仓库示例输出以 Windows 为主）

安装依赖：

```powershell
# 建议使用虚拟环境（可选）
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

配置基础 URL（可选）：

- 通过环境变量 BASE_URL，或在 `.env` 中设置，例如：

```
BASE_URL=http://localhost:8080
```

配置项位于 `config/settings.py`：

- BASE_URL 默认 `http://localhost:8080`
- 数据、日志、报告目录会在首次运行时自动创建

---

## 运行方式

项目入口：`run.py`。支持两种模式：

### 1) 自动导入模式（推荐，CI/CD 友好）

```powershell
# 自动导入 Excel 用例后执行测试
python run.py -i

# 指定导入策略
python run.py -i -s skip      # 跳过重复 ID（默认）
python run.py -i -s replace   # 替换重复 ID
python run.py -i -s append    # 直接追加
```

特点：无需交互，适合在流水线中运行。

### 2) 交互式模式（本地体验）

```powershell
python run.py
```

流程：
- 自动检测 `data/excel_cases/` 下的 Excel 文件
- 询问是否导入及合并策略
- 导入成功后执行测试

说明：如果在 IDE 的“运行”按钮等非交互环境中启动，系统会自动转为“自动导入 + 默认策略 skip”。

---

## Excel → YAML 导入说明（要点）

将 Excel 中的用例批量导入并合并到 `data/test_cases.yaml`。核心入口位于：

- 交互/自动流程：`utils/excel_case_loader.py`
- 导入实现：`utils/data_import/import_manager.py`

### 合并策略

- skip（推荐）：跳过已存在的 case_id
- replace：覆盖相同 case_id 的旧用例
- append：不检查重复，直接追加

### Excel 模板与示例

模板文件：`data/templates/test_case_template.xlsx`

关键列（必填）：

- case_id：唯一整数
- description：用例描述
- method：HTTP 方法，如 POST/GET/PUT/DELETE
- url：请求路径，如 /api/users
- expected_http_code：期望 HTTP 状态码
- expected_res_code：期望业务码

可选列（JSON 字符串）：headers、request_data、expected_response

### 动态占位符

在 YAML/Excel 的字符串中支持动态值：

- `{{generate_username:前缀}}`
- `{{generate_email:前缀}}`
- `{{generate_phone}}`
- `{{generate_age:默认}}`

由 `utils/DataGenerator.py` 与 `utils/yaml_utils.py` 协同生成。

---

## 报告与日志

- 报告：`reports/report_YYYY-MM-DD_HH-MM-SS.html`
- 日志：`logs/test_YYYY-MM-DD_HH-MM-SS.log`

首次运行会自动创建上述目录。Windows 下文件名已避免使用不支持的冒号字符。

执行后测试报告：
<img width="1460" height="1086" alt="image" src="https://github.com/user-attachments/assets/c9c9cade-109b-4d80-a1d4-48baeff58da5" />
---

## 如何扩展

### 1) 新增接口用例

- 直接在 `data/test_cases.yaml` 追加
- 或在 `data/excel_cases/` 新建 Excel，并通过导入合并

### 2) 新增数据生成规则

- 扩展 `utils/DataGenerator.py`
- 在 `utils/yaml_utils.py` 的 `_generate_dynamic_value` 中注册新占位符

### 3) 新增断言/校验

- 扩展 `base/assertion.py`，新增方法或增强现有方法
- 在测试文件中（如 `TestCase/API/test_api.py`）调用新的断言

### 4) 新的导入策略

- 在 `utils/data_import/yaml_handler.py` 中扩展合并逻辑
- 在 `utils/excel_case_loader.py` 中登记策略编号与名称映射

### 5) 新测试模块

- 在 `TestCase/` 下创建新目录（如 `UI/`、`DataBase/`），编写对应测试与 `conftest.py`

---

## 常见问题（FAQ）

1) 运行后没有触发 Excel 导入？
- 确认 Excel 文件放在 `data/excel_cases/`
- IDE 中点击运行不具备交互输入时，会自动使用“自动导入 + skip”策略

2) 导入后 YAML 没变化？
- 使用 skip 策略时，重复 case_id 会被跳过，尝试 replace/append

3) JSON 字段解析失败？
- 请使用合法 JSON 字符串，键和值需要双引号

4) BASE_URL 如何修改？
- 在 `.env` 设置 `BASE_URL`，或修改 `config/settings.py`

5) 如何清理缓存/旧报告？

```powershell
python scripts/cleanup.py                # 清理缓存、7天前日志与报告
python scripts/cleanup.py --cache        # 仅清理缓存
python scripts/cleanup.py --logs         # 仅清理旧日志
python scripts/cleanup.py --reports      # 仅清理旧报告
```

---

## 试运行

```powershell
# 自动导入并执行
python run.py -i

# 交互式（在可输入的终端中运行）
python run.py
```

生成的报告位于 `reports/` 目录，可直接在浏览器打开。

---

最后更新：2025-10-22

