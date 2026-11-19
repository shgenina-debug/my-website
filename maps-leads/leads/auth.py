"""تسجيل الدخول بباسورد لما الأداة تكون على سيرفر على النت."""
import hashlib
import hmac
import os
import secrets
import threading
import time

COOKIE = "ml_session"
SESSION_DAYS = 30
MAX_FAILS, FAIL_WINDOW = 8, 15 * 60  # 8 محاولات غلط في 15 دقيقة لكل IP


def load_secret(data_dir):
    s = os.environ.get("SECRET_KEY")
    if s:
        return s.encode()
    path = os.path.join(data_dir, "secret.key")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(secrets.token_hex(32))
    with open(path) as f:
        return f.read().strip().encode()


class Auth:
    def __init__(self, password, secret):
        self.password = password or ""
        self.secret = secret
        self.fails = {}
        self.lock = threading.Lock()

    @property
    def enabled(self):
        return bool(self.password)

    def _sign(self, exp):
        return hmac.new(self.secret, f"{exp}".encode(), hashlib.sha256).hexdigest()

    def new_token(self):
        exp = int(time.time()) + SESSION_DAYS * 86400
        return f"{exp}.{self._sign(exp)}"

    def valid(self, token):
        if not self.enabled:
            return True
        try:
            exp, sig = (token or "").split(".", 1)
            return int(exp) > time.time() and hmac.compare_digest(sig, self._sign(int(exp)))
        except ValueError:
            return False

    def blocked(self, ip):
        now = time.time()
        with self.lock:
            fails = [t for t in self.fails.get(ip, []) if now - t < FAIL_WINDOW]
            self.fails[ip] = fails
            return len(fails) >= MAX_FAILS

    def check_password(self, ip, password):
        ok = hmac.compare_digest((password or "").encode(), self.password.encode())
        if not ok:
            with self.lock:
                self.fails.setdefault(ip, []).append(time.time())
        return ok
