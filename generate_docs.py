"""
Generate PrintBridge API Documentation PDF — Updated for new /print, /queue, /jobs API.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Preformatted, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import datetime

OUTPUT = "PrintBridge_API_Documentation.pdf"

# ── Colors ─────────────────────────────────────────────────────────────────────
BLUE        = colors.HexColor("#2563EB")
DARK_BLUE   = colors.HexColor("#1E3A8A")
LIGHT_BLUE  = colors.HexColor("#DBEAFE")
GREEN       = colors.HexColor("#16A34A")
LIGHT_GREEN = colors.HexColor("#DCFCE7")
RED         = colors.HexColor("#DC2626")
LIGHT_RED   = colors.HexColor("#FEE2E2")
ORANGE      = colors.HexColor("#D97706")
LIGHT_ORANGE= colors.HexColor("#FEF3C7")
PURPLE      = colors.HexColor("#7C3AED")
GRAY        = colors.HexColor("#6B7280")
LIGHT_GRAY  = colors.HexColor("#F9FAFB")
DARK        = colors.HexColor("#111827")
MID_GRAY    = colors.HexColor("#E5E7EB")
CODE_BG     = colors.HexColor("#1E1E2E")
CODE_FG     = colors.HexColor("#CDD6F4")

W = A4[0] - 4*cm

# ── Style helpers ──────────────────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)

TITLE = S("TITLE", fontName="Helvetica-Bold", fontSize=30, textColor=colors.white,
    alignment=TA_CENTER, spaceAfter=4, leading=36)
SUBTITLE = S("SUBTITLE", fontName="Helvetica", fontSize=13,
    textColor=colors.HexColor("#BFDBFE"), alignment=TA_CENTER, spaceAfter=2)
H1 = S("H1", fontName="Helvetica-Bold", fontSize=17, textColor=DARK_BLUE,
    spaceAfter=6, spaceBefore=16, leading=22)
H2 = S("H2", fontName="Helvetica-Bold", fontSize=13, textColor=BLUE,
    spaceAfter=4, spaceBefore=10, leading=17)
H3 = S("H3", fontName="Helvetica-Bold", fontSize=11, textColor=DARK,
    spaceAfter=3, spaceBefore=6, leading=15)
BODY = S("BODY", fontName="Helvetica", fontSize=10, textColor=DARK,
    spaceAfter=4, leading=15)
BODY_SMALL = S("BODY_SMALL", fontName="Helvetica", fontSize=9, textColor=GRAY,
    spaceAfter=3, leading=13)
MONO = S("MONO", fontName="Courier", fontSize=9, textColor=DARK,
    spaceAfter=3, leading=13)

def code(text):
    return Preformatted(text, ParagraphStyle(
        "code", fontName="Courier", fontSize=8, textColor=CODE_FG,
        backColor=CODE_BG, leading=12, leftIndent=8, rightIndent=8,
        spaceBefore=4, spaceAfter=8,
    ))

def info_box(text, bg=LIGHT_BLUE, fg=DARK):
    data = [[Paragraph(f"  ℹ️  {text}", S("nb", fontName="Helvetica", fontSize=9,
        textColor=fg, leading=13))]]
    t = Table(data, colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    return t

def warn_box(text):
    return info_box(f"⚠️  {text}", bg=LIGHT_ORANGE, fg=colors.HexColor("#78350F"))

def endpoint_header(method, path):
    color_map = {"GET": GREEN, "POST": BLUE, "DELETE": RED}
    bg = color_map.get(method, PURPLE)
    data = [[
        Paragraph(method, S("m", fontName="Helvetica-Bold", fontSize=10,
            textColor=colors.white, alignment=TA_CENTER)),
        Paragraph(f"<b>{path}</b>", S("p", fontName="Courier-Bold",
            fontSize=12, textColor=DARK_BLUE)),
    ]]
    t = Table(data, colWidths=[1.7*cm, W - 1.7*cm], rowHeights=[0.72*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), bg),
        ("BACKGROUND", (1,0), (1,0), LIGHT_BLUE),
        ("ALIGN", (0,0), (0,0), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (1,0), (1,0), 14),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return t

def fields_table(rows, headers=("Field", "Type", "Required", "Description")):
    widths = [3.2*cm, 2.2*cm, 2.2*cm, W - 7.6*cm]
    data = [[Paragraph(h, S("th", fontName="Helvetica-Bold", fontSize=9,
        textColor=colors.white)) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), BODY_SMALL) for c in row])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    return t

def response_table(rows):
    widths = [3.8*cm, 2.5*cm, W - 6.3*cm]
    data = [[Paragraph(h, S("th", fontName="Helvetica-Bold", fontSize=9,
        textColor=colors.white)) for h in ("Field", "Type", "Description")]]
    for row in rows:
        data.append([Paragraph(str(c), BODY_SMALL) for c in row])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    return t

def status_badge(code_str, desc, bg):
    data = [[
        Paragraph(code_str, S("sc", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white, alignment=TA_CENTER)),
        Paragraph(desc, BODY_SMALL),
    ]]
    t = Table(data, colWidths=[1.5*cm, W - 1.5*cm], rowHeights=[0.55*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), bg),
        ("BACKGROUND", (1,0), (1,0), colors.white),
        ("ALIGN", (0,0), (0,0), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (1,0), (1,0), 10),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return t


# ── BUILD ──────────────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    story = []

    # ══════════════════════════════════════════════════
    # COVER
    # ══════════════════════════════════════════════════
    cover = Table([[
        Paragraph("🖨️  PrintBridge", TITLE),
        Paragraph("Local Thermal Print Server", SUBTITLE),
        Paragraph("API Reference &amp; Developer Guide", SUBTITLE),
        Spacer(1, 0.3*cm),
        Paragraph(
            f"v1.0.0  •  {datetime.date.today().strftime('%B %d, %Y')}",
            S("d", fontName="Helvetica", fontSize=10,
              textColor=colors.HexColor("#93C5FD"), alignment=TA_CENTER)),
    ]], colWidths=[W])
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_BLUE),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 30),
        ("BOTTOMPADDING", (0,0), (-1,-1), 30),
        ("LEFTPADDING", (0,0), (-1,-1), 20),
        ("RIGHTPADDING", (0,0), (-1,-1), 20),
    ]))
    story += [cover, Spacer(1, 0.7*cm)]

    # ══════════════════════════════════════════════════
    # 1. OVERVIEW
    # ══════════════════════════════════════════════════
    story += [
        Paragraph("1. What is PrintBridge?", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.2*cm),
        Paragraph(
            "PrintBridge is a lightweight local Windows service that exposes a simple HTTP REST API. "
            "It allows any web application, POS system, or browser-based frontend to silently print "
            "receipts and Kitchen Order Tickets (KOTs) to a connected thermal printer — "
            "<b>with no browser print dialog.</b>", BODY),
        Paragraph(
            "Jobs are placed in an in-memory queue and dispatched to the printer asynchronously "
            "using raw ESC/POS bytes via the Windows spooler (win32print). "
            "The server runs as a background process and opens a browser dashboard on startup.", BODY),
        Spacer(1, 0.3*cm),
    ]

    # Architecture
    story.append(Paragraph("Architecture Overview", H2))
    arch = [
        [Paragraph(h, S("th", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white)) for h in ("Layer", "File", "Role")],
        [Paragraph("Entry Point", BODY_SMALL),
         Paragraph("main.py", MONO),
         Paragraph("Starts Flask server + system tray icon (pystray)", BODY_SMALL)],
        [Paragraph("HTTP Server", BODY_SMALL),
         Paragraph("server.py", MONO),
         Paragraph("Flask REST API — defines /print, /queue, /jobs routes", BODY_SMALL)],
        [Paragraph("Job Queue", BODY_SMALL),
         Paragraph("queue.py", MONO),
         Paragraph("In-memory job queue with status tracking", BODY_SMALL)],
        [Paragraph("Printer Layer", BODY_SMALL),
         Paragraph("printer_manager.py", MONO),
         Paragraph("win32print wrapper — sends raw bytes to printers", BODY_SMALL)],
        [Paragraph("Formatter", BODY_SMALL),
         Paragraph("universal_formatter.py", MONO),
         Paragraph("Converts plain-text content → ESC/POS bytes", BODY_SMALL)],
        [Paragraph("Dashboard", BODY_SMALL),
         Paragraph("templates/index.html", MONO),
         Paragraph("Browser UI for status, queue, and test prints", BODY_SMALL)],
    ]
    arch_t = Table(arch, colWidths=[2.8*cm, 4.2*cm, W - 7*cm])
    arch_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [arch_t, Spacer(1, 0.4*cm)]

    story.append(Paragraph("Request Flow", H2))
    story.append(code(
"  Your App / POS / Browser\n"
"         │\n"
"         │  HTTP POST  { \"type\": \"RECEIPT\", \"content\": \"...\" }\n"
"         ▼\n"
"  PrintBridge  (localhost:5000)\n"
"         │\n"
"         ├──  Validate type & content\n"
"         ├──  Enqueue job  →  queue.py\n"
"         ├──  universal_formatter.py  →  ESC/POS bytes\n"
"         └──  printer_manager.py  →  win32print  →  🖨️  Thermal Printer"
    ))

    # ══════════════════════════════════════════════════
    # 2. QUICK START
    # ══════════════════════════════════════════════════
    story += [
        Paragraph("2. Quick Start", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.2*cm),
        Paragraph("Step 1 — Run the server", H2),
        code("python main.py"),
        Paragraph("Step 2 — Server is live at:", H2),
        code("http://localhost:5000"),
        Paragraph("Step 3 — Open Dashboard", H2),
        Paragraph(
            "The server automatically opens the dashboard in your browser 1.5 s after startup. "
            "You can also navigate there manually.", BODY),
        Spacer(1, 0.3*cm),
    ]

    # ══════════════════════════════════════════════════
    # 3. BASE URL & HEADERS
    # ══════════════════════════════════════════════════
    story += [
        Paragraph("3. Base URL &amp; Request Headers", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.2*cm),
    ]
    hdr = [
        [Paragraph(h, S("th", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white)) for h in ("Item", "Value")],
        [Paragraph("Base URL", BODY_SMALL), Paragraph("http://localhost:5000", MONO)],
        [Paragraph("Content-Type (POST)", BODY_SMALL), Paragraph("application/json", MONO)],
        [Paragraph("Accept", BODY_SMALL), Paragraph("application/json", MONO)],
        [Paragraph("CORS", BODY_SMALL), Paragraph("All origins allowed (*)", BODY_SMALL)],
        [Paragraph("Authentication", BODY_SMALL), Paragraph("None required (local service)", BODY_SMALL)],
    ]
    hdr_t = Table(hdr, colWidths=[5*cm, W - 5*cm])
    hdr_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 9),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [hdr_t, Spacer(1, 0.4*cm)]

    # ══════════════════════════════════════════════════
    # 4. VALID DOCUMENT TYPES
    # ══════════════════════════════════════════════════
    story += [
        Paragraph("4. Document Types (type field)", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.15*cm),
        Paragraph(
            'The <b>type</b> field in <b>POST /print</b> controls how the content is formatted '
            'and printed. It must be one of the following values (case-insensitive):', BODY),
        Spacer(1, 0.15*cm),
    ]
    types = [
        [Paragraph(h, S("th", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white)) for h in ("Type Value", "Description", "Use Case")],
        [Paragraph("RECEIPT", MONO),
         Paragraph("Customer payment receipt with itemised bill and total", BODY_SMALL),
         Paragraph("End-of-order customer copy", BODY_SMALL)],
        [Paragraph("KOT", MONO),
         Paragraph("Kitchen Order Ticket — items grouped by station, no prices", BODY_SMALL),
         Paragraph("Kitchen / prep station slip", BODY_SMALL)],
        [Paragraph("LABEL", MONO),
         Paragraph("Short label or tag slip (compact format)", BODY_SMALL),
         Paragraph("Product labels, takeaway stickers", BODY_SMALL)],
        [Paragraph("REPORT", MONO),
         Paragraph("End-of-day or shift report (plain text, wide format)", BODY_SMALL),
         Paragraph("Daily sales summary printout", BODY_SMALL)],
    ]
    types_t = Table(types, colWidths=[2.5*cm, 7*cm, W - 9.5*cm])
    types_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [types_t, Spacer(1, 0.5*cm)]

    # ══════════════════════════════════════════════════
    # 5. API REFERENCE
    # ══════════════════════════════════════════════════
    story += [
        Paragraph("5. API Reference", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.2*cm),
    ]

    # ── 5.1  POST /print ──────────────────────────────
    story += [
        Paragraph("5.1  Submit a Print Job", H2),
        KeepTogether([
            endpoint_header("POST", "/print"),
            Spacer(1, 0.15*cm),
            Paragraph(
                "Accepts a JSON body with a document <b>type</b> and a <b>content</b> string. "
                "The server validates the input, places the job in the queue, and asynchronously "
                "dispatches it to the configured printer.", BODY),
        ]),
        Spacer(1, 0.25*cm),
        Paragraph("Request Body Fields", H3),
        fields_table([
            ("type", "string", "✅ Required",
             "Document type. Must be one of: RECEIPT, KOT, LABEL, REPORT (case-insensitive)"),
            ("content", "string", "✅ Required",
             "The text content to print. Must not be empty. Plain text; ESC/POS formatting is "
             "applied automatically based on the type."),
        ]),
        Spacer(1, 0.3*cm),
        Paragraph("Example Request", H3),
        code(
'POST http://localhost:5000/print\n'
'Content-Type: application/json\n\n'
'{\n'
'  "type": "RECEIPT",\n'
'  "content": "Chai Point\\nOrder #42\\nMasala Chai x2  Rs.80\\nTotal: Rs.80"\n'
'}'
        ),
        Paragraph("Success Response  (HTTP 200)", H3),
        code(
'{\n'
'  "status": "success",\n'
'  "message": "Job queued",\n'
'  "job": {\n'
'    "id": "a1b2c3d4",\n'
'    "type": "RECEIPT",\n'
'    "status": "queued",\n'
'    "created_at": "2024-04-02T10:30:00"\n'
'  },\n'
'  "printer": "connected",\n'
'  "queue_depth": 1\n'
'}'
        ),
        Paragraph("Success Response Fields", H3),
        response_table([
            ("status", "string", '"success" on successful queue insertion'),
            ("message", "string", 'Human-readable confirmation: "Job queued"'),
            ("job", "object", "Job details — id, type, current status, and created_at timestamp"),
            ("job.id", "string", "Unique job identifier (UUID or short hash)"),
            ("job.type", "string", "Document type as submitted (uppercased)"),
            ("job.status", "string", '"queued", "printing", "done", or "failed"'),
            ("job.created_at", "string", "ISO 8601 timestamp of when the job was created"),
            ("printer", "string", '"connected" if the printer is reachable, "disconnected" otherwise'),
            ("queue_depth", "integer", "Number of jobs currently waiting in the queue after this one"),
        ]),
        Spacer(1, 0.3*cm),
        Paragraph("KOT Example", H3),
        code(
'POST http://localhost:5000/print\n'
'Content-Type: application/json\n\n'
'{\n'
'  "type": "KOT",\n'
'  "content": "Table 5 | Order #55\\nMasala Chai x2\\nVeg Sandwich x1\\nNote: No onions"\n'
'}'
        ),
        Spacer(1, 0.5*cm),
    ]

    # ── 5.2  GET /queue ───────────────────────────────
    story += [
        Paragraph("5.2  Get Queue Depth", H2),
        KeepTogether([
            endpoint_header("GET", "/queue"),
            Spacer(1, 0.15*cm),
            Paragraph(
                "Returns the number of jobs currently waiting in the print queue. "
                "Useful for health checks and monitoring.", BODY),
        ]),
        Spacer(1, 0.25*cm),
        Paragraph("Example Request", H3),
        code("GET http://localhost:5000/queue\n\n(No body required)"),
        Paragraph("Response  (HTTP 200)", H3),
        code(
'{\n'
'  "status": "ok",\n'
'  "queue_depth": 3\n'
'}'
        ),
        Paragraph("Response Fields", H3),
        response_table([
            ("status", "string", '"ok" — always returns 200 unless server is down'),
            ("queue_depth", "integer",
             "Current number of jobs pending in the queue. 0 means the queue is empty."),
        ]),
        Spacer(1, 0.5*cm),
    ]

    # ── 5.3  GET /jobs ────────────────────────────────
    story += [
        Paragraph("5.3  List Recent Jobs", H2),
        KeepTogether([
            endpoint_header("GET", "/jobs"),
            Spacer(1, 0.15*cm),
            Paragraph(
                "Returns a list of recently processed print jobs. "
                "Supports an optional <b>limit</b> query parameter to control how many jobs are returned.", BODY),
        ]),
        Spacer(1, 0.25*cm),
        Paragraph("Query Parameters", H3),
        fields_table(
            [("limit", "integer", "Optional",
              "Number of recent jobs to return. Default: 20. Min: 1. Max: 100. "
              "Values outside range are clamped automatically.")],
            headers=("Parameter", "Type", "Required", "Description")
        ),
        Spacer(1, 0.3*cm),
        Paragraph("Example Requests", H3),
        code(
'# Default (last 20 jobs)\nGET http://localhost:5000/jobs\n\n'
'# Last 5 jobs only\nGET http://localhost:5000/jobs?limit=5\n\n'
'# Maximum (last 100 jobs)\nGET http://localhost:5000/jobs?limit=100'
        ),
        Paragraph("Response  (HTTP 200)", H3),
        code(
'{\n'
'  "status": "ok",\n'
'  "jobs": [\n'
'    {\n'
'      "id": "a1b2c3d4",\n'
'      "type": "RECEIPT",\n'
'      "status": "done",\n'
'      "created_at": "2024-04-02T10:30:00"\n'
'    },\n'
'    {\n'
'      "id": "e5f6a7b8",\n'
'      "type": "KOT",\n'
'      "status": "done",\n'
'      "created_at": "2024-04-02T10:29:45"\n'
'    }\n'
'  ],\n'
'  "queue_depth": 0\n'
'}'
        ),
        Paragraph("Response Fields", H3),
        response_table([
            ("status", "string", '"ok" — always 200'),
            ("jobs", "array", "Array of job objects ordered newest-first"),
            ("jobs[].id", "string", "Unique job identifier"),
            ("jobs[].type", "string", "Document type — RECEIPT, KOT, LABEL, or REPORT"),
            ("jobs[].status", "string", '"queued", "printing", "done", or "failed"'),
            ("jobs[].created_at", "string", "ISO 8601 timestamp"),
            ("queue_depth", "integer", "Current number of pending jobs at time of response"),
        ]),
        Spacer(1, 0.5*cm),
    ]

    # ══════════════════════════════════════════════════
    # 6. ERROR REFERENCE
    # ══════════════════════════════════════════════════
    story += [
        Paragraph("6. Error Reference", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.15*cm),
        Paragraph("All errors follow the same envelope:", BODY),
        code('{ "status": "error", "message": "<human-readable description>" }'),
    ]

    err_rows = [
        ("400", "Content-Type not application/json",
         "Set header Content-Type: application/json on your POST request"),
        ("400", "Malformed JSON body",
         "Ensure the request body is valid JSON (check commas, brackets, quotes)"),
        ("405", "Wrong HTTP method used",
         "POST /print only accepts POST. GET /queue and GET /jobs only accept GET."),
        ("422", "Invalid type value",
         "Use one of: RECEIPT, KOT, LABEL, REPORT (case-insensitive)"),
        ("422", "Empty content field",
         'The "content" field must not be an empty string'),
        ("500", "Printer / spooler error",
         "Check printer is online and connected. See printbridge.log for details."),
    ]
    err_hdr = [Paragraph(h, S("th", fontName="Helvetica-Bold", fontSize=9,
        textColor=colors.white)) for h in ("HTTP", "Scenario", "Fix")]
    err_data = [err_hdr] + [
        [Paragraph(r[0], S("ec", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white, alignment=TA_CENTER)),
         Paragraph(r[1], BODY_SMALL),
         Paragraph(r[2], BODY_SMALL)]
        for r in err_rows
    ]
    err_bg = {
        "400": colors.HexColor("#B45309"),
        "405": colors.HexColor("#7C3AED"),
        "422": colors.HexColor("#C2410C"),
        "500": colors.HexColor("#991B1B"),
    }
    err_t = Table(err_data, colWidths=[1.3*cm, 6*cm, W - 7.3*cm])
    err_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#7F1D1D")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#FFF1F2")]),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("ALIGN", (0,0), (0,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BACKGROUND", (0,1), (0,2), err_bg["400"]),
        ("BACKGROUND", (0,3), (0,3), err_bg["405"]),
        ("BACKGROUND", (0,4), (0,5), err_bg["422"]),
        ("BACKGROUND", (0,6), (0,6), err_bg["500"]),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [err_t, Spacer(1, 0.5*cm)]

    # Error examples
    story += [
        Paragraph("Error Response Examples", H2),
        code(
'// 400 — missing Content-Type\n'
'{ "status": "error", "message": "Request Content-Type must be application/json." }\n\n'
'// 422 — bad type\n'
'{ "status": "error", "message": "Invalid \'type\': \'BILL\'. Must be one of [\'KOT\', \'LABEL\', \'RECEIPT\', \'REPORT\']." }\n\n'
'// 422 — empty content\n'
'{ "status": "error", "message": "\'content\' must not be empty." }\n\n'
'// 500 — printer error\n'
'{ "status": "error", "message": "win32print: printer not found" }'
        ),
        Spacer(1, 0.5*cm),
    ]

    # ══════════════════════════════════════════════════
    # 7. POSTMAN GUIDE
    # ══════════════════════════════════════════════════
    story += [
        Paragraph("7. Postman Quick Setup", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.2*cm),
    ]
    steps = [
        ("1", "Create a Collection", "Name it 'PrintBridge'"),
        ("2", "Add Request — Send a Print Job",
         "Method: POST  |  URL: http://localhost:5000/print"),
        ("3", "Set Body",
         "Body tab → raw → JSON → paste:\n"
         '{ "type": "RECEIPT", "content": "Test receipt\\nItem 1 x1  Rs.50\\nTotal: Rs.50" }'),
        ("4", "Set Header", "Headers tab → Add:  Content-Type = application/json"),
        ("5", "Send", 'Click Send → expect { "status": "success", "message": "Job queued" }'),
        ("6", "Check Queue",
         "Add new GET request:  http://localhost:5000/queue  → shows current queue depth"),
        ("7", "Check Jobs",
         "Add new GET request:  http://localhost:5000/jobs?limit=5  → shows last 5 jobs"),
    ]
    step_data = [[Paragraph(h, S("th", fontName="Helvetica-Bold", fontSize=9,
        textColor=colors.white)) for h in ("Step", "Action", "Details")]]
    for num, action, detail in steps:
        step_data.append([
            Paragraph(num, S("sn", fontName="Helvetica-Bold", fontSize=13,
                textColor=BLUE, alignment=TA_CENTER)),
            Paragraph(f"<b>{action}</b>", BODY_SMALL),
            Paragraph(detail, BODY_SMALL),
        ])
    step_t = Table(step_data, colWidths=[1.1*cm, 4.5*cm, W - 5.6*cm])
    step_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("ALIGN", (0,0), (0,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    story += [step_t, Spacer(1, 0.5*cm)]

    # ══════════════════════════════════════════════════
    # 8. FULL ENDPOINT SUMMARY
    # ══════════════════════════════════════════════════
    story += [
        Paragraph("8. Endpoint Summary", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.15*cm),
    ]
    summ_data = [
        [Paragraph(h, S("th", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white)) for h in ("Method", "Endpoint", "Body / Params", "Returns")],
        [Paragraph("POST", S("m", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white, alignment=TA_CENTER)),
         Paragraph("/print", MONO),
         Paragraph('{ "type": "...", "content": "..." }', MONO),
         Paragraph("Job object + printer status + queue depth", BODY_SMALL)],
        [Paragraph("GET", S("g", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white, alignment=TA_CENTER)),
         Paragraph("/queue", MONO),
         Paragraph("—", BODY_SMALL),
         Paragraph("Current queue depth", BODY_SMALL)],
        [Paragraph("GET", S("g2", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white, alignment=TA_CENTER)),
         Paragraph("/jobs", MONO),
         Paragraph("?limit=N  (1–100, default 20)", MONO),
         Paragraph("List of recent job objects", BODY_SMALL)],
    ]
    summ_t = Table(summ_data, colWidths=[1.5*cm, 2.2*cm, 5.5*cm, W - 9.2*cm])
    summ_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
        ("BACKGROUND", (0,1), (0,1), BLUE),
        ("BACKGROUND", (0,2), (0,3), GREEN),
        ("ROWBACKGROUNDS", (1,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("ALIGN", (0,1), (0,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    story += [summ_t, Spacer(1, 0.5*cm)]

    # ══════════════════════════════════════════════════
    # FOOTER
    # ══════════════════════════════════════════════════
    story += [
        HRFlowable(width="100%", thickness=1, color=MID_GRAY),
        Spacer(1, 0.1*cm),
        Paragraph(
            f"PrintBridge v1.0.0  •  Generated {datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')}  •  Internal Use Only",
            S("footer", fontName="Helvetica", fontSize=8, textColor=GRAY, alignment=TA_CENTER)
        ),
    ]

    doc.build(story)
    print(f"✅  PDF generated → {OUTPUT}")


if __name__ == "__main__":
    build()
