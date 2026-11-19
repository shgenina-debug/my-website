"""تشغيل أداة جمع أرقام العملاء: python app.py  ثم افتح http://127.0.0.1:8765"""
import os
import socket
import sys
import threading
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from leads.server import serve  # noqa: E402


def main():
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass
    port = int(os.environ.get("LEADS_PORT", "8765"))
    url = f"http://127.0.0.1:{port}"
    with socket.socket() as s:
        if s.connect_ex(("127.0.0.1", port)) == 0:
            print("الأداة شغالة بالفعل — هفتحها في المتصفح:", url)
            webbrowser.open(url)
            return
    data = os.path.join(HERE, "data")
    os.makedirs(data, exist_ok=True)
    httpd, _, _ = serve(os.path.join(data, "leads.db"), port=port)
    print("=" * 50)
    print("  الأداة شغالة على:", url)
    print("  متقفلش الشباك ده طول ما انتي شغالة.")
    print("  للإغلاق: اقفلي الشباك أو دوسي Ctrl+C")
    print("=" * 50)
    if "--no-browser" not in sys.argv:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
