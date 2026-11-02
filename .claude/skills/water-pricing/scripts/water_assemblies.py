#!/usr/bin/env python3
"""مولّد بنود خطوط المياه والصرف (تحليل هندسي + تفكيك البند).

Takes a water project JSON with a `pipelines` list and a `rates` library,
computes the trench geometry and the quantity of every sub-activity per
metre of pipe (excavation, rock, bedding, surround, backfill, disposal,
shoring, dewatering, asphalt reinstatement, testing, warning tape), turns
them into BOQ components, and writes a project JSON that pricing_calc.py
can price. It also prints an engineering sheet with checks.

Usage:
    python3 water_assemblies.py water_project.json --out priced_input.json [--sheet sheet.md]
    python3 ../../saudi-project-pricing/scripts/pricing_calc.py priced_input.json --csv boq.csv
"""

import argparse
import copy
import json
import math
import sys

# indicative defaults — every one can be overridden in project["design"]
DEFAULT_DESIGN = {
    "min_width_m": 0.60,          # practical minimum trench width
    "clearance_small_m": 0.20,    # each side, DN <= 300
    "clearance_large_m": 0.30,    # each side, DN > 300
    "bedding_m": 0.15,            # below the pipe
    "surround_above_m": 0.30,     # above the crown
    "min_cover_m": 1.00,          # to crown
    "shoring_depth_m": 1.50,      # shoring from this depth
    "deep_trench_m": 4.00,        # special design above this
    "bulking": 1.25,              # loose / bank volume for disposal
    "asphalt_overlap_m": 0.30,    # each side of the trench
    "pipe_waste": 0.02,
}

# indicative laying productivity (m/day) per material and DN band, from
# water-projects-knowledge/references/productivity-norms.md — used for checks only
PRODUCTIVITY_NORMS = [
    ("HDPE", 0, 160, 150, 300),
    ("HDPE", 161, 400, 80, 150),
    ("DI", 0, 300, 80, 150),
    ("DI", 301, 600, 40, 80),
    ("DI", 601, 1200, 20, 40),
    ("GRP", 301, 600, 40, 80),
    ("GRP", 601, 1600, 20, 40),
    ("UPVC", 0, 400, 50, 100),
]

FLEXIBLE = {"HDPE", "GRP", "UPVC", "PVC"}


def geometry(p, d):
    od = p["od_m"]
    clearance = d["clearance_small_m"] if p["dn_mm"] <= 300 else d["clearance_large_m"]
    width = max(d["min_width_m"], od + 2 * clearance)
    depth = p["cover_m"] + od + d["bedding_m"]
    pipe_area = math.pi * od ** 2 / 4
    exc = width * depth
    bed = width * d["bedding_m"]
    sur = width * (od + d["surround_above_m"]) - pipe_area
    backfill = exc - bed - sur - pipe_area
    imported = bed + sur + (backfill if p.get("import_backfill") else 0.0)
    disposal = (pipe_area + bed + sur + (backfill if p.get("import_backfill") else 0.0)) * d["bulking"]
    shoring = 2 * depth if depth > d["shoring_depth_m"] else 0.0
    asphalt = width + 2 * d["asphalt_overlap_m"] if p.get("surface") == "asphalt" else 0.0
    rock = exc * p.get("rock_ratio", 0.0)
    return {
        "width": width, "depth": depth, "excavation": exc - rock, "rock": rock,
        "bedding": bed, "surround": sur, "backfill": backfill, "imported": imported,
        "disposal": disposal, "shoring": shoring, "asphalt": asphalt,
    }


def need(rates, key, code, missing):
    if key not in rates:
        missing.add(f"{key} (مطلوب للبند {code})")
        return None
    return rates[key]


def comp(rates, key, name, qty, code, missing, waste=0.0):
    r = need(rates, key, code, missing)
    if r is None or qty <= 0:
        return None
    c = {"type": r.get("type", "subcontract"), "name": name, "key": r.get("key", key),
         "qty": round(qty, 4), "rate": r["rate"]}
    if waste:
        c["waste"] = waste
    return c


def build_item(p, rates, d, missing):
    g = geometry(p, d)
    code = p["code"]
    comps = []
    comps.append({"type": "material", "name": f"أنبوب {p['material']} DN{p['dn_mm']}", "key": "pipe",
                  "qty": 1, "rate": p["pipe_rate_per_m"], "waste": p.get("pipe_waste", d["pipe_waste"])})
    if p.get("fittings_allowance"):
        comps.append({"type": "material", "name": "قطع ووصلات (نسبة من سعر الأنبوب)", "key": "pipe",
                      "qty": p["fittings_allowance"], "rate": p["pipe_rate_per_m"]})
    factor = 1.0
    for f in p.get("productivity_factors", []):
        factor *= f["factor"]
    comps.append({"type": "labor", "name": "فرقة التمديد والوصل", "key": "labor",
                  "daily_cost": p["lay_crew_daily_cost"],
                  "productivity": round(p["lay_productivity_m_day"] * factor, 3)})
    if p.get("lay_equipment_daily_cost"):
        comps.append({"type": "equipment", "name": "معدات التمديد (رفع/لحام)", "key": "equipment",
                      "daily_cost": p["lay_equipment_daily_cost"],
                      "productivity": round(p["lay_productivity_m_day"] * factor, 3)})
    rows = [
        ("excavation_m3", "حفر خندق", g["excavation"]),
        ("rock_excavation_m3", "حفر صخري", g["rock"]),
        ("bedding_m3", "فرشة رملية", g["bedding"]),
        ("surround_m3", "تغليف بمادة مختارة", g["surround"]),
        ("backfill_m3", "ردم ودمك على طبقات", g["backfill"]),
        ("disposal_m3", "نقل الفائض للمرادم المعتمدة", g["disposal"]),
        ("shoring_m2", "تدعيم جوانب الخندق", g["shoring"]),
        ("asphalt_m2", "قص وإعادة الأسفلت وطبقة الأساس", g["asphalt"]),
        ("dewatering_m", "نزح المياه الجوفية", 1.0 if p.get("ground_water") else 0.0),
        ("testing_m", "اختبار الضغط والتطهير", 1.0),
        ("tape_m", "شريط تحذيري كاشف", 1.0),
    ]
    for key, name, qty in rows:
        c = comp(rates, key, name, qty, code, missing)
        if c:
            comps.append(c)
    item = {"code": code, "description": p["description"], "unit": "م.ط",
            "qty": p["length_m"], "components": comps}
    return item, g, factor


def checks(p, g, d, factor, proj):
    w = []
    mat = p["material"].upper()
    if p["cover_m"] < d["min_cover_m"]:
        w.append(f"الغطاء {p['cover_m']} م أقل من الحد الأدنى {d['min_cover_m']} م — حماية خرسانية أو تأكيد من المواصفة.")
    if g["depth"] > d["deep_trench_m"]:
        w.append(f"عمق الخندق {g['depth']:.2f} م > {d['deep_trench_m']} م — يتطلب تصميم تدعيم خاص ودراسة سلامة.")
    if g["shoring"]:
        w.append(f"التدعيم محمّل لأن العمق {g['depth']:.2f} م > {d['shoring_depth_m']} م.")
    if p.get("ground_water"):
        w.append("مياه جوفية: تأكد من طريقة النزح وتأثيرها على الإنتاجية (معامل التعديل).")
    if mat in FLEXIBLE:
        w.append("أنبوب مرن: جودة الفرشة والتغليف والدمك حاسمة لمنع الانبعاج — راجع متطلبات المصنع.")
    for m, lo_dn, hi_dn, lo, hi in PRODUCTIVITY_NORMS:
        if mat == m and lo_dn <= p["dn_mm"] <= hi_dn:
            eff = p["lay_productivity_m_day"] * factor
            if not lo * 0.6 <= eff <= hi * 1.2:
                w.append(f"إنتاجية التمديد الفعلية {eff:.0f} م/يوم بعيدة عن النطاق الإرشادي {lo}–{hi} م/يوم.")
            break
    crews = p.get("crews", 1)
    days = p["length_m"] / (p["lay_productivity_m_day"] * factor * crews)
    available = proj.get("duration_months", 0) * proj.get("working_days_per_month", 26)
    if available and days > 0.7 * available:
        w.append(f"مدة التمديد {days:.0f} يوم عمل بـ {crews} فرقة تتجاوز 70% من المدة المتاحة ({available:g} يوم) — "
                 "زِد الفرق وحمّل تكلفتها أو راجع البرنامج.")
    return w


def sheet(items_geo, d):
    out = ["# الورقة الهندسية لبنود الخطوط", "",
           "| البند | المادة/القطر | الطول م | الغطاء م | العرض م | العمق م | حفر م³/م | صخر م³/م | فرشة | تغليف | ردم | فائض | تدعيم م²/م | أسفلت م²/م |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for p, g, _, _ in items_geo:
        out.append(
            f"| {p['code']} | {p['material']} DN{p['dn_mm']} | {p['length_m']:,g} | {p['cover_m']} | {g['width']:.2f} | "
            f"{g['depth']:.2f} | {g['excavation']:.3f} | {g['rock']:.3f} | {g['bedding']:.3f} | {g['surround']:.3f} | "
            f"{g['backfill']:.3f} | {g['disposal']:.3f} | {g['shoring']:.2f} | {g['asphalt']:.2f} |")
    out += ["", "## إجمالي الكميات الهندسية", "", "| النشاط | الكمية |", "|---|---|"]
    totals = {}
    for p, g, _, _ in items_geo:
        for k in ("excavation", "rock", "bedding", "surround", "backfill", "disposal", "shoring", "asphalt"):
            totals[k] = totals.get(k, 0.0) + g[k] * p["length_m"]
    labels = {"excavation": "حفر م³", "rock": "حفر صخري م³", "bedding": "فرشة م³", "surround": "تغليف م³",
              "backfill": "ردم م³", "disposal": "نقل فائض م³ (مفكك)", "shoring": "تدعيم م²", "asphalt": "إعادة أسفلت م²"}
    for k, v in totals.items():
        out.append(f"| {labels[k]} | {v:,.1f} |")
    out += ["", "## الفحوص الهندسية", ""]
    for p, _, _, w in items_geo:
        for x in w:
            out.append(f"- **{p['code']}**: {x}")
    out += ["", "الافتراضات التصميمية (إرشادية — طابقها مع المواصفات): " +
            "، ".join(f"{k}={v}" for k, v in d.items())]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--out", required=True, help="output project JSON for pricing_calc.py")
    ap.add_argument("--sheet", help="write the engineering sheet to this Markdown file")
    args = ap.parse_args()

    with open(args.project, encoding="utf-8") as f:
        src = json.load(f)
    d = {**DEFAULT_DESIGN, **src.get("design", {})}
    rates = src.get("rates", {})
    missing = set()
    generated, items_geo = [], []
    for p in src.get("pipelines", []):
        try:
            item, g, factor = build_item(p, rates, d, missing)
        except KeyError as e:
            sys.exit(f"خطأ: الحقل {e} مفقود في الخط {p.get('code')}")
        generated.append(item)
        items_geo.append((p, g, factor, checks(p, g, d, factor, src["project"])))
    if missing:
        sys.exit("أسعار ناقصة في rates — لا تُخترع الأسعار، أضفها من عروض الموردين:\n- " + "\n- ".join(sorted(missing)))

    out = copy.deepcopy(src)
    for k in ("pipelines", "rates", "design"):
        out.pop(k, None)
    out["boq"] = generated + src.get("boq", [])
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    text = sheet(items_geo, d)
    if args.sheet:
        with open(args.sheet, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    print(text)
    print(f"\nتم إنشاء ملف التسعير: {args.out}")


if __name__ == "__main__":
    main()
