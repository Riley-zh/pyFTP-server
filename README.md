# PyFTP Server GUI

一个基于 PyQt5 和 pyftpdlib 构建的图形化 FTP 服务器应用程序。

## 功能特性

- 🖥️ 图形用户界面，便于管理 FTP 服务器
- ⚙️ 可配置的服务器设置：
  - 端口号
  - 根目录
  - 被动模式及自定义端口范围
  - 编码设置（GBK 或 UTF-8）
  - 线程模式（单线程或多线程）
- 📝 实时日志显示与级别过滤
- 💾 配置保存与加载
- 🔄 热重载服务器配置
- 📊 状态栏显示服务器状态和配置信息

## 安装

### 使用 pip 安装（推荐）

```bash
pip install .
```

### 使用 uv 安装

1. 确保已安装 [uv](https://github.com/astral-sh/uv)
2. 安装依赖：
   ```bash
   uv pip install .
   ```

## 使用方法

### 运行应用程序

安装完成后，可以通过以下方式运行应用程序：

```bash
pyftp
```

或者直接从源代码目录运行：

```bash
python -m src.pyftp.main
```

### 配置说明

1. 配置服务器设置：
   - 设置端口（默认：2121）
   - 选择 FTP 访问的根目录
   - 启用/禁用被动模式并设置端口范围
   - 选择编码（GBK 适用于中文或 UTF-8 国际化）
   - 选择线程模式

2. 点击"启动服务器"按钮启动服务器

3. 使用任何 FTP 客户端连接到服务器：
   - 地址：localhost
   - 端口：配置的端口（默认 2121）
   - 用户名：anonymous（无需密码）

## 配置选项

- **端口**：FTP 服务器监听的 TCP 端口（默认：2121）
- **根目录**：通过 FTP 访问的基目录
- **被动模式**：
  - 默认启用
  - 可自定义端口范围（默认：60000-61000）
- **编码设置**：
  - GBK：支持中文
  - UTF-8：国际化字符支持
- **线程模式**：
  - 单线程模式：简单但并发性较差
  - 多线程模式：更好的多连接支持

## 开发

### 项目结构

```
pyFTP-server/
├── README.md
├── pyproject.toml
├── src/
│   └── pyftp/
│       ├── __init__.py
│       ├── main.py
│       ├── gui/
│       │   ├── __init__.py
│       │   ├── window.py
│       │   └── components/
│       │       ├── __init__.py
│       │       ├── config_panel.py
│       │       ├── control_panel.py
│       │       ├── log_panel.py
│       │       └── user_panel.py
│       ├── server/
│       │   ├── __init__.py
│       │   ├── ftp_server.py
│       │   └── logger.py
│       └── config/
│           ├── __init__.py
│           └── manager.py
└── tests/
    ├── __init__.py
    └── test_config.py
```

### 设置开发环境

```bash
# 使用 venv（标准 Python 方法）
python -m venv .venv
source .venv/bin/activate  # Windows 上使用: .venv\Scripts\activate
pip install -e .

# 使用 uv（更快的方法）
uv venv .venv
source .venv/bin/activate  # Windows 上使用: .venv\Scripts\activate
uv pip install -e .
```

### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行带覆盖率的测试
python -m pytest --cov=src
```

## 贡献

欢迎提交 Pull Request。对于重大更改，请先开 issue 讨论您想要改变的内容。

## 许可证

[MIT](https://choosealicense.com/licenses/mit/)