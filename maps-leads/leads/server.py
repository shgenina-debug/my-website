"""سيرفر محلي بسيط (127.0.0.1) للواجهة والـ API."""
import json
import os
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import xlsx
from .cities import DEFAULT_CITIES
from .db import DB, STATUSES
from .phones import extract_mobiles, wa_link
from .worker import Worker

STATIC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

EXPORT_COLS = [
    ("name", "اسم المكان", 34), ("phone", "الرقم", 13), ("phone_type", "نوع الرقم", 9),
    ("person", "اسم الشخص / صفته", 22), ("status", "الحالة", 14), ("notes", "ملاحظات", 28),
    ("category", "التصنيف", 20), ("city", "المدينة", 12), ("address", "العنوان", 40),
    ("rating", "التقييم", 8), ("reviews", "عدد المراجعات", 10), ("website", "الموقع الإلكتروني", 30),
    ("maps_url", "رابط جوجل ماب", 40), ("wa", "رابط واتساب", 28), ("activity", "النشاط", 14),
    ("search_area", "منطقة البحث", 12), ("created", "تاريخ الإضافة", 17),
]


def make_handler(db, worker):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
            if isinstance(body, (dict, list)):
                body = json.dumps(body, ensure_ascii=False).encode("utf-8")
            elif isinstance(body, str):
                body = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def _json(self):
            n = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(n).decode("utf-8") or "{}") if n else {}

        def do_GET(self):
            u = urllib.parse.urlparse(self.path)
            if u.path in ("/", "/index.html"):
                with open(os.path.join(STATIC, "index.html"), "rb") as f:
                    return self._send(200, f.read(), "text/html; charset=utf-8")
            if u.path == "/api/state":
                return self._send(200, {
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
            try:
                b = self._json()
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
                    phones = extract_mobiles(b.get("text") or "")
                    added, in_leads = db.add_exclusions(phones, b.get("source") or "واتساب")
                    return self._send(200, {"found": len(phones), "added": added, "in_leads": in_leads,
                                            "total": db.excluded_count()})
            except RuntimeError as e:
                return self._send(409, {"error": str(e)})
            except (ValueError, KeyError) as e:
                return self._send(400, {"error": str(e)})
            return self._send(404, {"error": "مش موجود"})

    return H


def serve(db_path, host="127.0.0.1", port=8765):
    db = DB(db_path)
    worker = Worker(db)
    httpd = ThreadingHTTPServer((host, port), make_handler(db, worker))
    return httpd, db, worker
