import os
import sys
import json
import logging

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from printer_manager import PrinterManager
from universal_formatter import format_universal

logger = logging.getLogger(__name__)

# ── Config helpers ────────────────────────────────────────────────────────────

def _app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(_app_dir(), 'config.json')

DEFAULT_CONFIG = {
    'port': 5000,
    'printer': None,
    'paper_width': 80,
}

def get_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)

def save_config(cfg: dict):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)

# ── Flask app factory ─────────────────────────────────────────────────────────

def create_app() -> Flask:
    if getattr(sys, 'frozen', False):
        tmpl_dir = os.path.join(sys._MEIPASS, 'templates')
    else:
        tmpl_dir = os.path.join(os.path.dirname(__file__), 'templates')

    app = Flask(__name__, template_folder=tmpl_dir)
    CORS(app, origins='*')

    pm = PrinterManager()

    # ── Dashboard ─────────────────────────────────────────────────────────────
    @app.route('/')
    def dashboard():
        return render_template('index.html')

    # ── GET /api/status ───────────────────────────────────────────────────────
    @app.route('/api/status', methods=['GET'])
    def api_status():
        try:
            cfg          = get_config()
            printer_name = cfg.get('printer') or pm.get_default_printer()
            printers     = pm.get_printers()
            is_online    = pm.is_printer_online(printer_name) if printer_name else False

            return jsonify({
                'success':          True,
                'status':           'online' if is_online else 'offline',
                'printerName':      printer_name,
                'isDefault':        printer_name == pm.get_default_printer(),
                'isOnline':         is_online,
                'paperWidth':       cfg.get('paper_width', 80),
                'availablePrinters': printers,
                'serverVersion':    '1.1.1',
            })
        except Exception as e:
            logger.error(f"[/api/status] {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # ── GET /api/printers ─────────────────────────────────────────────────────
    @app.route('/api/printers', methods=['GET'])
    def api_printers():
        try:
            return jsonify({
                'success':  True,
                'printers': pm.get_printers(),
                'default':  pm.get_default_printer(),
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # ── GET/POST /api/config ──────────────────────────────────────────────────
    @app.route('/api/config', methods=['GET'])
    def api_config_get():
        return jsonify(get_config())

    @app.route('/api/config', methods=['POST'])
    def api_config_post():
        try:
            data = request.json or {}
            cfg  = get_config()
            if 'printer'     in data: cfg['printer']     = data['printer']
            if 'paper_width' in data: cfg['paper_width'] = int(data['paper_width'])
            save_config(cfg)
            return jsonify({'success': True, 'config': cfg})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # ── POST /api/print and legacy variants ───────────────────────────────────
    @app.route('/api/print', methods=['POST'])
    @app.route('/api/print/receipt', methods=['POST'])
    @app.route('/api/print/kot', methods=['POST'])
    def api_print_generic():
        content_type = request.content_type or ''

        # ── Resolve printer (shared for both paths) ────────────────────────────
        # Priority: request body/param "printer" → config default → OS default
        cfg              = get_config()
        request_printer  = request.args.get('printer')  # query param
        if not request_printer and request.is_json and request.json:
            request_printer = request.json.get('printer')  # JSON body
        printer_name = request_printer or cfg.get('printer') or pm.get_default_printer()
        if not printer_name:
            return jsonify({
                'success': False,
                'message': 'No printer configured. Please set a printer in the dashboard.',
            }), 503

        # ── Build raw ESC/POS bytes ────────────────────────────────────────────
        try:
            if 'text/plain' in content_type:
                # Plain-text path: print exactly as received, no formatting
                text = request.get_data(as_text=True)
                if not text:
                    return jsonify({
                        'success': False,
                        'message': 'Empty text body',
                    }), 400

                CMD_INIT = b'\x1b\x40'
                CMD_CUT  = b'\x1d\x56\x41\x05'
                raw = CMD_INIT + text.encode('cp437', errors='replace') + b'\n\n\n' + CMD_CUT
                mode = 'text'

            else:
                # JSON path: use universal formatter
                data = request.json
                if not data:
                    return jsonify({
                        'success': False,
                        'message': 'No JSON body provided',
                    }), 400
                raw  = format_universal(data, paper_width=cfg.get('paper_width', 80))
                mode = 'json'

            job_id = pm.print_raw(printer_name, raw)
            logger.info(f"[/api/print] [{mode}] Job #{job_id} sent to '{printer_name}'")
            return jsonify({
                'success': True,
                'message': 'Printed successfully',
                'jobId':   str(job_id),
                'printer': printer_name,
                'mode':    mode,
            }), 200

        except RuntimeError as e:
            logger.warning(f"[/api/print] Printer error: {e}")
            return jsonify({
                'success': False,
                'message': str(e),
                'printer': printer_name,
            }), 503

        except Exception as e:
            logger.error(f"[/api/print] Unexpected error: {e}")
            return jsonify({
                'success': False,
                'message': f'Print failed: {str(e)}',
                'printer': printer_name,
            }), 500

    # ── POST /api/test-print ──────────────────────────────────────────────────
    @app.route('/api/test-print', methods=['POST'])
    def api_test_print():
        try:
            cfg          = get_config()
            printer_name = cfg.get('printer') or pm.get_default_printer()
            if not printer_name:
                return jsonify({'success': False, 'error': 'No printer configured'}), 400

            test_payload = {
                'businessName':     'PrintBridge Test',
                'orderId':          'TEST-001',
                'dailyTokenNumber': '1',
                'dateTime':         'Test Print',
                'customerName':     'Test Customer',
                'tableNumber':      '1',
                'items':            [{'name': 'Test Item', 'quantity': 1, 'price': 100, 'total': 100}],
                'otherCharges':     [],
                'orderTotal':       100,
                'deliveryType':     'DINE_IN',
                'customerNote':     'This is a test print from PrintBridge',
            }
            raw    = format_universal(test_payload, paper_width=cfg.get('paper_width', 80))
            job_id = pm.print_raw(printer_name, raw)

            return jsonify({'success': True, 'message': 'Test print sent', 'jobId': str(job_id)})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    return app
