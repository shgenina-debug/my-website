"""توحيد أرقام الهواتف السعودية وتصنيفها واستخراجها من النصوص."""
import re

_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

MOBILE, LANDLINE, UNIFIED, TOLLFREE, OTHER = "جوال", "أرضي", "920", "800", "غير معروف"


def _digits(raw):
    s = (raw or "").translate(_DIGITS)
    plus = s.strip().startswith("+")
    d = re.sub(r"\D", "", s)
    return d, plus


def normalize(raw):
    """يرجع (الرقم الموحد، النوع). الجوال دايماً 05XXXXXXXX، الأرضي 01XXXXXXXX (10 أرقام)."""
    d, _ = _digits(raw)
    if d.startswith("00966"):
        d = d[5:]
    elif d.startswith("966") and len(d) >= 11:
        d = d[3:]
    if d.startswith("920") and len(d) == 9:
        return d, UNIFIED
    if d.startswith("800") and len(d) == 10:
        return d, TOLLFREE
    if not d.startswith("0") and len(d) == 9 and d[0] in "1234567":
        d = "0" + d
    if d.startswith("05") and len(d) == 10:
        return d, MOBILE
    if len(d) == 10 and d[0] == "0" and d[1] in "1234567":  # 011/012/013/014/016/017 + 7 أرقام
        return d, LANDLINE
    return d, OTHER


def wa_link(mobile):
    """رابط wa.me للجوال 05XXXXXXXX -> https://wa.me/9665XXXXXXXX"""
    return "https://wa.me/966" + mobile[1:] if mobile.startswith("05") else ""


# أرقام الجوال بأي صيغة: +966 5x xxx xxxx / 00966 / 966 / 05x / 5x (مع مسافات أو شرط أو علامات اتجاه)
_SEP = r"[\s\-\.‎‏‪-‮ ()]*"
_MOBILE_RE = re.compile(
    r"(?<!\d)(?:(?:\+|00)?966" + _SEP + r"0?|0)?5(?:" + _SEP + r"\d){8}(?!\d)"
)


def extract_mobiles(text):
    """يستخرج كل أرقام الجوال السعودية من نص (مثل ملف تصدير جروب واتساب)."""
    text = (text or "").translate(_DIGITS)
    found = []
    seen = set()
    for m in _MOBILE_RE.finditer(text):
        num, kind = normalize(m.group(0))
        if kind == MOBILE and num not in seen:
            seen.add(num)
            found.append(num)
    return found
