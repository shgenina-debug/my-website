#!/usr/bin/env python3
"""حاسبة تسعير مشاريع المقاولات (السعودية).

Reads a project JSON (see examples/sample_project.json), builds the unit-rate
analysis of every BOQ item, adds site overheads and markups, spreads them
across items in a balanced way, and prints the priced BOQ, the bid summary
with VAT, and a sensitivity analysis.

Usage:
    python3 pricing_calc.py project.json [--csv priced_boq.csv] [--sensitivity 0.10]
"""

import argparse
import csv
import json
import sys

COMPONENT_TYPES = {
    "material": "مواد",
    "labor": "عمالة",
    "equipment": "معدات",
    "subcontract": "مقاول باطن",
}

MARKUP_LABELS = {
    "head_office": "المصاريف العامة للشركة",
    "finance": "تكلفة التمويل",
    "bonds_insurance": "الضمانات البنكية والتأمين",
    "contingency": "المخاطر والطوارئ",
}


def component_unit_cost(c):
    """Cost of one component per unit of the BOQ item."""
    if "productivity" in c:
        # crew/equipment daily cost divided by units produced per day
        if c["productivity"] <= 0:
            raise ValueError(f"productivity must be > 0 in component {c.get('name')}")
        cost = c["daily_cost"] / c["productivity"]
    else:
        cost = c["qty"] * c["rate"]
    return cost * (1 + c.get("waste", 0.0))


def item_direct_unit_cost(item, overrides=None):
    breakdown = {t: 0.0 for t in COMPONENT_TYPES}
    for c in item.get("components", []):
        if c["type"] not in COMPONENT_TYPES:
            raise ValueError(f"unknown component type {c['type']!r} in item {item['code']}")
        cost = component_unit_cost(c)
        if overrides and c.get("key") in overrides:
            cost *= 1 + overrides[c["key"]]
        breakdown[c["type"]] += cost
    return sum(breakdown.values()), breakdown


def site_overheads_total(project):
    total = 0.0
    rows = []
    for oh in project.get("site_overheads", []):
        if "monthly_cost" in oh:
            months = oh.get("months", project["project"]["duration_months"])
            amount = oh.get("count", 1) * oh["monthly_cost"] * months
        else:
            amount = oh["lump_sum"]
        rows.append((oh["name"], amount))
        total += amount
    return total, rows


def price(project, overrides=None):
    items = []
    direct = 0.0
    for item in project["boq"]:
        unit, breakdown = item_direct_unit_cost(item, overrides)
        total = unit * item["qty"]
        items.append({**item, "direct_unit": unit, "breakdown": breakdown, "direct_total": total})
        direct += total

    site_total, site_rows = site_overheads_total(project)
    project_cost = direct + site_total

    m = project.get("markups", {})
    markup_rows = [(MARKUP_LABELS[k], project_cost * m.get(k, 0.0)) for k in MARKUP_LABELS]
    total_cost = project_cost + sum(a for _, a in markup_rows)
    profit = total_cost * m.get("profit", 0.0)
    bid = total_cost + profit
    vat_rate = project["project"].get("vat_rate", 0.15)
    vat = bid * vat_rate

    # balanced spread: every item carries the same uplift on its direct cost
    factor = bid / direct if direct else 0.0
    priced_sum = 0.0
    for it in items:
        it["unit_price"] = round(it["direct_unit"] * factor, 2)
        it["total_price"] = round(it["unit_price"] * it["qty"], 2)
        priced_sum += it["total_price"]

    return {
        "items": items,
        "direct": direct,
        "site_total": site_total,
        "site_rows": site_rows,
        "project_cost": project_cost,
        "markup_rows": markup_rows,
        "total_cost": total_cost,
        "profit": profit,
        "bid": bid,
        "priced_sum": priced_sum,
        "vat_rate": vat_rate,
        "vat": vat,
        "factor": factor,
    }


def fmt(x):
    return f"{x:,.2f}"


def pct(x, base):
    return f"{(x / base * 100) if base else 0:.2f}%"


def report(project, r):
    p = project["project"]
    out = [f"# التسعير: {p['name']}", ""]
    if p.get("location"):
        out.append(f"- الموقع: {p['location']}")
    out.append(f"- مدة التنفيذ (بالأشهر): {p['duration_months']}")
    out.append(f"- العملة: {p.get('currency', 'ر.س')} — الأسعار غير شاملة ضريبة القيمة المضافة")
    out += ["", "## تحليل أسعار البنود (التكلفة المباشرة للوحدة)", ""]
    out.append("| البند | الوصف | الوحدة | " + " | ".join(COMPONENT_TYPES.values()) + " | التكلفة المباشرة للوحدة |")
    out.append("|---|---|---|" + "---|" * len(COMPONENT_TYPES) + "---|")
    for it in r["items"]:
        cells = " | ".join(fmt(it["breakdown"][t]) for t in COMPONENT_TYPES)
        out.append(f"| {it['code']} | {it['description']} | {it['unit']} | {cells} | {fmt(it['direct_unit'])} |")

    out += ["", "## جدول الكميات المسعَّر", ""]
    out.append("| البند | الوصف | الوحدة | الكمية | سعر الوحدة | الإجمالي |")
    out.append("|---|---|---|---|---|---|")
    for it in r["items"]:
        out.append(
            f"| {it['code']} | {it['description']} | {it['unit']} | {it['qty']:,g} | "
            f"{fmt(it['unit_price'])} | {fmt(it['total_price'])} |"
        )
    out.append(f"| | **الإجمالي قبل الضريبة** | | | | **{fmt(r['priced_sum'])}** |")

    out += ["", "## مصاريف الموقع غير المباشرة", ""]
    out.append("| البند | المبلغ |")
    out.append("|---|---|")
    for name, amount in r["site_rows"]:
        out.append(f"| {name} | {fmt(amount)} |")

    bid = r["bid"]
    out += ["", "## ملخص العرض المالي", ""]
    out.append("| المكوّن | المبلغ | النسبة من سعر العرض |")
    out.append("|---|---|---|")
    out.append(f"| التكلفة المباشرة | {fmt(r['direct'])} | {pct(r['direct'], bid)} |")
    out.append(f"| مصاريف الموقع غير المباشرة | {fmt(r['site_total'])} | {pct(r['site_total'], bid)} |")
    out.append(f"| **تكلفة المشروع** | **{fmt(r['project_cost'])}** | {pct(r['project_cost'], bid)} |")
    for name, amount in r["markup_rows"]:
        out.append(f"| {name} | {fmt(amount)} | {pct(amount, bid)} |")
    out.append(f"| **إجمالي التكلفة** | **{fmt(r['total_cost'])}** | {pct(r['total_cost'], bid)} |")
    out.append(f"| الربح | {fmt(r['profit'])} | {pct(r['profit'], bid)} |")
    out.append(f"| **سعر العرض قبل الضريبة** | **{fmt(bid)}** | 100.00% |")
    out.append(f"| ضريبة القيمة المضافة ({r['vat_rate'] * 100:g}%) | {fmt(r['vat'])} | |")
    out.append(f"| **سعر العرض شامل الضريبة** | **{fmt(bid + r['vat'])}** | |")
    out += [
        "",
        f"- معامل التحميل المتوازن على التكلفة المباشرة: {r['factor']:.4f}",
        f"- فرق التقريب بين مجموع الجدول والملخص: {fmt(r['priced_sum'] - bid)}",
        f"- المبلغ المعتمد في خطاب العرض هو مجموع الجدول المسعَّر: {fmt(r['priced_sum'])} قبل الضريبة، "
        f"و{fmt(r['priced_sum'] * (1 + r['vat_rate']))} شامل الضريبة.",
    ]
    warnings = sanity_warnings(project, r)
    if warnings:
        out += ["", "## تنبيهات المعقولية", ""] + [f"- ⚠️ {w}" for w in warnings]
    return "\n".join(out)


# indicative ranges from references/methodology.md, as a share of the base shown
SANITY_RANGES = [
    ("مصاريف الموقع من التكلفة المباشرة", "site_total", "direct", 0.08, 0.15),
]
MARKUP_RANGES = {
    "head_office": (0.03, 0.07),
    "contingency": (0.02, 0.10),
    "profit": (0.05, 0.15),
}


def sanity_warnings(project, r):
    warnings = []
    for label, num, den, lo, hi in SANITY_RANGES:
        share = r[num] / r[den] if r[den] else 0.0
        if not lo <= share <= hi:
            warnings.append(f"{label} = {share * 100:.1f}% خارج النطاق المعتاد ({lo * 100:g}% – {hi * 100:g}%). راجع الحساب التفصيلي.")
    m = project.get("markups", {})
    labels = {**MARKUP_LABELS, "profit": "الربح"}
    for k, (lo, hi) in MARKUP_RANGES.items():
        v = m.get(k, 0.0)
        if not lo <= v <= hi:
            warnings.append(f"نسبة {labels[k]} = {v * 100:g}% خارج النطاق المعتاد ({lo * 100:g}% – {hi * 100:g}%).")
    for it in r["items"]:
        if it["direct_unit"] <= 0:
            warnings.append(f"البند {it['code']} بدون تكلفة — تأكد من تسعيره أو وضّح سبب الصفر.")
    return warnings


def sensitivity(project, base, delta):
    keys = sorted({c["key"] for it in project["boq"] for c in it.get("components", []) if c.get("key")})
    if not keys:
        return ""
    out = ["", f"## تحليل الحساسية (±{delta * 100:g}% على تكلفة المورد، بنفس نسب الإضافات)", ""]
    out.append("| المورد | الأثر على سعر العرض | النسبة |")
    out.append("|---|---|---|")
    rows = []
    for k in keys:
        diff = price(project, {k: delta})["bid"] - base["bid"]
        rows.append((k, diff))
    for k, diff in sorted(rows, key=lambda x: -abs(x[1])):
        out.append(f"| {k} | ±{fmt(abs(diff))} | ±{pct(abs(diff), base['bid'])} |")
    return "\n".join(out)


def write_csv(path, r):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["البند", "الوصف", "الوحدة", "الكمية", "التكلفة المباشرة للوحدة", "سعر الوحدة", "الإجمالي"])
        for it in r["items"]:
            w.writerow([it["code"], it["description"], it["unit"], it["qty"],
                        round(it["direct_unit"], 2), it["unit_price"], it["total_price"]])
        w.writerow([])
        w.writerow(["", "الإجمالي قبل الضريبة", "", "", "", "", round(r["priced_sum"], 2)])
        w.writerow(["", f"ضريبة القيمة المضافة {r['vat_rate'] * 100:g}%", "", "", "", "", round(r["vat"], 2)])
        w.writerow(["", "الإجمالي شامل الضريبة", "", "", "", "", round(r["bid"] + r["vat"], 2)])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", help="project JSON file")
    ap.add_argument("--csv", help="write the priced BOQ to this CSV file")
    ap.add_argument("--sensitivity", type=float, default=0.10, help="sensitivity delta (default 0.10)")
    args = ap.parse_args()

    with open(args.project, encoding="utf-8") as f:
        project = json.load(f)

    try:
        r = price(project)
    except (KeyError, ValueError) as e:
        sys.exit(f"خطأ في ملف الإدخال: {e}")

    print(report(project, r))
    print(sensitivity(project, r, args.sensitivity))
    if args.csv:
        write_csv(args.csv, r)
        print(f"\nتم حفظ جدول الكميات المسعَّر في: {args.csv}")


if __name__ == "__main__":
    main()
