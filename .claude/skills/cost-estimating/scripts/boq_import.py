#!/usr/bin/env python3
"""قراءة جدول كميات من Excel/CSV ومطابقة بنوده مع مكتبة البنود.

Standard library only (zipfile + xml), so it runs anywhere. The same
header detection and matching rules are mirrored in
pricing-platform/index.html (importer section) — keep them in sync.

- read_table(path, sheet=None) -> (sheet_names, rows)  rows = list of lists of str
- detect_header(rows) -> (row_index, {"code": i, "desc": i, "unit": i, "qty": i})
- rows_to_items(rows, header_row, cols) -> items (rows without qty become section titles)
- best_template(item, templates) -> (template_id or None, score)
"""

import csv
import math
import re
import zipfile
import xml.etree.ElementTree as ET

HEADER_KEYS = {  # order matters: description before code ("item description" is not the item number)
    "desc": ["الوصف", "وصف", "البيان", "بيان", "description", "desc"],
    "qty": ["الكمية", "كمية", "الكميه", "qty", "quantity", "qnty"],
    "unit": ["الوحدة", "وحدة", "وحده", "unit", "uom"],
    "code": ["رقم البند", "البند", "رقم", "مسلسل", "م", "item", "no", "code", "ref", "s/n"],
}
STOP = set("من في على مع الى الي او و ب ل حسب المواصفات المخططات المواصفه كامل كامله جميع اعمال عمل شامل شاملا شامله "
           "توريد تركيب وتركيب وتوريد بما ذلك يلزم اللازمه اللازم وغيرها الخ the and of with to for in on by supply install "
           "including incl all complete as per".split())
UNIT_MAP = [
    ("m2", ["م2", "م²", "m2", "sqm", "متر مربع", "مترمربع"]),
    ("m3", ["م3", "م³", "m3", "cum", "متر مكعب", "مترمكعب"]),
    ("m", ["م.ط", "مط", "م ط", "متر طولي", "lm", "m", "ml", "rm", "م"]),
    ("t", ["طن", "ton", "t", "tonne"]),
    ("no", ["عدد", "no", "nr", "nos", "each", "ea", "pcs", "حبة", "قطعة"]),
    ("pt", ["نقطة", "نقطه", "point", "pt"]),
    ("ls", ["مقطوع", "ls", "l.s", "lump sum", "lot"]),
]
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩٫٬", "0123456789.,")
MATCH_THRESHOLD = 0.30


# ---------- reading ----------
def _col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _iter(el, name):
    return (e for e in el.iter() if _local(e.tag) == name)


def _text(el):
    return "".join(t.text or "" for t in _iter(el, "t"))


def read_xlsx(path, sheet=None):
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        shared = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = [_text(si) for si in root if _local(si.tag) == "si"]
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels}
        sheets = []
        for s in _iter(wb, "sheet"):
            rid = next(v for k, v in s.attrib.items() if _local(k) == "id")
            t = targets[rid].lstrip("/")
            sheets.append((s.get("name"), t if t.startswith("xl/") else "xl/" + t))
        if not sheets:
            raise ValueError("no sheets in workbook")
        chosen = next((p for n, p in sheets if n == sheet), sheets[0][1]) if sheet else sheets[0][1]
        root = ET.fromstring(z.read(chosen))
    rows = []
    for row in _iter(root, "row"):
        r = int(row.get("r", len(rows) + 1)) - 1
        while len(rows) <= r:
            rows.append([])
        cells = rows[r]
        for i, c in enumerate(e for e in row if _local(e.tag) == "c"):
            idx = _col_index(c.get("r")) if c.get("r") else len(cells)
            t = c.get("t")
            v = next((e.text or "" for e in c if _local(e.tag) == "v"), "")
            if t == "s":
                val = shared[int(v)] if v else ""
            elif t == "inlineStr":
                val = _text(c)
            elif t == "b":
                val = "TRUE" if v == "1" else "FALSE"
            else:
                val = v
            while len(cells) <= idx:
                cells.append("")
            cells[idx] = val.strip()
    return [n for n, _ in sheets], rows


def read_table(path, sheet=None):
    if path.lower().endswith(".csv"):
        with open(path, encoding="utf-8-sig", newline="") as f:
            return ["csv"], [[c.strip() for c in r] for r in csv.reader(f)]
    if path.lower().endswith(".xls"):
        raise ValueError("صيغة .xls القديمة غير مدعومة — احفظ الملف بصيغة .xlsx")
    return read_xlsx(path, sheet)


# ---------- interpretation ----------
def to_number(s):
    if s is None:
        return None
    s = str(s).translate(ARABIC_DIGITS).replace(",", "").replace(" ", "").strip()
    try:
        x = float(s)
        return x if math.isfinite(x) else None
    except ValueError:
        return None


def norm_header(s):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s/]", " ", str(s).lower())).strip()


def detect_header(rows, scan=25):
    best = (None, {}, 0)
    for i, row in enumerate(rows[:scan]):
        cols = {}
        for j, cell in enumerate(row):
            h = norm_header(cell)
            if not h:
                continue
            for field, keys in HEADER_KEYS.items():
                if field in cols:
                    continue
                if any(h == k or (len(k) > 2 and k in h) for k in keys):
                    cols[field] = j
                    break
        score = len(cols) + (1 if "desc" in cols else 0) + (1 if "qty" in cols else 0)
        if score > best[2]:
            best = (i, cols, score)
    if best[0] is None or "desc" not in best[1]:
        return None, {}
    return best[0], best[1]


def rows_to_items(rows, header_row, cols):
    items, section = [], ""
    get = lambda r, f: (r[cols[f]] if f in cols and cols[f] < len(r) else "").strip()
    for r in rows[header_row + 1:]:
        desc, code, unit = get(r, "desc"), get(r, "code"), get(r, "unit")
        qty = to_number(get(r, "qty"))
        if not desc and not code:
            continue
        if qty is None:
            if desc:
                section = desc  # heading line (no quantity)
            continue
        items.append({"code": code or f"I-{len(items) + 1:03d}", "description": desc, "unit": unit,
                      "qty": qty, "section": section})
    return items


# ---------- matching ----------
def norm_text(s):
    s = str(s).lower()
    s = re.sub(r"[ً-ْـ]", "", s)
    s = re.sub("[إأآ]", "ا", s).replace("ى", "ي").replace("ة", "ه")
    return re.sub(r"[^\w]+", " ", s.translate(ARABIC_DIGITS))


def tokens(s):
    out = set()
    for t in norm_text(s).split():
        for pre in ("وال", "بال", "كال", "فال", "لل", "ال"):
            if t.startswith(pre) and len(t) > len(pre) + 2:
                t = t[len(pre):]
                break
        if len(t) >= 2 and t not in STOP:
            out.add(stem(t))
    return out


def stem(t):
    """Light Arabic suffix folding so دهانات/دهان and داخلية/داخلي compare equal."""
    for suf in ("ات", "يه", "ين", "ون"):
        if t.endswith(suf) and len(t) > 4:
            return t[:-2]
    if t[-1:] in ("ه", "ي") and len(t) > 3:
        return t[:-1]
    return t


def norm_unit(u):
    u = str(u).strip().lower().replace("²", "2").replace("³", "3")
    for key, alts in UNIT_MAP:
        if u in [a.replace("²", "2").replace("³", "3") for a in alts]:
            return key
    return u


def match_score(item, tpl):
    a, b = tokens(item["description"]), tokens(tpl["description"])
    if not a or not b:
        return 0.0
    s = len(a & b) / math.sqrt(len(a) * len(b))
    if norm_unit(item["unit"]) == norm_unit(tpl["unit"]):
        s += 0.1
    return s


def best_template(item, templates, disciplines=None):
    best, best_s = None, 0.0
    for t in templates:
        s = match_score(item, t) + (0.05 if disciplines and t["d"] in disciplines else 0)
        if s > best_s:
            best, best_s = t, s
    return (best["id"], round(best_s, 3)) if best and best_s >= MATCH_THRESHOLD else (None, round(best_s, 3))
