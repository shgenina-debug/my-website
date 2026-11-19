"""السيرفر: على الكمبيوتر (127.0.0.1 بدون باسورد) أو على سيرفر على النت (بباسورد)."""
import base64
import io
import json
import os
import time
import urllib.parse
import zipfile
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import xlsx
from .auth import COOKIE, SESSION_DAYS, Auth
from .cities import DEFAULT_CITIES
from .db import DB, STATUSES
from .phones import extract_mobiles, wa_link
from .worker import Worker

STATIC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
STATIC_FILES = {
    "/manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json; charset=utf-8"),
    "/icon-192.png": ("icon-192.png", "image/png"),
    "/icon-512.png": ("icon-512.png", "image/png"),
}
PUBLIC = {"/login", "/api/login", "/healthz", *STATIC_FILES}
MAX_BODY = 25 * 1024 * 1024        # أقصى حجم لملف الواتساب المرفوع
MAX_UNZIPPED = 60 * 1024 * 1024


def text_from_upload(b):
    """النص من طلب الاستبعاد: نص ملصوق و/أو ملف .zip من تصدير الواتساب."""
    text = b.get("text") or ""
    if b.get("zip_b64"):
        raw = base64.b64decode(b["zip_b64"])
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            total = 0
            for info in z.infolist():
                if info.filename.lower().endswith(".txt"):
                    total += info.file_size
                    if total > MAX_UNZIPPED:
                        raise ValueError("الملف كبير جداً")
                    text += "\n" + z.read(info).decode("utf-8", "replace")
    return text


EXPORT_COLS = [
    ("name", "اسم المكان", 34), ("phone", "الرقم", 13), ("phone_type", "نوع الرقم", 9),
    ("person", "اسم الشخص / صفته", 22), ("status", "الحالة", 14), ("notes", "ملاحظات", 28),
    ("category", "التصنيف", 20), ("city", "المدينة", 12), ("address", "العنوان", 40),
    ("rating", "التقييم", 8), ("reviews", "عدد المراجعات", 10), ("website", "الموقع الإلكتروني", 30),
    ("maps_url", "رابط جوجل ماب", 40), ("wa", "رابط واتساب", 28), ("activity", "النشاط", 14),
    ("search_area", "منطقة البحث", 12), ("created", "تاريخ الإضافة", 17),
]


def make_handler(db, worker, auth):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _ip(self):
            fwd = self.headers.get("X-Forwarded-For")
            return fwd.split(",")[0].strip() if fwd else self.client_address[0]

        def _authed(self):
            c = SimpleCookie(self.headers.get("Cookie") or "")
            return auth.valid(c[COOKIE].value if COOKIE in c else "")

        def _guard(self, path):
            """يرجع True لو الطلب مسموح، وإلا يرد بنفسه (تحويل لصفحة الدخول أو 401)."""
            if path in PUBLIC or self._authed():
                return True
            if path.startswith("/api/"):
                self._send(401, {"error": "لازم تسجلي دخول"})
            else:
                self.send_response(302)
                self.send_header("Location", "/login")
                self.send_header("Content-Length", "0")
                self.end_headers()
            return False

        def _file(self, name, ctype, cache=False):
            with open(os.path.join(STATIC, name), "rb") as f:
                extra = {"Cache-Control": "public, max-age=86400"} if cache else None
                return self._send(200, f.read(), ctype, extra)

        def _send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
            if isinstance(body, (dict, list)):
                body = json.dumps(body, ensure_ascii=False).encode("utf-8")
            elif isinstance(body, str):
                body = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            extra = dict(extra or {})
            self.send_header("Cache-Control", extra.pop("Cache-Control", "no-store"))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            for k, v in extra.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def _json(self):
            n = int(self.headers.get("Content-Length") or 0)
            if n > MAX_BODY:
                raise ValueError("الملف كبير جداً")
            return json.loads(self.rfile.read(n).decode("utf-8") or "{}") if n else {}

        def do_GET(self):
            u = urllib.parse.urlparse(self.path)
            if u.path == "/healthz":
                return self._send(200, {"ok": True})
            if u.path in STATIC_FILES:
                return self._file(*STATIC_FILES[u.path], cache=True)
            if u.path == "/login":
                if not auth.enabled:
                    return self._send(302, b"", extra={"Location": "/"})
                return self._file("login.html", "text/html; charset=utf-8")
            if not self._guard(u.path):
                return
            if u.path in ("/", "/index.html"):
                return self._file("index.html", "text/html; charset=utf-8")
            if u.path == "/api/state":
                return self._send(200, {
                    "auth": auth.enabled,
                    "statuses": STATUSES, "default_cities": DEFAULT_CITIES,
                    "busy": worker.busy(), "current": worker.current,
                    "searches": db.searches(), "excluded": db.excluded_count(),
                })
            if u.path == "/api/leads":
                return self._send(200, db.leads())
            if u.path == "/api/export.xlsx":
                ids = urllib.parse.parse_qs(u.query).get("ids", [""])[0]
                rows = db.leads()
                if ids:
                    keep = {int(i) for i in ids.split(",") if i.isdigit()}
                    rows = [r for r in rows if r["id"] in keep]
                data = []
                for r in rows:
                    r["wa"] = wa_link(r["phone"])
                    r["created"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(r["created_at"] or 0))
                    data.append([r.get(k) for k, _, _ in EXPORT_COLS])
                body = xlsx.build([h for _, h, _ in EXPORT_COLS], data, [w for _, _, w in EXPORT_COLS])
                fname = time.strftime("leads-%Y%m%d-%H%M.xlsx")
                return self._send(200, body, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                  {"Content-Disposition": f'attachment; filename="{fname}"'})
            return self._send(404, {"error": "مش موجود"})

        def do_POST(self):
            u = urllib.parse.urlparse(self.path)
            # حماية من الطلبات المزورة من مواقع تانية: كل الـ API بيقبل JSON بس
            if not (self.headers.get("Content-Type") or "").startswith("application/json"):
                return self._send(415, {"error": "نوع الطلب غلط"})
            if not self._guard(u.path):
                return
            try:
                b = self._json()
                if u.path == "/api/login":
                    ip = self._ip()
                    if auth.blocked(ip):
                        return self._send(429, {"error": "محاولات كتير غلط — استني ربع ساعة"})
                    if not auth.check_password(ip, b.get("password")):
                        return self._send(401, {"error": "الباسورد غلط"})
                    secure = "; Secure" if self.headers.get("X-Forwarded-Proto") == "https" else ""
                    cookie = (f"{COOKIE}={auth.new_token()}; Path=/; HttpOnly; SameSite=Lax"
                              f"; Max-Age={SESSION_DAYS * 86400}{secure}")
                    return self._send(200, {"ok": True}, extra={"Set-Cookie": cookie})
                if u.path == "/api/logout":
                    return self._send(200, {"ok": True}, extra={"Set-Cookie": f"{COOKIE}=; Path=/; Max-Age=0"})
                if u.path == "/api/search":
                    activity = (b.get("activity") or "").strip()
                    areas = [a.strip() for a in b.get("areas", []) if a.strip()]
                    areas = list(dict.fromkeys(areas))
                    if not activity or not areas:
                        return self._send(400, {"error": "اكتب النشاط واختار مدينة واحدة على الأقل"})
                    if worker.busy():
                        return self._send(409, {"error": "فيه بحث شغال دلوقتي — استنى يخلص أو وقّفه"})
                    opts = {
                        "mobile_only": bool(b.get("mobile_only", True)),
                        "exclude_closed": bool(b.get("exclude_closed", True)),
                        "min_rating": float(b.get("min_rating") or 0),
                        "min_reviews": int(b.get("min_reviews") or 0),
                    }
                    sid = db.create_search(activity, areas, opts)
                    worker.start(sid)
                    return self._send(200, {"id": sid})
                if u.path == "/api/resume":
                    worker.start(int(b["id"]))
                    return self._send(200, {"ok": True})
                if u.path == "/api/stop":
                    worker.stop()
                    return self._send(200, {"ok": True})
                if u.path == "/api/lead":
                    db.update_lead(int(b["id"]), b)
                    return self._send(200, {"ok": True})
                if u.path == "/api/exclusions":
                    phones = extract_mobiles(text_from_upload(b))
                    added, in_leads = db.add_exclusions(phones, b.get("source") or "واتساب")
                    return self._send(200, {"found": len(phones), "added": added, "in_leads": in_leads,
                                            "total": db.excluded_count()})
            except RuntimeError as e:
                return self._send(409, {"error": str(e)})
            except (ValueError, KeyError, zipfile.BadZipFile) as e:
                return self._send(400, {"error": str(e)})
            return self._send(404, {"error": "مش موجود"})

    return H


def serve(db_path, host="127.0.0.1", port=8765, password="", secret=b"dev"):
    db = DB(db_path)
    worker = Worker(db)
    httpd = ThreadingHTTPServer((host, port), make_handler(db, worker, Auth(password, secret)))
    return httpd, db, worker
