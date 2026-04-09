"""
PrintBridge — main entry point
Starts the Flask server on port 5000 and adds a system-tray icon.
"""
import os
import sys
import threading
import webbrowser
import logging

# ── Logging ───────────────────────────────────────────────────────────────────
_app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) \
           else os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    filename=os.path.join(_app_dir, 'printbridge.log'),
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-8s  %(name)s — %(message)s',
)
logger = logging.getLogger('printbridge')

# ── Imports after logging ─────────────────────────────────────────────────────
from server import create_app, get_config                # noqa: E402

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    logger.warning("pystray/Pillow not found — running without system tray")


# ── Tray icon ─────────────────────────────────────────────────────────────────

def _make_icon_image() -> 'Image':
    size = 64
    img  = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d    = ImageDraw.Draw(img)
    # Printer body
    d.rectangle([6, 22, 58, 46], fill='#2563EB', outline='#1E40AF', width=2)
    # Paper tray (top)
    d.rectangle([14, 8, 50, 24],  fill='#93C5FD', outline='#3B82F6', width=1)
    # Paper output (bottom)
    d.rectangle([14, 44, 50, 58], fill='#F8FAFC', outline='#CBD5E1', width=1)
    # Status LED
    d.ellipse([44, 28, 54, 38], fill='#10B981')
    return img


def _run_flask(app, port: int):
    try:
        app.run(host='127.0.0.1', port=port, debug=False,
                use_reloader=False, threaded=True)
    except Exception as e:
        logger.error(f"Flask server crashed: {e}")


# ── Main ──────────────────────────────────────────────────────────────────────

def _open_browser_delayed(url, delay=1.5):
    """Open browser after a short delay to let the server start."""
    import time
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except Exception as e:
        logger.warning(f"Could not open browser: {e}")


def main():
    cfg  = get_config()
    port = cfg.get('port', 5000)
    url  = f'http://localhost:{port}'

    app = create_app()

    # Start server in background daemon thread
    t = threading.Thread(target=_run_flask, args=(app, port), daemon=True)
    t.start()
    logger.info(f"PrintBridge server listening on {url}")

    # Always open browser dashboard after a short delay so the user sees something
    browser_thread = threading.Thread(target=_open_browser_delayed, args=(url,), daemon=True)
    browser_thread.start()

    if not TRAY_AVAILABLE:
        logger.info("No tray — blocking on Flask thread")
        t.join()
        return

    # ── System tray ───────────────────────────────────────────────────────────
    url = f'http://localhost:{port}'

    menu = pystray.Menu(
        pystray.MenuItem(f'PrintBridge  —  port {port}', None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Open Dashboard', lambda icon, item: webbrowser.open(url)),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Exit', lambda icon, item: (icon.stop(), sys.exit(0))),
    )

    icon = pystray.Icon(
        'PrintBridge',
        _make_icon_image(),
        f'PrintBridge  :{port}',
        menu,
    )

    def _on_setup(icon):
        icon.visible = True
        try:
            icon.notify(
                f'Running at http://localhost:{port}',
                'PrintBridge Started',
            )
        except Exception:
            pass

    icon.run(_on_setup)


if __name__ == '__main__':
    main()
