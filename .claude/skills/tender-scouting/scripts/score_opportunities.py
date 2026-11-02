#!/usr/bin/env python3
"""مصفوفة قرار المشاركة (Go / No-go) لسجل الفرص.

Reads a pipeline CSV (see templates/pipeline.csv), scores each opportunity
0-100 with the weighted criteria in SKILL.md, applies the qualification
knock-out rule, flags close deadlines, and writes a ranked Markdown report.

Usage:
    python3 score_opportunities.py pipeline.csv [--out ranked.md] [--today 2026-11-02]
"""

import argparse
import csv
import datetime as dt
import sys

# column -> (weight, label)
CRITERIA = {
    "scope_fit": (25, "ملاءمة النطاق"),
    "qualification": (15, "التصنيف والتأهيل"),
    "capacity": (15, "القيمة مقابل الطاقة"),
    "location": (10, "الموقع"),
    "client_score": (10, "العميل وسجل الصرف"),
    "competition": (10, "المنافسة"),
    "time": (10, "الوقت المتاح"),
    "risk": (5, "المخاطر"),
}
assert sum(w for w, _ in CRITERIA.values()) == 100


def score(row):
    total = 0.0
    missing = []
    for col, (weight, label) in CRITERIA.items():
        raw = (row.get(col) or "").strip()
        if raw == "":
            missing.append(label)
            continue
        v = float(raw)
        if not 0 <= v <= 5:
            raise ValueError(f"{row.get('id')}: {col}={v} must be between 0 and 5")
        total += v / 5 * weight
    return round(total, 1), missing


def decision(row, total, missing):
    if (row.get("qualification") or "").strip() == "0":
        return "No-go ⛔ (التأهيل غير مستوفى)"
    if missing:
        return "ناقص بيانات ❔"
    if total >= 70:
        return "Go ✅"
    if total >= 50:
        return "Review 🟡"
    return "No-go ⛔"


def days_left(row, today):
    raw = (row.get("submission_deadline") or "").strip()
    if not raw:
        return None
    try:
        return (dt.date.fromisoformat(raw) - today).days
    except ValueError:
        return None


def fmt_value(raw):
    try:
        return f"{float(raw):,.0f}"
    except (TypeError, ValueError):
        return raw or "—"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pipeline")
    ap.add_argument("--out")
    ap.add_argument("--today", default=dt.date.today().isoformat())
    args = ap.parse_args()
    today = dt.date.fromisoformat(args.today)

    with open(args.pipeline, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    results = []
    for r in rows:
        try:
            total, missing = score(r)
        except ValueError as e:
            sys.exit(f"خطأ: {e}")
        results.append((r, total, missing, decision(r, total, missing), days_left(r, today)))
    results.sort(key=lambda x: -x[1])

    out = [f"# ترتيب الفرص — {today.isoformat()}", ""]
    out.append("| # | الفرصة | العميل | المدينة | القيمة التقديرية (ر.س) | الدرجة | القرار | أيام حتى التقديم | المصدر |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for i, (r, total, missing, dec, left) in enumerate(results, 1):
        left_s = "—" if left is None else (f"⚠️ {left}" if 0 <= left <= 14 else ("منتهية" if left < 0 else str(left)))
        out.append(
            f"| {i} | {r.get('title', '')} | {r.get('client', '')} | {r.get('city', '')} | "
            f"{fmt_value(r.get('est_value_sar'))} | {total} | {dec} | {left_s} | {r.get('source_url', '')} |"
        )

    urgent = [x for x in results if x[4] is not None and 0 <= x[4] <= 14 and x[3].startswith(("Go", "Review"))]
    if urgent:
        out += ["", "## مواعيد قريبة (خلال 14 يوماً) تحتاج قراراً"]
        out += [f"- {r.get('title')} — {left} يوم — {dec}" for r, _, _, dec, left in urgent]

    incomplete = [x for x in results if x[2]]
    if incomplete:
        out += ["", "## بيانات تقييم ناقصة"]
        out += [f"- {r.get('title')}: {', '.join(m)}" for r, _, m, _, _ in incomplete]

    out += ["", "الأوزان: " + "، ".join(f"{label} {w}" for w, label in CRITERIA.values()),
            "القرار: ≥70 Go، 50–69 Review، <50 No-go، والتأهيل = 0 يعني No-go."]
    text = "\n".join(out)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
