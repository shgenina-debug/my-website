"""تشغيل أداة جمع أرقام العملاء.

على الكمبيوتر:  python app.py   (تفتح http://127.0.0.1:8765 من غير باسورد)
على سيرفر:      HOST=0.0.0.0 PORT=10000 APP_PASSWORD=... DATA_DIR=/var/data python app.py --no-browser
"""
import os
import socket
import sys
import threading
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from leads.auth import load_secret  # noqa: E402
from leads.server import serve  # noqa: E402


def main():
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT") or os.environ.get("LEADS_PORT") or "8765")
    password = os.environ.get("APP_PASSWORD", "")
    data = os.environ.get("DATA_DIR") or os.path.join(HERE, "data")
    local = host in ("127.0.0.1", "localhost")
    if not local and len(password) < 8:
        print("لازم APP_PASSWORD (8 حروف على الأقل) لما الأداة تشتغل على سيرفر مفتوح على النت.")
        sys.exit(1)
    url = f"http://127.0.0.1:{port}"
    if local:
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                print("الأداة شغالة بالفعل — هفتحها في المتصفح:", url)
                webbrowser.open(url)
                return
    os.makedirs(data, exist_ok=True)
    httpd, _, _ = serve(os.path.join(data, "leads.db"), host=host, port=port,
                        password=password, secret=load_secret(data))
    print("=" * 50)
    if local:
        print("  الأداة شغالة على:", url)
        print("  متقفلش الشباك ده طول ما انتي شغالة.")
        print("  للإغلاق: اقفلي الشباك أو دوسي Ctrl+C")
    else:
        print(f"  السيرفر شغال على {host}:{port} — الباسورد مفعّل — البيانات في {data}", flush=True)
    print("=" * 50, flush=True)
    if local and "--no-browser" not in sys.argv:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
