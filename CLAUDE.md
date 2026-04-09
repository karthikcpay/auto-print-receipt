# PrintBridge AI Coding Guidelines

This document outlines the rules, styling conventions, and architectural notes for any AI agents interacting with the `print-server` (PrintBridge) repository.

## User Global Rules
* **Imports:** **Always place import statements at the beginning of the file.** Do not place imports inline within functions or classes.
* **Virtual Environment Check:** **Always check for a `venv` directory before running any python code or tests.** Use the python executable from the virtual environment if it exists.

## Project Architecture Notes
- **Web Framework:** Flask is used for the web server and API (`server.py`).
- **Printer Interactions:** All OS-level print interactions are handled in `printer_manager.py`. It uses platform-specific calls or utilities to map to physical printers.
- **Payload Formatting:** The layout building logic (`universal_formatter.py`) uses a raw byte string builder that outputs ESC/POS commands (e.g. `\x1b\x40` for init, `\x1b\x61\x01` for center align).
- **Configuration:** No external database is used. A simple local JSON cache config file (`config.json`) persists the selected default printer and paper width.

## Code Constraints
- **PyInstaller compatibility:** Since this app is frequently packaged to an `.exe` workflow (`release.yml`), avoid adding system-level dependencies or packages with complex C-extensions unless strictly required. Also handle the difference between `__file__` and `sys.executable` (via `sys._MEIPASS`) for finding bundled assets like `templates/`.
- **Frontend changes:** HTML/JS/CSS live solely within `templates/index.html`. 
- **Error Handling:** When editing the `/api/print` endpoint, securely handle hardware/driver level exceptions gracefully, returning standard JSON failure payloads (status 5xx/4xx), not stack traces.
