# PrintBridge (Auto Print Receipt Server)

PrintBridge is a local web server built with Python and Flask that acts as an intermediate layer between web applications and local thermal ESC/POS printers. It accepts JSON HTTP requests with POS ticket or KOT data and directly sends the corresponding ESC/POS byte sequence to configured local/network printers.

## Key Features
* **Universal Formatter**: Converts JSON payloads into raw ESC/POS bytes to support a consistent thermal printing interface.
* **REST API**: Provides simple endpoints to check printer status, configure the default printing device, and print receipts/KOTs.
* **Dashboard Display**: A local frontend interface at `http://localhost:5000/` for verifying the server status, checking available printers, and doing test prints.
* **Standalone Executable**: The project is packaged using PyInstaller into a standalone Windows `.exe` to run effortlessly with no Python environment dependencies. (See GitHub actions `.github/workflows/release.yml`)

## Structure
- `main.py` - Entry point to start the Flask application daemon.
- `server.py` - Contains the Flask API Routes (`/api/print`, `/api/status`, etc.).
- `printer_manager.py` - System-level printer interfacing handling logic for Windows/Linux.
- `universal_formatter.py` - Custom formatting logic using raw ESC/POS byte commands.
- `config.json` - Server state to remember default printer and paper width.

## API Usage
You can find the full documentation generated via `generate_docs.py` as a PDF, but here are the key endpoints:

- `POST /api/print`: Send JSON data to trigger a print job.
- `POST /api/test-print`: Generate a dummy test ticket to verify connection.
- `GET /api/status`: Fetch server and printer health/status.
- `GET /api/printers`: List all locally available printers.

## Local Setup
1. Create a virtual environment (e.g. `python -m venv venv`) and activate it.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   python main.py
   ```
4. Access the config dashboard at [http://localhost:5000/](http://localhost:5000/).
