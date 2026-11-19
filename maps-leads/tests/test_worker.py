import os
import tempfile
import unittest

from leads.db import DB
from leads.worker import Worker
from leads import gmaps


def place(i, phone, rating=4.0, reviews=10, closed=False):
    return {"key": f"k{i}", "name": f"مكان {i}", "phones": [phone] if phone else [], "category": "مصنع",
            "categories": ["مصنع"], "address": "شارع", "city": "", "rating": rating, "reviews": reviews,
            "website": "", "maps_url": f"https://www.google.com/maps?cid={i}",
            "status": "مغلق نهائيًا" if closed else "", "closed": closed, "lat": 0, "lon": 0}


class FakeGoogle:
    """صفحتين لكل مدينة: 20 + 5 نتايج."""
    def __init__(self, block_at=None):
        self.calls = []
        self.block_at = block_at

    def __call__(self, query, lat, lon, span, offset):
        self.calls.append((query, offset))
        if self.block_at is not None and len(self.calls) - 1 >= self.block_at:
            raise gmaps.Blocked("captcha")
        base = 100 if "جدة" in query else 200
        n = 20 if offset == 0 else (5 if offset == 20 else 0)
        out = []
        for j in range(n):
            i = base + offset + j
            out.append(place(i, f"05{i:08d}"))
        if "جدة" in query and offset == 0:
            out[0] = place(1, "+966 55 771 7180")          # موجود في الجروب
            out[1] = place(2, "012 612 3456")              # أرضي
            out[2] = place(3, None)                        # بدون رقم
            out[3] = place(4, "0500000004", closed=True)   # مقفول
            out[4] = place(5, "0500000005", rating=2.0)    # تقييم أقل
        if "الرياض" in query and offset == 0:
            out[0] = place(6, "0500000110")                # نفس رقم من جدة → مكرر
        return out, n


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = DB(os.path.join(self.tmp, "t.db"))

    def run_worker(self, w, sid):
        w.start(sid)
        w.thread.join(10)

    def test_full_run_filters_and_dedup(self):
        self.db.add_exclusions(["0557717180"], "واتساب")
        sid = self.db.create_search("مصنع مياه", ["جدة", "الرياض"], {"mobile_only": True, "exclude_closed": True, "min_rating": 3, "min_reviews": 0})
        g = FakeGoogle()
        self.run_worker(Worker(self.db, sleep=lambda s: None, search_page=g), sid)
        s = self.db.search(sid)
        self.assertEqual(s["state"], "done")
        jed, ruh = s["areas"]
        self.assertEqual(jed["found"], 25)
        self.assertEqual(jed["saved"], 20)
        self.assertEqual(jed["skipped"], {"مكرر/متعامل معاه": 1, "مش جوال": 1, "بدون رقم": 1, "مقفول": 1, "تقييم أقل": 1})
        self.assertEqual(ruh["saved"], 24)
        self.assertEqual(ruh["skipped"], {"مكرر/متعامل معاه": 1})
        leads = self.db.leads()
        self.assertEqual(len(leads), 44)
        self.assertTrue(all(l["phone"].startswith("05") and len(l["phone"]) == 10 for l in leads))
        self.assertEqual({l["city"] for l in leads}, {"جدة", "الرياض"})  # المدينة الفاضية تتملي من منطقة البحث
        # بحث تاني لنفس الحاجة بدون فلتر تقييم: الرقم الوحيد الجديد هو اللي اتستبعد قبل كده بسبب التقييم
        sid2 = self.db.create_search("مصنع مياه", ["جدة"], {"mobile_only": True})
        self.run_worker(Worker(self.db, sleep=lambda s: None, search_page=FakeGoogle()), sid2)
        self.assertEqual(self.db.search(sid2)["areas"][0]["saved"], 1)

    def test_resume_after_block(self):
        sid = self.db.create_search("مصنع مياه", ["جدة", "الرياض"], {"mobile_only": True})
        # الطلب التاني وما بعده مرفوض → البحث يتوقف بعد الصفحة الأولى
        self.run_worker(Worker(self.db, sleep=lambda s: None, search_page=FakeGoogle(block_at=1)), sid)
        s = self.db.search(sid)
        self.assertEqual(s["state"], "paused")
        self.assertEqual(s["areas"][0]["next_offset"], 20)
        # كمّل: يبدأ من الصفحة التانية في جدة مش من الأول
        g = FakeGoogle()
        self.run_worker(Worker(self.db, sleep=lambda s: None, search_page=g), sid)
        self.assertEqual(g.calls[0], ("مصنع مياه جدة", 20))
        self.assertEqual(self.db.search(sid)["state"], "done")
        self.assertEqual(len(self.db.leads()), 22 + 24)  # جدة: 25 - (أرضي، بدون رقم، مقفول) • الرياض: 25 - مكرر

    def test_restart_marks_running_as_paused(self):
        sid = self.db.create_search("x", ["جدة"], {})
        self.db.set_search_state(sid, "running")
        db2 = DB(os.path.join(self.tmp, "t.db"))
        self.assertEqual(db2.search(sid)["state"], "paused")


if __name__ == "__main__":
    unittest.main()
