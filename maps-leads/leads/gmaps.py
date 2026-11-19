"""سحب نتائج خرائط جوجل بدون مفتاح API.

الطريقة مأخوذة بالهندسة العكسية من مشروع gosom/google-maps-scraper (رخصة MIT،
انظر THIRD_PARTY_NOTICES.md): صفحة البحث في خرائط جوجل تطلب داخلياً
/search?tbm=map&pb=... ويرجع JSON فيه بيانات كل مكان كاملة في item[14]، ومواقع
الحقول (الاسم [11]، الرقم [178][0][0]، التصنيف [13] ...) هي نفسها اللي يقرأها gosom.
أضفنا هنا التنقل بين الصفحات عبر المعامل !8i{offset} لحد آخر النتائج.
"""
import json
import re
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
PAGE_SIZE = 20


class Blocked(Exception):
    """جوجل رفض الطلب أو طلب تحقق (captcha) — لازم نستنى."""


def _g(a, *path):
    for i in path:
        if not isinstance(a, list) or i >= len(a) or i < 0:
            return None
        a = a[i]
    return a


def build_url(query, lat, lon, span_m, offset, hl="ar", gl="sa"):
    pb = (
        f"!4m12!1m3!1d{span_m}!2d{lon:.4f}!3d{lat:.4f}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1"
        f"!7i{PAGE_SIZE}!8i{offset}"
        "!10b1!12m22!1m3!18b1!30b1!34e1!2m3!5m1!6e2!20e3!4b0!10b1!12b1!13b1!16b1!17m1!3e1"
        "!20m3!5e2!6b1!14b1!46m1!1b0!96b1!19m4!2m3!1i360!2i120!4i8"
    )
    params = {"tbm": "map", "authuser": "0", "hl": hl, "gl": gl, "q": query, "pb": pb}
    return "https://www.google.com/search?" + urllib.parse.urlencode(params)


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept-Language": "ar-SA,ar;q=0.9",
        "Accept": "*/*",
        "Referer": "https://www.google.com/maps",
        # موافقة الكوكيز: لو السيرفر في أوروبا جوجل بيحوّل لصفحة موافقة بدل النتايج
        "Cookie": "CONSENT=YES+; SOCS=CAESEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiA_LyaBg",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            final = r.geturl()
            body = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code in (429, 403, 503):
            raise Blocked(f"HTTP {e.code}")
        raise
    if "/sorry/" in final or not body.lstrip().startswith(")]}'"):
        raise Blocked("captcha")
    return body


CLOSED_WORDS = ("مغلق نهائي", "مغلق مؤقت", "مغلقة نهائي", "مغلقة مؤقت", "permanently closed", "temporarily closed")


def _hours_status(p):
    """نص ساعات العمل الحالي (مثلاً: مفتوح · يغلق عند الساعة ٩ م) — للعرض فقط."""
    for path in ((34, 4, 4), (88, 0)):
        v = _g(p, *path)
        if isinstance(v, str) and v:
            return v
    return ""


def _closed_label(p, depth=0):
    """يدور على "مغلق نهائيًا" أو "مغلق مؤقتًا" في بيانات المكان (مش "مغلق الآن")."""
    if isinstance(p, str):
        low = p.lower()
        return p if any(w in low for w in CLOSED_WORDS) else ""
    if isinstance(p, list) and depth < 5:
        for x in p:
            r = _closed_label(x, depth + 1)
            if r:
                return r
    return ""


def _real_url(u):
    if u and u.startswith("/url?"):
        return urllib.parse.parse_qs(urllib.parse.urlparse(u).query).get("q", [u])[0]
    return u or ""


def parse_place(p):
    title = _g(p, 11)
    if not isinstance(title, str) or not title:
        return None
    cats = _g(p, 13)
    cats = [c for c in cats if isinstance(c, str)] if isinstance(cats, list) else []
    cid = _g(p, 10) or ""
    place_id = _g(p, 78) or ""
    maps_url = ""
    if isinstance(cid, str) and ":" in cid:
        try:
            maps_url = "https://www.google.com/maps?cid=%d" % int(cid.split(":")[1], 16)
        except ValueError:
            pass
    if not maps_url and place_id:
        maps_url = "https://www.google.com/maps/place/?q=place_id:" + place_id
    address = _g(p, 18) or ""
    if isinstance(address, str) and address.startswith(title + "،"):
        address = address[len(title) + 1:].strip()
    phones = []
    for ph in _g(p, 178) or []:
        v = _g(ph, 0)
        if isinstance(v, str):
            phones.append(v)
    rating = _g(p, 4, 7)
    reviews = _g(p, 4, 8)
    closed = _closed_label(p)
    return {
        "key": place_id or cid or title,
        "name": title.strip(),
        "phones": phones,
        "category": cats[0] if cats else "",
        "categories": cats,
        "address": address if isinstance(address, str) else "",
        "city": _g(p, 183, 1, 3) or "",
        "rating": float(rating) if isinstance(rating, (int, float)) else None,
        "reviews": int(reviews) if isinstance(reviews, (int, float)) else 0,
        "website": _real_url(_g(p, 7, 0)),
        "maps_url": maps_url,
        "status": closed or _hours_status(p),
        "closed": bool(closed),
        "lat": _g(p, 9, 2),
        "lon": _g(p, 9, 3),
    }


def parse_page(body):
    """يرجع (قايمة الأماكن، عدد العناصر الخام). عدد 0 معناه إن النتائج خلصت."""
    text = body.split("\n", 1)[1] if body.startswith(")]}'") else body
    text = re.sub(r"^\)\]\}'\s*", "", text)
    data = json.loads(text)
    items = _g(data, 0, 1)
    if not isinstance(items, list):
        return [], 0
    places = []
    raw = 0
    for it in items:
        p = _g(it, 14)
        if isinstance(p, list):
            raw += 1
            parsed = parse_place(p)
            if parsed:
                places.append(parsed)
    return places, raw


def search_page(query, lat, lon, span_m, offset):
    return parse_page(fetch(build_url(query, lat, lon, span_m, offset)))
