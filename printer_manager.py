import logging

logger = logging.getLogger(__name__)

try:
    import win32print
    WIN32_AVAILABLE = True
except Exception as _e:
    WIN32_AVAILABLE = False
    logger.warning(f"pywin32 not available ({type(_e).__name__}: {_e}) — printer features disabled (dev mode)")


class PrinterManager:

    def get_printers(self):
        if not WIN32_AVAILABLE:
            return ["Demo Printer (pywin32 not installed)"]
        try:
            printers = win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS,
                None, 2
            )
            return [p['pPrinterName'] for p in printers]
        except Exception as e:
            logger.error(f"Error listing printers: {e}")
            return []

    def get_default_printer(self):
        if not WIN32_AVAILABLE:
            return "Demo Printer"
        try:
            return win32print.GetDefaultPrinter()
        except Exception as e:
            logger.error(f"Error getting default printer: {e}")
            return None

    def is_printer_online(self, printer_name):
        if not WIN32_AVAILABLE:
            return False
        try:
            handle = win32print.OpenPrinter(printer_name)
            info = win32print.GetPrinter(handle, 2)
            win32print.ClosePrinter(handle)
            # Status 0 = ready; anything else = error/offline/busy
            return info.get('Status', -1) == 0
        except Exception as e:
            logger.error(f"Error checking printer '{printer_name}': {e}")
            return False

    def print_raw(self, printer_name, data: bytes) -> int:
        """Send raw ESC/POS bytes to printer. Returns job ID.
        
        Raises:
            RuntimeError: if printer is offline, not found, or spooling fails.
        """
        if not WIN32_AVAILABLE:
            logger.info(f"[DEV MODE] Would print {len(data)} bytes to '{printer_name}'")
            return 0

        # ── Pre-flight: check printer is online before spooling ────────────────
        try:
            handle_check = win32print.OpenPrinter(printer_name)
            info = win32print.GetPrinter(handle_check, 2)
            win32print.ClosePrinter(handle_check)
            status = info.get('Status', -1)
            # status flags: 0=ready, non-zero = error/offline/busy
            if status != 0:
                status_map = {
                    0x00000080: 'Printer is offline',
                    0x00000008: 'Printer has an error',
                    0x00000020: 'Paper jam',
                    0x00000040: 'Out of paper',
                    0x00000010: 'Printer is busy',
                    0x00001000: 'Door open',
                }
                msg = status_map.get(status, f'Printer not ready (status code: {status})')
                logger.warning(f"Pre-flight failed for '{printer_name}': {msg}")
                raise RuntimeError(msg)
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"Cannot reach printer '{printer_name}': {e}")

        # ── Spool the job ──────────────────────────────────────────────────────
        handle = win32print.OpenPrinter(printer_name)
        try:
            job = win32print.StartDocPrinter(handle, 1, ("PrintBridge Job", None, "RAW"))
            try:
                win32print.StartPagePrinter(handle)
                win32print.WritePrinter(handle, data)
                win32print.EndPagePrinter(handle)
            finally:
                win32print.EndDocPrinter(handle)
            logger.info(f"Print job #{job} sent to '{printer_name}' ({len(data)} bytes)")
            return job
        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Print failed on '{printer_name}': {e}")
            raise RuntimeError(f"Printing failed: {e}")
        finally:
            win32print.ClosePrinter(handle)
