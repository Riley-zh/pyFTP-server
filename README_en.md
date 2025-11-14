# PyFTP Server GUI

A graphical FTP server application built with PyQt5 and pyftpdlib.

## Features

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

## Installation

### Using pip (recommended)

```bash
pip install .
```

### Using uv

1. Make sure you have [uv](https://github.com/astral-sh/uv) installed
2. Install dependencies:
   ```bash
   uv pip install .
   ```

## Usage

### Running the application

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

### Configuration

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

## Configuration Options

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

## Development

### Project Structure

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

### Setting up development environment

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

### Running tests

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=src
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)