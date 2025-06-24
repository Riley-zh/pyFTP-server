# PyFTP Server GUI

A graphical FTP server application built with PyQt5 and pyftpdlib.

## Features

- 🖥️ Graphical user interface for easy FTP server management
- ⚙️ Configurable server settings:
  - Port number
  - Root directory
  - Passive mode with customizable port range
  - Encoding (GBK for Chinese or UTF-8)
  - Threading mode (single or multi-threaded)
- 📝 Real-time logging with level filtering
- 💾 Configuration saving and loading
- 🔄 Hot reload of server configuration
- 📊 Status bar showing server status and configuration

## Installation

1. Make sure you have [uv](https://github.com/astral-sh/uv) installed
2. Clone this repository
3. Install dependencies:
   ```bash
   uv pip install PyQt5 pyftpdlib
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Configure server settings:
   - Set the port (default: 2121)
   - Choose the root directory for FTP access
   - Enable/disable passive mode and set port range
   - Select encoding (GBK for Chinese or UTF-8)
   - Choose threading mode

3. Start the server by clicking "Start Server" button

4. Use any FTP client to connect to the server:
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

To set up development environment:
```bash
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
