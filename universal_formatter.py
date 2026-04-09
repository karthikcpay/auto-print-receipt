"""
Universal ESC/POS Formatter
Dynamically handles Receipt or KOT style payloads.
"""

# ── ESC/POS command bytes ──────────────────────────────────────────────────────
CMD_INIT          = b'\x1b\x40'
CMD_ALIGN_LEFT    = b'\x1b\x61\x00'
CMD_ALIGN_CENTER  = b'\x1b\x61\x01'
CMD_ALIGN_RIGHT   = b'\x1b\x61\x02'
CMD_BOLD_ON       = b'\x1b\x45\x01'
CMD_BOLD_OFF      = b'\x1b\x45\x00'
CMD_DOUBLE_SIZE   = b'\x1b\x21\x30'
CMD_DOUBLE_HEIGHT = b'\x1b\x21\x10'
CMD_NORMAL_SIZE   = b'\x1b\x21\x00'
CMD_LINE_FEED     = b'\x0a'
CMD_CUT           = b'\x1d\x56\x41\x05'   # Partial cut + 5-dot feed


def _feed(n: int) -> bytes:
    return b'\x1b\x64' + bytes([n])


def _txt(text: str) -> bytes:
    return str(text).encode('cp437', errors='replace')


class _Builder:
    """Fluent ESC/POS byte builder."""

    def __init__(self, width: int = 48):
        self.w = width
        self._buf = bytearray()

    def _b(self, *items):
        for it in items:
            self._buf += it if isinstance(it, (bytes, bytearray)) else _txt(it)
        return self

    def init(self):          return self._b(CMD_INIT)
    def lf(self, n=1):      [self._b(CMD_LINE_FEED) for _ in range(n)]; return self
    def bold(self, on=True): return self._b(CMD_BOLD_ON if on else CMD_BOLD_OFF)
    def big(self, on=True):  return self._b(CMD_DOUBLE_SIZE if on else CMD_NORMAL_SIZE)
    def tall(self, on=True): return self._b(CMD_DOUBLE_HEIGHT if on else CMD_NORMAL_SIZE)
    def left(self):          return self._b(CMD_ALIGN_LEFT)
    def center(self):        return self._b(CMD_ALIGN_CENTER)
    def right(self):         return self._b(CMD_ALIGN_RIGHT)

    def line(self, text=''):
        return self._b(_txt(str(text)[:self.w]), CMD_LINE_FEED)

    def sep(self, ch='='):
        return self.line(ch * self.w)

    def two_col(self, left, right):
        r = str(right)
        l = str(left)
        space = self.w - len(r)
        return self.line(l[:space].ljust(space) + r)

    def item_row(self, name, qty, amount):
        w_name = self.w - 13
        row = str(name)[:w_name].ljust(w_name) + str(qty).center(4) + str(amount).rjust(9)
        return self.line(row)

    def cut(self):
        return self._b(_feed(4), CMD_CUT)

    def build(self) -> bytes:
        return bytes(self._buf)


def format_universal(data: dict, paper_width: int = 80) -> bytes:
    """
    Format a universal payload containing arbitrary JSON fields.
    If 'kotSections' exists, prints sections. 
    If prices exist on items, prints full receipt style.
    Normally uses 'main' object if present for metadata.
    """
    w = 48 if paper_width >= 80 else 32
    r = _Builder(w)
    r.init()

    # Determine main payload (in KOT it's under 'main')
    main = data.get('main', data)
    
    # Check if this is primarily a KOT (has kotSections)
    is_kot = 'kotSections' in data

    # ── Header ────────────────────────────────────────────────────────────────
    if is_kot and not main.get('businessName'):
        r.center().bold(True).tall(True)
        r.line('** KITCHEN ORDER **')
        r.tall(False).bold(False).left()
    else:
        r.center().bold(True).big(True)
        r.line(main.get('businessName', 'PRINT TICKET'))
        r.big(False).bold(False).left()

    r.sep('=')

    # ── Order Meta ────────────────────────────────────────────────────────────
    dt       = main.get('datetime', main.get('dateTime', ''))
    order_id = main.get('orderId', '')
    token    = main.get('dailyTokenNumber', '')

    if dt: r.two_col('Date :', dt)
    if order_id: r.two_col('Order :', order_id)
    if token: r.two_col('Token :', f'# {token}')

    r.sep('-')

    # ── Customer / Table ──────────────────────────────────────────────────────
    name  = main.get('customerName', '')
    phone = main.get('customerPhone', '')
    table = main.get('tableNumber', '')
    dtype = main.get('deliveryType', '').replace('_', ' ')
    addr  = main.get('address', '')
    note  = main.get('customerNote', '')

    if name:  r.two_col('Customer :', name)
    if phone: r.two_col('Phone :', f'+{phone}')
    if table and str(table) != '0': r.two_col('Table :', str(table))
    if dtype: r.two_col('Order Type :', dtype)
    if addr and 'DELIVERY' in str(main.get('deliveryType', '')):
        r.two_col('Address :', str(addr)[:w - 12])
        
    if note:
        r.bold(True)
        r.line(f'Note : {note}')
        r.bold(False)

    r.sep('=')

    # ── Specific KOT Sections ─────────────────────────────────────────────────
    kot_sections = data.get('kotSections', {})
    
    if kot_sections:
        for section, items in kot_sections.items():
            r.center().bold(True).tall(True)
            r.line(f'--- {str(section).upper()} ---')
            r.tall(False).bold(False).left()
            r.sep('-')
            
            for item in items:
                name = str(item.get('name', ''))
                qty  = str(item.get('quantity', 0))
                max_name = w - len(qty) - 4
                dots = max(1, w - len(name[:max_name]) - len(qty) - 3)
                r.bold(True)
                r.line(name[:max_name] + ' ' + '.' * dots + f' x{qty}')
                r.bold(False)
            r.lf()
            
    # ── Main Items (if not separated by sections or if we print them anyway) ──
    items = main.get('items', [])
    if items:
        # Check if we should print prices (if 'price' or 'total' is present in the first item)
        has_prices = 'total' in items[0] or 'price' in items[0]
        
        if has_prices:
            r.bold(True).item_row('ITEM', 'QTY', 'AMOUNT').bold(False)
            r.sep('-')
        else:
            r.bold(True).line("ITEMS").bold(False)
            r.sep('-')

        for item in items:
            name = item.get('name', '')
            qty  = item.get('quantity', 0)
            
            if has_prices:
                total = item.get('total', 0)
                if not total and 'price' in item:
                    total = float(item.get('price', 0)) * float(qty)
                r.item_row(name, qty, f"Rs.{total}")
            else:
                qty_str = str(qty)
                max_name = w - len(qty_str) - 4
                dots = max(1, w - len(name[:max_name]) - len(qty_str) - 3)
                r.bold(True)
                r.line(name[:max_name] + ' ' + '.' * dots + f' x{qty_str}')
                r.bold(False)

        r.sep('-')

    # ── Charges & Total (Receipt style) ───────────────────────────────────────
    if 'otherCharges' in main or 'orderTotal' in main:
        for charge in main.get('otherCharges', []):
            r.two_col(f"  {charge.get('name', '')} :", f"Rs.{charge.get('value', 0)}")
            
        if 'orderTotal' in main:
            r.sep('=')
            r.bold(True).two_col('TOTAL :', f"Rs.{main.get('orderTotal', 0)}").bold(False)
            r.sep('=')

    # ── General Total QTY for KOT ─────────────────────────────────────────────
    if is_kot and not has_prices and items:
        # Total QTY logic for KOT
        total_qty = sum(int(it.get('quantity', 0)) for it in items)
        r.center().bold(True).line(f'Total Items : {total_qty}').bold(False).left()
        r.sep('=')

    # ── Footer ────────────────────────────────────────────────────────────────
    r.center().lf()
    if not is_kot:
        r.line('Thank you for your order!')
        r.line('Please visit again')
        r.lf()

    qr = main.get('encrQrString', '')
    if qr:
        r.line(f"Ref: {main.get('orderLongId', '')}")

    r.left().cut()
    return r.build()
