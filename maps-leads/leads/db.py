"""الحفظ في SQLite محلي: النتايج، الأرقام المستبعدة، وعمليات البحث (للاستكمال)."""
import json
import sqlite3
import threading
import time

STATUSES = ["جديد", "تم الإرسال", "رد", "في جروب الطلبات", "عميل", "مش مهتم"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT NOT NULL UNIQUE,
    phone_type TEXT NOT NULL,
    phone_raw TEXT,
    place_key TEXT,
    name TEXT NOT NULL,
    category TEXT, address TEXT, city TEXT,
    rating REAL, reviews INTEGER, website TEXT, maps_url TEXT, place_status TEXT,
    activity TEXT, search_area TEXT, search_id INTEGER,
    person TEXT DEFAULT '', status TEXT DEFAULT 'جديد', notes TEXT DEFAULT '',
    created_at REAL, updated_at REAL
);
CREATE INDEX IF NOT EXISTS leads_place ON leads(place_key);
CREATE TABLE IF NOT EXISTS excluded_phones (
    phone TEXT PRIMARY KEY, source TEXT, added_at REAL
);
CREATE TABLE IF NOT EXISTS searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity TEXT NOT NULL, options TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'paused',   -- running / paused / done
    message TEXT DEFAULT '', created_at REAL, updated_at REAL
);
CREATE TABLE IF NOT EXISTS search_areas (
    search_id INTEGER, pos INTEGER, area TEXT,
    next_offset INTEGER DEFAULT 0, done INTEGER DEFAULT 0,
    found INTEGER DEFAULT 0, saved INTEGER DEFAULT 0,
    skipped TEXT DEFAULT '{}',
    PRIMARY KEY (search_id, pos)
);
"""

LEAD_FIELDS = ["id", "phone", "phone_type", "name", "category", "address", "city", "rating",
               "reviews", "website", "maps_url", "place_status", "activity", "search_area",
               "search_id", "person", "status", "notes", "created_at", "updated_at"]


class DB:
    def __init__(self, path):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        with self.lock:
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.executescript(SCHEMA)
            # أي بحث كان شغال لما الأداة اتقفلت يبقى "متوقف" ويتكمّل بزرار
            self.conn.execute("UPDATE searches SET state='paused', message='اتوقف لما الأداة اتقفلت — دوس كمّل' WHERE state='running'")
            self.conn.commit()

    def q(self, sql, args=()):
        with self.lock:
            return [dict(r) for r in self.conn.execute(sql, args).fetchall()]

    def x(self, sql, args=()):
        with self.lock:
            cur = self.conn.execute(sql, args)
            self.conn.commit()
            return cur

    # ---------- الأرقام المعروفة ----------
    def phone_known(self, phone):
        with self.lock:
            return (self.conn.execute("SELECT 1 FROM leads WHERE phone=?", (phone,)).fetchone()
                    or self.conn.execute("SELECT 1 FROM excluded_phones WHERE phone=?", (phone,)).fetchone()) is not None

    def add_exclusions(self, phones, source):
        now = time.time()
        added = 0
        with self.lock:
            for p in phones:
                cur = self.conn.execute("INSERT OR IGNORE INTO excluded_phones VALUES (?,?,?)", (p, source, now))
                added += cur.rowcount
            self.conn.commit()
            in_leads = 0
            if phones:
                marks = ",".join("?" * len(phones))
                in_leads = self.conn.execute(f"SELECT COUNT(*) FROM leads WHERE phone IN ({marks})", phones).fetchone()[0]
        return added, in_leads

    def excluded_count(self):
        return self.q("SELECT COUNT(*) n FROM excluded_phones")[0]["n"]

    # ---------- النتايج ----------
    def insert_lead(self, rec):
        rec = dict(rec, created_at=time.time(), updated_at=time.time())
        cols = ",".join(rec)
        with self.lock:
            cur = self.conn.execute(
                f"INSERT OR IGNORE INTO leads ({cols}) VALUES ({','.join('?' * len(rec))})", list(rec.values()))
            self.conn.commit()
            return cur.rowcount == 1

    def update_lead(self, lead_id, fields):
        allowed = {k: v for k, v in fields.items() if k in ("person", "status", "notes")}
        if "status" in allowed and allowed["status"] not in STATUSES:
            raise ValueError("حالة غير معروفة")
        if not allowed:
            return
        sets = ",".join(f"{k}=?" for k in allowed)
        self.x(f"UPDATE leads SET {sets}, updated_at=? WHERE id=?", [*allowed.values(), time.time(), lead_id])

    def leads(self):
        cols = ",".join(LEAD_FIELDS)
        rows = self.q(f"SELECT {cols}, EXISTS(SELECT 1 FROM excluded_phones e WHERE e.phone=leads.phone) AS in_group FROM leads ORDER BY id DESC")
        return rows

    # ---------- عمليات البحث ----------
    def create_search(self, activity, areas, options):
        now = time.time()
        with self.lock:
            cur = self.conn.execute("INSERT INTO searches (activity, options, state, created_at, updated_at) VALUES (?,?,?,?,?)",
                                    (activity, json.dumps(options, ensure_ascii=False), "paused", now, now))
            sid = cur.lastrowid
            for i, a in enumerate(areas):
                self.conn.execute("INSERT INTO search_areas (search_id, pos, area) VALUES (?,?,?)", (sid, i, a))
            self.conn.commit()
        return sid

    def search(self, sid):
        rows = self.q("SELECT * FROM searches WHERE id=?", (sid,))
        if not rows:
            return None
        s = rows[0]
        s["options"] = json.loads(s["options"])
        s["areas"] = self.q("SELECT * FROM search_areas WHERE search_id=? ORDER BY pos", (sid,))
        for a in s["areas"]:
            a["skipped"] = json.loads(a["skipped"] or "{}")
        return s

    def searches(self, limit=30):
        ids = [r["id"] for r in self.q("SELECT id FROM searches ORDER BY id DESC LIMIT ?", (limit,))]
        return [self.search(i) for i in ids]

    def set_search_state(self, sid, state, message=""):
        self.x("UPDATE searches SET state=?, message=?, updated_at=? WHERE id=?", (state, message, time.time(), sid))

    def update_area(self, sid, pos, **f):
        if "skipped" in f:
            f["skipped"] = json.dumps(f["skipped"], ensure_ascii=False)
        sets = ",".join(f"{k}=?" for k in f)
        self.x(f"UPDATE search_areas SET {sets} WHERE search_id=? AND pos=?", [*f.values(), sid, pos])
