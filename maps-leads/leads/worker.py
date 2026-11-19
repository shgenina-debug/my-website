"""تشغيل البحث في الخلفية: مدينة مدينة، صفحة صفحة، بتأخير عشوائي، مع حفظ مكان التوقف."""
import random
import threading
import time
import traceback

from . import gmaps
from .cities import locate
from .phones import normalize, MOBILE

MAX_PAGES = 30          # أمان: جوجل غالباً بيخلص قبل كده (حوالي 120 نتيجة)
PAGE_DELAY = (2.5, 6.0)  # ثواني بين كل صفحة والتانية
AREA_DELAY = (8.0, 15.0)  # ثواني بين كل مدينة والتانية
BLOCK_WAITS = [60, 180, 420]  # لو جوجل رفض: نستنى ونجرب تاني


def evaluate(place, opts, db):
    """يرجع (الرقم، النوع، الرقم الخام) أو (None, سبب الاستبعاد)."""
    if not place["phones"]:
        return None, "بدون رقم"
    if opts.get("exclude_closed", True) and place["closed"]:
        return None, "مقفول"
    if place["rating"] is not None and place["rating"] < float(opts.get("min_rating") or 0):
        return None, "تقييم أقل"
    if place["rating"] is None and float(opts.get("min_rating") or 0) > 0:
        return None, "تقييم أقل"
    if place["reviews"] < int(opts.get("min_reviews") or 0):
        return None, "مراجعات أقل"
    best = None
    for raw in place["phones"]:
        num, kind = normalize(raw)
        if kind == MOBILE:
            best = (num, kind, raw)
            break
        if best is None:
            best = (num, kind, raw)
    num, kind, raw = best
    if opts.get("mobile_only", True) and kind != MOBILE:
        return None, "مش جوال"
    if db.phone_known(num):
        return None, "مكرر/متعامل معاه"
    return (num, kind, raw), None


class Worker:
    def __init__(self, db, sleep=time.sleep, search_page=gmaps.search_page):
        self.db = db
        self.sleep = sleep
        self.search_page = search_page
        self.thread = None
        self.stop_flag = threading.Event()
        self.current = None
        self.live = ""

    def busy(self):
        return self.thread is not None and self.thread.is_alive()

    def start(self, sid):
        if self.busy():
            raise RuntimeError("فيه بحث شغال دلوقتي — استنى يخلص أو وقّفه")
        self.stop_flag.clear()
        self.current = sid
        self.db.set_search_state(sid, "running", "بيبدأ...")
        self.thread = threading.Thread(target=self._run, args=(sid,), daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_flag.set()

    def _wait(self, rng):
        left = random.uniform(*rng) if isinstance(rng, tuple) else float(rng)
        while left > 0:
            if self.stop_flag.is_set():
                return False
            step = min(left, 0.5)
            self.sleep(step)
            left -= step
        return not self.stop_flag.is_set()

    def _run(self, sid):
        try:
            self._run_inner(sid)
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            self.db.set_search_state(sid, "paused", f"حصل خطأ: {e} — دوس كمّل")
        finally:
            self.current = None

    def _run_inner(self, sid):
        s = self.db.search(sid)
        opts, activity = s["options"], s["activity"]
        first = True
        for a in s["areas"]:
            if a["done"]:
                continue
            if not first and a["next_offset"] == 0 and not self._wait(AREA_DELAY):
                break
            first = False
            lat, lon, span = locate(a["area"])
            query = f"{activity} {a['area']}"
            offset, found, saved, skipped = a["next_offset"], a["found"], a["saved"], a["skipped"]
            pages = offset // gmaps.PAGE_SIZE
            while not self.stop_flag.is_set():
                self.db.set_search_state(sid, "running", f"بيبحث في {a['area']} — صفحة {pages + 1}")
                places, raw = None, 0
                for attempt, wait in enumerate([0] + BLOCK_WAITS):
                    if wait:
                        self.db.set_search_state(sid, "running", f"جوجل طلب نستنى — هنجرب تاني بعد {wait // 60} دقيقة")
                        if not self._wait(float(wait)):
                            break
                    try:
                        places, raw = self.search_page(query, lat, lon, span, offset)
                        break
                    except gmaps.Blocked:
                        continue
                if self.stop_flag.is_set():
                    break
                if places is None:
                    self.db.set_search_state(sid, "paused", "جوجل وقف الطلبات مؤقتاً. استنى نص ساعة أو غيّر الشبكة ودوس كمّل.")
                    return
                for p in places:
                    found += 1
                    res, why = evaluate(p, opts, self.db)
                    if not res:
                        skipped[why] = skipped.get(why, 0) + 1
                        continue
                    num, kind, rawnum = res
                    ok = self.db.insert_lead({
                        "phone": num, "phone_type": kind, "phone_raw": rawnum, "place_key": p["key"],
                        "name": p["name"], "category": p["category"], "address": p["address"],
                        "city": p["city"] or a["area"], "rating": p["rating"], "reviews": p["reviews"],
                        "website": p["website"], "maps_url": p["maps_url"], "place_status": p["status"],
                        "activity": activity, "search_area": a["area"], "search_id": sid,
                    })
                    if ok:
                        saved += 1
                    else:
                        skipped["مكرر/متعامل معاه"] = skipped.get("مكرر/متعامل معاه", 0) + 1
                offset += gmaps.PAGE_SIZE
                pages += 1
                done = raw < gmaps.PAGE_SIZE or pages >= MAX_PAGES
                self.db.update_area(sid, a["pos"], next_offset=offset, found=found, saved=saved,
                                    skipped=skipped, done=1 if done else 0)
                if done or not self._wait(PAGE_DELAY):
                    break
            if self.stop_flag.is_set():
                break
        if self.stop_flag.is_set():
            self.db.set_search_state(sid, "paused", "اتوقف — دوس كمّل علشان يكمّل من نفس المكان")
        else:
            self.db.set_search_state(sid, "done", "خلص")
