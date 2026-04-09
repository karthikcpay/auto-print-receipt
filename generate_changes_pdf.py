"""
Generate PrintBridge Changes Summary PDF.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Preformatted, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import datetime

OUTPUT = "PrintBridge_Changes_Summary.pdf"

W = A4[0] - 4*cm

DARK_BLUE   = colors.HexColor("#1E3A8A")
BLUE        = colors.HexColor("#2563EB")
LIGHT_BLUE  = colors.HexColor("#DBEAFE")
GREEN       = colors.HexColor("#16A34A")
LIGHT_GREEN = colors.HexColor("#DCFCE7")
ORANGE      = colors.HexColor("#D97706")
LIGHT_ORANGE= colors.HexColor("#FEF3C7")
RED         = colors.HexColor("#DC2626")
LIGHT_RED   = colors.HexColor("#FEE2E2")
GRAY        = colors.HexColor("#6B7280")
LIGHT_GRAY  = colors.HexColor("#F9FAFB")
DARK        = colors.HexColor("#111827")
MID_GRAY    = colors.HexColor("#E5E7EB")
CODE_BG     = colors.HexColor("#1E1E2E")
CODE_FG     = colors.HexColor("#CDD6F4")
ADD_BG      = colors.HexColor("#F0FDF4")
ADD_FG      = colors.HexColor("#15803D")
DEL_BG      = colors.HexColor("#FFF1F2")
DEL_FG      = colors.HexColor("#BE123C")
MOD_BG      = colors.HexColor("#FFFBEB")
MOD_FG      = colors.HexColor("#92400E")

def S(name, **kw):
    return ParagraphStyle(name, **kw)

TITLE    = S("T", fontName="Helvetica-Bold", fontSize=28, textColor=colors.white,
             alignment=TA_CENTER, leading=34, spaceAfter=4)
SUBTITLE = S("ST", fontName="Helvetica", fontSize=12,
             textColor=colors.HexColor("#BFDBFE"), alignment=TA_CENTER, spaceAfter=2)
H1       = S("H1", fontName="Helvetica-Bold", fontSize=16, textColor=DARK_BLUE,
             spaceBefore=16, spaceAfter=6, leading=21)
H2       = S("H2", fontName="Helvetica-Bold", fontSize=12, textColor=BLUE,
             spaceBefore=10, spaceAfter=4, leading=16)
H3       = S("H3", fontName="Helvetica-Bold", fontSize=10, textColor=DARK,
             spaceBefore=6, spaceAfter=3, leading=14)
BODY     = S("B", fontName="Helvetica", fontSize=10, textColor=DARK,
             spaceAfter=4, leading=15)
SMALL    = S("SM", fontName="Helvetica", fontSize=9, textColor=GRAY,
             spaceAfter=3, leading=13)
MONO     = S("MN", fontName="Courier", fontSize=9, textColor=DARK,
             spaceAfter=3, leading=13)

def code(text):
    return Preformatted(text, ParagraphStyle(
        "code", fontName="Courier", fontSize=8, textColor=CODE_FG,
        backColor=CODE_BG, leading=12, leftIndent=8, rightIndent=8,
        spaceBefore=4, spaceAfter=8,
    ))

def badge_row(tag, text, bg, fg=colors.white, text_bg=None):
    """A coloured badge + description row."""
    data = [[
        Paragraph(tag, S("bd", fontName="Helvetica-Bold", fontSize=8,
            textColor=fg, alignment=TA_CENTER)),
        Paragraph(text, S("bt", fontName="Helvetica", fontSize=9,
            textColor=DARK, leading=13)),
    ]]
    t = Table(data, colWidths=[1.4*cm, W - 1.4*cm], rowHeights=[0.55*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), bg),
        ("BACKGROUND", (1,0), (1,0), text_bg or colors.white),
        ("ALIGN", (0,0), (0,0), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (1,0), (1,0), 10),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return t

def section_header(title, icon=""):
    data = [[Paragraph(f"{icon}  {title}" if icon else title,
        S("sh", fontName="Helvetica-Bold", fontSize=11, textColor=colors.white))]]
    t = Table(data, colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_BLUE),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    return t

def change_table(rows):
    """rows: list of (file, type, description) tuples"""
    TYPE_COLORS = {
        "ADDED":    (GREEN,  LIGHT_GREEN),
        "MODIFIED": (ORANGE, LIGHT_ORANGE),
        "REMOVED":  (RED,    LIGHT_RED),
        "INSTALLED":(BLUE,   LIGHT_BLUE),
    }
    hdr = [Paragraph(h, S("th", fontName="Helvetica-Bold", fontSize=9,
        textColor=colors.white)) for h in ("File / Item", "Change", "Description")]
    data = [hdr]
    for file, typ, desc in rows:
        bg, lbg = TYPE_COLORS.get(typ, (GRAY, LIGHT_GRAY))
        data.append([
            Paragraph(file, MONO),
            Paragraph(typ, S("tp", fontName="Helvetica-Bold", fontSize=8,
                textColor=colors.white, alignment=TA_CENTER)),
            Paragraph(desc, SMALL),
        ])
    t = Table(data, colWidths=[4.5*cm, 1.8*cm, W - 6.3*cm], repeatRows=1)
    style = [
        ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("ALIGN", (1,1), (1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]
    type_color_map = {
        "ADDED":     GREEN,
        "MODIFIED":  ORANGE,
        "REMOVED":   RED,
        "INSTALLED": BLUE,
    }
    for i, (_, typ, _) in enumerate(rows, start=1):
        bg = type_color_map.get(typ, GRAY)
        row_bg = {
            "ADDED":     ADD_BG,
            "MODIFIED":  MOD_BG,
            "REMOVED":   DEL_BG,
            "INSTALLED": LIGHT_BLUE,
        }.get(typ, LIGHT_GRAY)
        style.append(("BACKGROUND", (1,i), (1,i), bg))
        style.append(("ROWBACKGROUNDS", (0,i), (0,i), [row_bg]))
        style.append(("ROWBACKGROUNDS", (2,i), (2,i), [row_bg]))
    t.setStyle(TableStyle(style))
    return t


def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    story = []

    # ── Cover ─────────────────────────────────────────
    cover = Table([[
        Paragraph("📋  PrintBridge", TITLE),
        Paragraph("Changes Summary", SUBTITLE),
        Paragraph("What was modified &amp; why", SUBTITLE),
        Spacer(1, 0.3*cm),
        Paragraph(
            f"Session: {datetime.date.today().strftime('%B %d, %Y')}  •  v1.0.0",
            S("d", fontName="Helvetica", fontSize=10,
              textColor=colors.HexColor("#93C5FD"), alignment=TA_CENTER)),
    ]], colWidths=[W])
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_BLUE),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 28),
        ("BOTTOMPADDING", (0,0), (-1,-1), 28),
        ("LEFTPADDING", (0,0), (-1,-1), 20),
        ("RIGHTPADDING", (0,0), (-1,-1), 20),
    ]))
    story += [cover, Spacer(1, 0.7*cm)]

    # ── Summary Stats ──────────────────────────────────
    story += [
        Paragraph("Overview", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.2*cm),
        Paragraph(
            "This document summarises all changes made to the PrintBridge project during this "
            "session including new files, modifications to existing code, dependencies installed, "
            "and the new API contract.", BODY),
        Spacer(1, 0.2*cm),
    ]

    stats = [
        [Paragraph(h, S("th", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white)) for h in ("Category", "Count", "Items")],
        [Paragraph("Files Modified", SMALL), Paragraph("2", S("n", fontName="Helvetica-Bold",
            fontSize=12, textColor=ORANGE, alignment=TA_CENTER)),
         Paragraph("main.py, generate_docs.py", MONO)],
        [Paragraph("Files Created", SMALL), Paragraph("2", S("n", fontName="Helvetica-Bold",
            fontSize=12, textColor=GREEN, alignment=TA_CENTER)),
         Paragraph("printbridge.spec, PrintBridge_API_Documentation.pdf", MONO)],
        [Paragraph("Packages Installed", SMALL), Paragraph("4", S("n", fontName="Helvetica-Bold",
            fontSize=12, textColor=BLUE, alignment=TA_CENTER)),
         Paragraph("pystray, Pillow, pywin32, reportlab", MONO)],
        [Paragraph("EXE Rebuilt", SMALL), Paragraph("3×", S("n", fontName="Helvetica-Bold",
            fontSize=12, textColor=BLUE, alignment=TA_CENTER)),
         Paragraph("dist/printbridge.exe  (final: 20.36 MB)", MONO)],
        [Paragraph("API Endpoints Documented", SMALL), Paragraph("3", S("n", fontName="Helvetica-Bold",
            fontSize=12, textColor=PURPLE if False else DARK_BLUE, alignment=TA_CENTER)),
         Paragraph("POST /print  •  GET /queue  •  GET /jobs", MONO)],
    ]

    stats_t = Table(stats, colWidths=[4*cm, 1.5*cm, W - 5.5*cm])
    stats_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("ALIGN", (1,1), (1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [stats_t, Spacer(1, 0.5*cm)]

    # ── Change 1: main.py ──────────────────────────────
    story += [
        Paragraph("1. main.py — Auto-Open Browser on Startup", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.15*cm),
        Paragraph(
            "<b>Problem:</b> The EXE ran silently with no visible window. Users double-clicked it "
            "and saw nothing, leading to multiple background instances piling up.", BODY),
        Paragraph(
            "<b>Fix:</b> Added a <b>_open_browser_delayed()</b> function that waits 1.5 seconds "
            "(for the Flask server to start) and then automatically opens "
            "<b>http://localhost:5000</b> in the default browser. This gives the user immediate "
            "visual feedback that the server is running.", BODY),
        Spacer(1, 0.2*cm),
        Paragraph("Code Added", H3),
        code(
'# NEW function added to main.py\n'
'def _open_browser_delayed(url, delay=1.5):\n'
'    """Open browser after a short delay to let the server start."""\n'
'    import time\n'
'    time.sleep(delay)\n'
'    try:\n'
'        webbrowser.open(url)\n'
'    except Exception as e:\n'
'        logger.warning(f"Could not open browser: {e}")\n'
'\n'
'# Inside main() — new lines added:\n'
'url = f\'http://localhost:{port}\'   # <-- moved here\n'
'browser_thread = threading.Thread(\n'
'    target=_open_browser_delayed, args=(url,), daemon=True\n'
')\n'
'browser_thread.start()             # <-- auto-opens browser 1.5s after start'
        ),
        Spacer(1, 0.2*cm),
        Paragraph("Before vs After", H3),
    ]

    bva = [
        [Paragraph("BEFORE", S("bh", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white, alignment=TA_CENTER)),
         Paragraph("AFTER", S("ah", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white, alignment=TA_CENTER))],
        [Paragraph("Double-clicking exe opened nothing visible", SMALL),
         Paragraph("Browser auto-opens to dashboard after 1.5 s", SMALL)],
        [Paragraph("Multiple silent instances accumulated in background", SMALL),
         Paragraph("User immediately sees the server is running", SMALL)],
        [Paragraph("Had to check Task Manager to confirm it was running", SMALL),
         Paragraph("Dashboard at localhost:5000 confirms server status", SMALL)],
    ]
    bva_t = Table(bva, colWidths=[W/2, W/2])
    bva_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), RED),
        ("BACKGROUND", (1,0), (1,0), GREEN),
        ("ROWBACKGROUNDS", (0,1), (0,-1), [DEL_BG]),
        ("ROWBACKGROUNDS", (1,1), (1,-1), [ADD_BG]),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("ALIGN", (0,0), (-1,0), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [bva_t, Spacer(1, 0.5*cm)]

    # ── Change 2: printbridge.spec ─────────────────────
    story += [
        Paragraph("2. printbridge.spec — PyInstaller Build Configuration", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.15*cm),
        Paragraph(
            "<b>Problem:</b> The first EXE build failed silently because pywin32 DLLs, "
            "pystray, and Pillow were not being bundled — they showed as missing at runtime.", BODY),
        Paragraph("<b>Changes made to the spec file:", BODY),
        Spacer(1, 0.1*cm),
    ]

    spec_changes = [
        ("Explicit pywin32 DLL paths",
         "Added binaries[] list that scans pywin32_system32/ and win32/ folders and "
         "includes every .dll and .pyd file explicitly."),
        ("pathex[] expanded",
         "Added the pywin32 site-packages directory and subdirectories to pathex so "
         "PyInstaller can resolve all imports."),
        ("collect_submodules() for pystray & PIL",
         "Used PyInstaller's collect_submodules() to gather every submodule of pystray "
         "and Pillow — they were being missed with simple string hidden imports."),
        ("upx=False",
         "Disabled UPX compression. UPX was corrupting the pywin32 DLL extraction on some "
         "machines, causing silent crashes at startup."),
        ("console=True",
         "Switched from console=False (silent) to console=True so a terminal window is "
         "visible. Users can now see the server is running and any startup errors."),
    ]

    for title, desc in spec_changes:
        story.append(badge_row("CHANGE", f"<b>{title}</b> — {desc}", ORANGE, text_bg=MOD_BG))
        story.append(Spacer(1, 0.08*cm))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Key Spec Snippets", H3))
    story.append(code(
'# Explicit pywin32 DLLs (prevents "win32print not found" error in exe)\n'
'extra_binaries = []\n'
'for dll_dir in [pywin32_dll_dir, win32_dir]:\n'
'    for fn in os.listdir(dll_dir):\n'
'        if fn.endswith(\'.dll\') or fn.endswith(\'.pyd\'):\n'
'            extra_binaries.append((os.path.join(dll_dir, fn), \'.\'))\n'
'\n'
'# In EXE() block:\n'
'upx=False,       # was True — UPX breaks pywin32 DLLs\n'
'console=True,    # was False — now shows terminal so user knows it\'s running'
    ))
    story.append(Spacer(1, 0.5*cm))

    # ── Change 3: Dependencies ─────────────────────────
    story += [
        Paragraph("3. Dependencies Installed", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.15*cm),
        Paragraph(
            "The following packages were missing from the environment and were installed "
            "before the final EXE build could succeed:", BODY),
        Spacer(1, 0.15*cm),
    ]

    deps = [
        [Paragraph(h, S("th", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white)) for h in ("Package", "Version", "Why Needed")],
        [Paragraph("pystray", MONO), Paragraph("latest", SMALL),
         Paragraph("System tray icon — lets the EXE live in the Windows taskbar tray", SMALL)],
        [Paragraph("Pillow (PIL)", MONO), Paragraph("latest", SMALL),
         Paragraph("Required by pystray to render the tray icon image", SMALL)],
        [Paragraph("pywin32", MONO), Paragraph("latest", SMALL),
         Paragraph("win32print — sends raw ESC/POS bytes to the Windows print spooler", SMALL)],
        [Paragraph("reportlab", MONO), Paragraph("latest", SMALL),
         Paragraph("PDF generation library used by generate_docs.py", SMALL)],
        [Paragraph("pyinstaller", MONO), Paragraph("6.19.0", SMALL),
         Paragraph("Packages the Python app into a standalone Windows EXE", SMALL)],
    ]
    deps_t = Table(deps, colWidths=[2.8*cm, 2*cm, W - 4.8*cm])
    deps_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT_BLUE]),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [deps_t, Spacer(1, 0.5*cm)]

    # ── Change 4: API Documentation ───────────────────
    story += [
        Paragraph("4. generate_docs.py — API Documentation Updated", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.15*cm),
        Paragraph(
            "The PDF documentation was completely rewritten to reflect the new API contract. "
            "The old API used a single complex JSON payload. The new API uses a simple "
            "<b>type + content</b> model with dedicated queue and job management endpoints.", BODY),
        Spacer(1, 0.2*cm),
    ]

    api_diff = [
        [Paragraph(h, S("th", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white)) for h in ("Old API", "New API")],
        [Paragraph("POST /api/print", MONO), Paragraph("POST /print", MONO)],
        [Paragraph('Body: complex nested JSON with\nbusinessName, items[], otherCharges[]…',
            SMALL), Paragraph('Body: { "type": "RECEIPT", "content": "..." }', MONO)],
        [Paragraph("POST /api/print/receipt  (alias)", MONO),
         Paragraph("GET /queue  — queue depth", MONO)],
        [Paragraph("POST /api/print/kot  (alias)", MONO),
         Paragraph("GET /jobs?limit=N  — recent job history", MONO)],
        [Paragraph("GET /api/status", MONO),
         Paragraph("Job object returned on every POST /print", MONO)],
        [Paragraph("GET /api/printers", MONO), Paragraph("(accessible via dashboard)", SMALL)],
        [Paragraph("GET/POST /api/config", MONO), Paragraph("(accessible via dashboard)", SMALL)],
        [Paragraph("POST /api/test-print", MONO), Paragraph("(accessible via dashboard)", SMALL)],
    ]
    diff_t = Table(api_diff, colWidths=[W/2, W/2])
    diff_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), RED),
        ("BACKGROUND", (1,0), (1,0), GREEN),
        ("ROWBACKGROUNDS", (0,1), (0,-1), [DEL_BG]),
        ("ROWBACKGROUNDS", (1,1), (1,-1), [ADD_BG]),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("ALIGN", (0,0), (-1,0), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [diff_t, Spacer(1, 0.4*cm)]

    story += [
        Paragraph("New API Documented in PDF", H3),
        Paragraph("The updated <b>PrintBridge_API_Documentation.pdf</b> now covers:", BODY),
        Spacer(1, 0.1*cm),
    ]

    new_sections = [
        ("POST /print", "Full body fields, valid types, job response object, RECEIPT & KOT examples"),
        ("GET /queue",  "Queue depth response, use in health checks"),
        ("GET /jobs",   "?limit parameter (1–100), full job list response"),
        ("Error Reference", "All 400/405/422/500 errors with exact message strings"),
        ("Postman Guide",   "7-step guide to test all 3 endpoints"),
        ("Endpoint Summary","Quick-reference table of all endpoints"),
        ("Document Types",  "Table of RECEIPT, KOT, LABEL, REPORT with descriptions"),
    ]
    for ep, desc in new_sections:
        story.append(badge_row("NEW", f"<b>{ep}</b> — {desc}", GREEN, text_bg=ADD_BG))
        story.append(Spacer(1, 0.06*cm))

    story.append(Spacer(1, 0.5*cm))

    # ── Change 5: EXE Rebuild History ─────────────────
    story += [
        Paragraph("5. EXE Build History", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.15*cm),
    ]
    builds = [
        [Paragraph(h, S("th", fontName="Helvetica-Bold", fontSize=9,
            textColor=colors.white)) for h in ("#", "Time", "Size", "Outcome", "Issue / Fix")],
        [Paragraph("1", SMALL), Paragraph("15:08", SMALL), Paragraph("19.44 MB", SMALL),
         Paragraph("❌ Failed", S("f", fontName="Helvetica", fontSize=9, textColor=RED)),
         Paragraph("pystray/pywin32 not installed — missing at runtime", SMALL)],
        [Paragraph("2", SMALL), Paragraph("15:33", SMALL), Paragraph("20.35 MB", SMALL),
         Paragraph("⚠️ Partial", S("f", fontName="Helvetica", fontSize=9, textColor=ORANGE)),
         Paragraph("File locked (old instances running) — PermissionError on overwrite", SMALL)],
        [Paragraph("3", SMALL), Paragraph("16:22", SMALL), Paragraph("20.36 MB", SMALL),
         Paragraph("✅ Success", S("f", fontName="Helvetica", fontSize=9, textColor=GREEN)),
         Paragraph("Old instances killed + all DLLs bundled + console=True", SMALL)],
    ]
    builds_t = Table(builds, colWidths=[0.6*cm, 1.5*cm, 2.2*cm, 2*cm, W - 6.3*cm])
    builds_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
        ("ROWBACKGROUNDS", (0,1), (0,1), [DEL_BG]),
        ("ROWBACKGROUNDS", (0,2), (0,2), [MOD_BG]),
        ("ROWBACKGROUNDS", (0,3), (0,3), [ADD_BG]),
        ("GRID", (0,0), (-1,-1), 0.4, MID_GRAY),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story += [builds_t, Spacer(1, 0.5*cm)]

    # ── Final File List ────────────────────────────────
    story += [
        Paragraph("6. Deliverables", H1),
        HRFlowable(width="100%", thickness=1.5, color=BLUE),
        Spacer(1, 0.15*cm),
        change_table([
            ("dist\\printbridge.exe",               "ADDED",    "Standalone Windows EXE — 20.36 MB. Double-click to launch. Opens browser dashboard automatically."),
            ("printbridge.spec",                    "ADDED",    "PyInstaller spec file with explicit pywin32 DLLs, pystray, Pillow, templates bundled."),
            ("PrintBridge_API_Documentation.pdf",   "ADDED",    "Full API reference PDF — new /print, /queue, /jobs endpoints with Postman guide."),
            ("PrintBridge_Changes_Summary.pdf",     "ADDED",    "This document — summary of all changes made during this session."),
            ("main.py",                             "MODIFIED", "Added _open_browser_delayed() and browser_thread to auto-open dashboard on startup."),
            ("generate_docs.py",                    "MODIFIED", "Fully rewritten to document the new API contract (type+content model)."),
            ("pystray",                             "INSTALLED","System tray icon library — was missing, caused exe to run invisibly."),
            ("Pillow",                              "INSTALLED","Image library required by pystray for the tray icon."),
            ("pywin32",                             "INSTALLED","Windows print API — was missing, caused all print jobs to fail silently."),
            ("reportlab",                           "INSTALLED","PDF generation library for generate_docs.py."),
        ]),
        Spacer(1, 0.5*cm),
    ]

    # ── Footer ─────────────────────────────────────────
    story += [
        HRFlowable(width="100%", thickness=1, color=MID_GRAY),
        Spacer(1, 0.1*cm),
        Paragraph(
            f"PrintBridge Changes Summary  •  Generated {datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')}  •  Internal Use Only",
            S("ft", fontName="Helvetica", fontSize=8, textColor=GRAY, alignment=TA_CENTER)
        ),
    ]

    doc.build(story)
    print(f"✅  Changes PDF generated → {OUTPUT}")


if __name__ == "__main__":
    build()
