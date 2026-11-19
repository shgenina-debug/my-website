import base64
import io
import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import zipfile

from leads.server import serve


class Client:
    def __init__(self, base):
        self.base, self.cookie = base, ""

    def req(self, path, body=None, ctype="application/json"):
        data = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(self.base + path, data=data, method="POST" if body is not None else "GET")
        if body is not None:
            r.add_header("Content-Type", ctype)
        if self.cookie:
            r.add_header("Cookie", self.cookie)

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None
        try:
            resp = urllib.request.build_opener(NoRedirect).open(r, timeout=5)
            code, headers, raw = resp.status, resp.headers, resp.read()
        except urllib.error.HTTPError as e:
            code, headers, raw = e.code, e.headers, e.read()
        sc = headers.get("Set-Cookie")
        if sc:
            self.cookie = sc.split(";")[0]
        return code, headers, raw


class ServerTests(unittest.TestCase):
    def start(self, password):
        tmp = tempfile.mkdtemp()
        httpd, db, _ = serve(os.path.join(tmp, "t.db"), port=0, password=password, secret=b"k")
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        self.addCleanup(httpd.shutdown)
        return Client(f"http://127.0.0.1:{httpd.server_address[1]}"), db

    def test_password_required_on_server(self):
        c, _ = self.start("secret-pass-1")
        self.assertEqual(c.req("/healthz")[0], 200)
        self.assertEqual(c.req("/manifest.webmanifest")[0], 200)
        code, h, _ = c.req("/")
        self.assertEqual((code, h["Location"]), (302, "/login"))
        self.assertEqual(c.req("/api/leads")[0], 401)
        self.assertEqual(c.req("/api/export.xlsx")[0], 401)
        self.assertEqual(c.req("/api/search", {"activity": "x", "areas": ["جدة"]})[0], 401)
        self.assertEqual(c.req("/api/login", {"password": "غلط"})[0], 401)
        code, h, _ = c.req("/api/login", {"password": "secret-pass-1"})
        self.assertEqual(code, 200)
        self.assertIn("HttpOnly", h["Set-Cookie"])
        self.assertEqual(c.req("/")[0], 200)
        self.assertTrue(json.loads(c.req("/api/state")[2])["auth"])
        c.req("/api/logout", {})
        self.assertEqual(c.req("/api/leads")[0], 401)

    def test_forged_cookie_and_bruteforce(self):
        c, _ = self.start("secret-pass-1")
        c.cookie = "ml_session=9999999999.deadbeef"
        self.assertEqual(c.req("/api/leads")[0], 401)
        c.cookie = ""
        for _ in range(8):
            c.req("/api/login", {"password": "x"})
        self.assertEqual(c.req("/api/login", {"password": "secret-pass-1"})[0], 429)

    def test_non_json_post_rejected(self):
        c, _ = self.start("")
        self.assertEqual(c.req("/api/stop", {}, ctype="text/plain")[0], 415)

    def test_local_mode_no_password_and_zip_upload(self):
        c, db = self.start("")
        self.assertEqual(c.req("/")[0], 200)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("WhatsApp Chat.txt", "🌷 مصنع . سدير\n0557717180\n+966 50 000 1111")
        body = {"zip_b64": base64.b64encode(buf.getvalue()).decode(), "text": "056-111-2233"}
        code, _, raw = c.req("/api/exclusions", body)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(raw)["added"], 3)
        self.assertEqual(c.req("/api/exclusions", {"zip_b64": "bm90IGEgemlw"})[0], 400)


if __name__ == "__main__":
    unittest.main()
