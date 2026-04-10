# Playwright 操作说明

本文档用于说明本项目中 Playwright 的基本使用方法，重点是“怎么跑起来”。

## 1. 项目说明

本项目使用的是：

- `Python`
- `Playwright`
- `pytest`

测试文件默认放在 `tests/` 目录下，运行结果默认输出到 `reports/` 目录。

## 2. 首次使用

建议在 PowerShell 中执行以下命令：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install
```

## 3. 常用运行命令

### 运行全部用例

```powershell
python -m pytest
```

### 指定环境运行

可选环境在 `config/config.yaml` 中配置，当前常见为 `dev`、`test`、`prod`。

```powershell
python -m pytest --env=dev
python -m pytest --env=test
```

### 指定是否无头运行

```powershell
python -m pytest --headless=true
python -m pytest --headless=false
```

说明：

- `true`：后台运行，不打开浏览器窗口
- `false`：前台运行，会看到浏览器操作过程
- 如果不传，默认读取 `config/config.yaml` 中的浏览器配置

### 运行单个测试文件

```powershell
python -m pytest tests/test_login.py
```

### 运行单个测试方法

```powershell
python -m pytest tests/test_login.py -k test_login_success
```

### 根据网址打开并录制操作

这个命令很常用，适合在新页面上快速录制 Playwright 操作代码。

```powershell
python -m playwright codegen https://example.com
```

如果使用项目虚拟环境，建议写法如下：

```powershell
.\.venv\Scripts\python.exe -m playwright codegen https://example.com
```

常见示例：

```powershell
python -m playwright codegen https://dev.aigrowth8.com/login
python -m playwright codegen --target=python-pytest https://dev.aigrowth8.com/login
python -m playwright codegen -o codegen_login.py https://dev.aigrowth8.com/login
```

说明：

- `codegen`：打开页面并录制操作，自动生成代码
- `--target=python-pytest`：按 `pytest` 风格生成代码，更适合当前项目
- `-o`：把生成结果输出到文件

### 按标记运行

当前项目里常用标记有 `smoke`、`login`。

```powershell
python -m pytest -m smoke
python -m pytest -m login
```

## 4. 运行结果查看

- 测试执行后，结果会输出到 `reports/`
- 用例失败时，会自动截图并附加到报告中
- 如果需要切换浏览器、账号、地址等配置，请修改 `config/config.yaml`

## 5. 常用操作建议

- 日常冒烟测试：`python -m pytest -m smoke --env=dev`
- 调试登录问题：`python -m pytest tests/test_login.py --headless=false`
- 跑指定环境：`python -m pytest --env=test`

## 6. 说明文件涉及的位置

- 测试目录：`tests/`
- 配置文件：`config/config.yaml`
- Pytest 配置：`pytest.ini`
- 公共夹具入口：`conftest.py`

以上命令可以直接作为本项目的日常操作入口使用。
