# PyFileServer (FTP Server GUI)

A graphical FTP server application built with PyQt5 and pyftpdlib.

一个基于 PyQt5 和 pyftpdlib 构建的图形化 FTP 服务器应用程序。


## 切换语言 / Switch Language
- [中文](#中文)
- [English](#english)


<a id="中文"></a>
## 中文

### 功能特性

- 🖥️ 图形用户界面，便于管理 FTP 服务器
- ⚙️ 可配置的服务器设置：
  - 端口号（默认：2121）
  - 根目录
  - 被动模式及自定义端口范围（默认：60000-61000）
  - 编码设置（GBK 或 UTF-8）
  - 线程模式（单线程或多线程）
- 📝 实时日志显示与级别过滤
- 💾 配置保存与加载
- 🔄 热重载服务器配置
- 📊 状态栏显示服务器状态和配置信息
- 👥 连接计数器显示当前连接数


### 安装

#### 使用 pip 安装（推荐）

```bash
pip install .
```

#### 使用 uv 安装

1. 确保已安装 [uv](https://github.com/astral-sh/uv)
2. 安装依赖：
   ```bash
   uv pip install .
   ```


### 使用方法

#### 运行应用程序

安装完成后，可以通过以下方式运行应用程序：

```bash
pyftp
```

或者直接从源代码目录运行：

```bash
python run.py
```

或者：

```bash
python -m src.pyftp.main
```

#### 配置说明

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


### 配置选项

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


### 开发

#### 项目结构

```
pyFTP-server/
├── README.md
├── README_en.md
├── pyproject.toml
├── run.py
├── ftpserver.ini
├── src/
│   └── pyftp/
│       ├── __init__.py
│       ├── main.py
│       ├── application.py
│       ├── test_refactor.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── base_service.py
│       │   ├── qt_base_service.py
│       │   ├── constants.py
│       │   ├── interfaces.py
│       │   ├── exceptions.py
│       │   ├── error_handler.py
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
│       │   ├── logger.py
│       │   ├── connection_counter.py
│       │   ├── port_cache.py
│       │   ├── validators.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── manager.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
```

#### 设置开发环境

```bash
# 使用 venv（标准 Python 方法）
python -m venv .venv
.venv\Scripts\activate  # Windows 上使用
pip install -e .

# 使用 uv（更快的方法）
uv venv .venv
.venv\Scripts\activate  # Windows 上使用
uv pip install -e .
```

#### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行带覆盖率的测试
python -m pytest --cov=src
```


### 贡献

欢迎提交 Pull Request。对于重大更改，请先开 issue 讨论您想要改变的内容。


### 许可证

[MIT](https://choosealicense.com/licenses/mit/)


<a id="english"></a>
## English

### Features

- 🖥️ Graphical user interface for easy FTP server management
- ⚙️ Configurable server settings:
  - Port number (default: 2121)
  - Root directory
  - Passive mode with customizable port range (default: 60000-61000)
  - Encoding (GBK for Chinese or UTF-8)
  - Threading mode (single or multi-threaded)
- 📝 Real-time logging with level filtering
- 💾 Configuration saving and loading
- 🔄 Hot reload of server configuration
- 📊 Status bar showing server status and configuration
- 👥 Connection counter showing current connections


### Installation

#### Using pip (recommended)

```bash
pip install .
```


### Usage

#### Running the application

After installation, you can run the application with:

```bash
pyftp
```

Or directly from the source directory:

```bash
python run.py
```

Or:

```bash
python -m src.pyftp.main
```

#### Configuration

1. Configure server settings:
   - Set the port (default: 2121)
   - Choose the root directory for FTP access
   - Enable/disable passive mode and set port range
   - Select encoding (GBK for Chinese or UTF-8)
   - Choose threading mode

2. Start the server by clicking "Start Server" button

3. Use any FTP client to connect to the server:
   - Address: localhost
   - Port: as configured (default 2121)
   - Username: anonymous (no password required)


### Configuration Options

- **Port**: The TCP port the FTP server listens on (default: 2121)
- **Root Directory**: The base directory accessible via FTP
- **Passive Mode**: 
  - Enabled by default
  - Customizable port range (default: 60000-61000)
- **Encoding**:
  - GBK: For Chinese language support
  - UTF-8: For international character support
- **Threading Mode**:
  - Single-threaded: Simpler but less concurrent
  - Multi-threaded: Better for multiple connections


### Development

#### Project Structure

```
pyFTP-server/
├── README.md
├── README_en.md
├── pyproject.toml
├── run.py
├── ftpserver.ini
├── src/
│   └── pyftp/
│       ├── __init__.py
│       ├── main.py
│       ├── application.py
│       ├── test_refactor.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── base_service.py
│       │   ├── qt_base_service.py
│       │   ├── constants.py
│       │   ├── interfaces.py
│       │   ├── exceptions.py
│       │   ├── error_handler.py
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
│       │   ├── logger.py
│       │   ├── connection_counter.py
│       │   ├── port_cache.py
│       │   ├── validators.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── manager.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
```

#### Setting up development environment

```bash
# Using venv (standard Python approach)
python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install -e .

# Using uv (faster approach)
uv venv .venv
.venv\Scripts\activate  # On Windows
uv pip install -e .
```

#### Running tests

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=src
```


### Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


### License

[MIT](https://choosealicense.com/licenses/mit/)
