#!/usr/bin/env python3
"""أداة التسعير العامة: من نوع المشروع إلى ملف جاهز للحاسبة.

Subcommands
-----------
types
    List project types and their disciplines.
new --type <project_type> --name <name> --out project.json [--duration 12] [--templates id1,id2]
    Create a project skeleton with every library template of the type's
    disciplines (qty 0) and the resources they use (rate null). Fill the
    quantities and the resource prices, delete what is not needed.
import BOQ.xlsx --type <project_type> --out project.json [--sheet-name S] [--header-row N] [--no-match]
    Read the owner's BOQ from Excel (.xlsx) or CSV, detect the columns
    (item / description / unit / quantity), keep rows without quantity as
    section titles, and suggest a library template (breakdown) for every
    item. Review the matches: wrong ones are cleared or replaced by hand.
build project.json --out priced_input.json [--sheet sheet.md]
    Resolve resource references (`res`) to priced components, expand
    water pipelines (trench geometry, via water_assemblies.py), drop
    zero-quantity items, run the discipline checks, and write a file
    that pricing_calc.py prices.

Prices never come from the library: a missing resource price stops the
build with the list of what is missing.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIB_PATH = os.path.join(HERE, "..", "library", "library.json")
sys.path.insert(0, os.path.join(HERE, "..", "..", "water-pricing", "scripts"))
import water_assemblies as wa  # noqa: E402
import boq_import  # noqa: E402


def load_library():
    with open(LIB_PATH, encoding="utf-8") as f:
        return json.load(f)


def cmd_types(lib, _args):
    for k, t in lib["project_types"].items():
        names = "، ".join(lib["disciplines"][d]["name"] for d in t["disciplines"])
        n = sum(1 for x in lib["templates"] if x["d"] in t["disciplines"])
        print(f"{k:18} {t['name']} — {names} ({n} بند)")


def cmd_new(lib, args):
    if args.type not in lib["project_types"]:
        sys.exit(f"نوع غير معروف: {args.type}. الأنواع: {', '.join(lib['project_types'])}")
    discs = lib["project_types"][args.type]["disciplines"]
    wanted = set(args.templates.split(",")) if args.templates else None
    items, used, counters = [], {}, {}
    for t in lib["templates"]:
        if t["d"] not in discs or (wanted and t["id"] not in wanted):
            continue
        prefix = lib["disciplines"][t["d"]]["prefix"]
        counters[prefix] = counters.get(prefix, 0) + 1
        items.append({"code": f"{prefix}-{counters[prefix]:02d}", "template": t["id"], "section": t["section"],
                      "description": t["description"], "unit": t["unit"], "qty": 0,
                      "components": [dict(c) for c in t["components"]]})
        for c in t["components"]:
            used[c["res"]] = {**lib["resources"][c["res"]], "rate": None}
    project = {
        "_note": "هيكل مولّد من مكتبة البنود — أدخل الكميات وأسعار الموارد (rate) من عروض الموردين، واحذف ما لا يلزم.",
        "project": {"name": args.name, "type": args.type, "location": "", "currency": "ر.س",
                    "duration_months": args.duration, "vat_rate": 0.15, "working_days_per_month": 26},
        "resources": used,
        "boq": items,
        "site_overheads": [],
        "markups": {"head_office": 0.05, "finance": 0.01, "bonds_insurance": 0.01, "contingency": 0.03, "profit": 0.08},
    }
    if "water_networks" in discs:
        project["pipelines"], project["rates"] = [], {}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(project, f, ensure_ascii=False, indent=2)
    print(f"تم إنشاء {args.out}: {len(items)} بنداً و{len(used)} مورداً تحتاج أسعاراً.")


def cmd_import(lib, args):
    if args.type not in lib["project_types"]:
        sys.exit(f"نوع غير معروف: {args.type}. الأنواع: {', '.join(lib['project_types'])}")
    try:
        sheets, rows = boq_import.read_table(args.file, args.sheet_name)
    except (ValueError, KeyError, OSError) as e:
        sys.exit(f"تعذرت قراءة الملف: {e}")
    if args.header_row:
        header, cols = args.header_row - 1, boq_import.detect_header(rows[args.header_row - 1:args.header_row])[1]
    else:
        header, cols = boq_import.detect_header(rows)
    if header is None or not {"desc", "qty"} <= set(cols):
        sys.exit("لم أتعرف على أعمدة الوصف والكمية — حدد صف العناوين بـ --header-row. الأوراق: " + "، ".join(sheets))
    items = boq_import.rows_to_items(rows, header, cols)
    discs = lib["project_types"][args.type]["disciplines"]
    tpl = {t["id"]: t for t in lib["templates"]}
    used, matched, report = {}, 0, []
    for it in items:
        it["components"] = []
        tid, score = (None, 0) if args.no_match else boq_import.best_template(it, lib["templates"], discs)
        if tid:
            matched += 1
            it.update(template=tid, match_score=score, components=[dict(c) for c in tpl[tid]["components"]])
            for c in tpl[tid]["components"]:
                used.setdefault(c["res"], {**lib["resources"][c["res"]], "rate": None})
        report.append(f"{it['code']:>8} | {it['description'][:55]:55} | {(tpl[tid]['description'][:45] + f' ({score})') if tid else '— بدون مطابقة: فكّكه يدوياً'}")
    name = args.name or os.path.splitext(os.path.basename(args.file))[0]
    project = {
        "_note": "مستورد من ملف المالك — راجع المطابقات المقترحة (match_score) وأدخل أسعار الموارد. البنود بدون مكونات تحتاج تفكيكاً يدوياً.",
        "project": {"name": name, "type": args.type, "location": "", "currency": "ر.س", "duration_months": args.duration,
                    "vat_rate": 0.15, "working_days_per_month": 26, "source_file": os.path.basename(args.file)},
        "resources": used, "boq": items, "site_overheads": [],
        "markups": {"head_office": 0.05, "finance": 0.01, "bonds_insurance": 0.01, "contingency": 0.03, "profit": 0.08},
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(project, f, ensure_ascii=False, indent=2)
    labels = {"code": "البند", "desc": "الوصف", "unit": "الوحدة", "qty": "الكمية"}
    print(f"الورقة: {args.sheet_name or sheets[0]} — صف العناوين: {header + 1} — الأعمدة: "
          + "، ".join(f"{labels[k]}={chr(65 + v) if v < 26 else v + 1}" for k, v in cols.items()))
    print("\n".join(report))
    print(f"\nتم استيراد {len(items)} بنداً، منها {matched} بمطابقة مقترحة و{len(items) - matched} تحتاج تفكيكاً يدوياً → {args.out}")


def resolve_component(c, resources, lib_res, code, missing):
    if "res" not in c:
        return dict(c)
    key = c["res"]
    r = {**lib_res.get(key, {}), **resources.get(key, {})}
    rate = r.get("rate")
    if not isinstance(rate, (int, float)) or "type" not in r:
        missing.add(f"{key} — {r.get('name', 'مورد غير معرّف')} ({r.get('unit', '')}) [البند {code}]")
        return None
    out = {"type": r["type"], "name": c.get("name") or r.get("name", key), "key": r.get("group", key)}
    if "productivity" in c:
        out.update(daily_cost=rate, productivity=c["productivity"])
    else:
        out.update(qty=c["qty"], rate=rate)
    if c.get("waste"):
        out["waste"] = c["waste"]
    return out


def qty_by_template(items):
    q = {}
    for it in items:
        if it.get("template"):
            q[it["template"]] = q.get(it["template"], 0) + it["qty"]
    return q


def discipline_checks(lib, items):
    q = qty_by_template(items)
    present = {k for k, v in q.items() if v > 0}
    out = []
    for c in lib.get("checks", []):
        if c["kind"] == "ratio":
            num, den = sum(q.get(i, 0) for i in c["num"]), sum(q.get(i, 0) for i in c["den"])
            if num and den:
                v = num / den * c.get("factor", 1)
                if not c["min"] <= v <= c["max"]:
                    out.append(f"{c['label']} = {v:.0f} {c['unit']} خارج النطاق الإرشادي {c['min']}–{c['max']}.")
        elif c["kind"] == "requires":
            if present & set(c["if"]) and not present & set(c["then"]):
                out.append(c["msg"])
    return out


def cmd_build(lib, args):
    with open(args.project, encoding="utf-8") as f:
        src = json.load(f)
    resources, lib_res = src.get("resources", {}), lib["resources"]
    missing, items, dropped = set(), [], []
    for it in src.get("boq", []):
        if not it.get("qty"):
            dropped.append(it["code"])
            continue
        comps = [resolve_component(c, resources, lib_res, it["code"], missing) for c in it.get("components", [])]
        items.append({**it, "components": [c for c in comps if c]})

    d = {**wa.DEFAULT_DESIGN, **src.get("design", {})}
    pipe_items, geo = [], []
    for p in src.get("pipelines", []):
        item, g, factor = wa.build_item(p, src.get("rates", {}), d, missing)
        pipe_items.append(item)
        geo.append((p, g, factor, wa.checks(p, g, d, factor, src["project"])))
    if missing:
        sys.exit("أسعار ناقصة — لا تُخترع الأسعار، أضفها من عروض الموردين:\n- " + "\n- ".join(sorted(missing)))

    out = {k: v for k, v in src.items() if k not in ("pipelines", "rates", "design", "resources")}
    out["boq"] = pipe_items + items
    rng = lib["project_types"].get(src["project"].get("type"), {}).get("site_overhead_range")
    if rng and "site_overhead_range" not in out["project"]:
        out["project"] = {**out["project"], "site_overhead_range": rng}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    lines = [f"# الورقة الهندسية — {src['project'].get('name', '')}", ""]
    ptype = src["project"].get("type")
    if ptype in lib["project_types"]:
        lines.append(f"- نوع المشروع: {lib['project_types'][ptype]['name']}")
    lines.append(f"- بنود مسعّرة: {len(out['boq'])} — بنود مستبعدة لأن كميتها صفر: {len(dropped)}"
                 + (f" ({', '.join(dropped)})" if dropped else ""))
    if geo:
        lines += ["", wa.sheet(geo, d)]
    checks = discipline_checks(lib, items)
    lines += ["", "## الفحوص الهندسية حسب التخصص", ""]
    lines += [f"- ⚠️ {c}" for c in checks] or ["- لا توجد ملاحظات."]
    text = "\n".join(lines)
    if args.sheet:
        with open(args.sheet, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    print(text)
    print(f"\nتم إنشاء ملف التسعير: {args.out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("types")
    n = sub.add_parser("new")
    n.add_argument("--type", required=True)
    n.add_argument("--name", required=True)
    n.add_argument("--out", required=True)
    n.add_argument("--duration", type=float, default=12)
    n.add_argument("--templates", help="comma-separated template ids (default: all of the type)")
    im = sub.add_parser("import")
    im.add_argument("file")
    im.add_argument("--type", required=True)
    im.add_argument("--out", required=True)
    im.add_argument("--name")
    im.add_argument("--sheet-name")
    im.add_argument("--header-row", type=int, help="1-based row number of the column titles")
    im.add_argument("--duration", type=float, default=12)
    im.add_argument("--no-match", action="store_true")
    b = sub.add_parser("build")
    b.add_argument("project")
    b.add_argument("--out", required=True)
    b.add_argument("--sheet")
    args = ap.parse_args()
    lib = load_library()
    {"types": cmd_types, "new": cmd_new, "import": cmd_import, "build": cmd_build}[args.cmd](lib, args)


if __name__ == "__main__":
    main()
