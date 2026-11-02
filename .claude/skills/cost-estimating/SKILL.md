---
name: cost-estimating
description: التسعير الهندسي العام لأي مشروع مقاولات حسب نوعه — مبنى متكامل، إلكتروميكانيك (كهرباء، تكييف، سباكة وحريق)، معماري وتشطيبات، إنشائي، شبكات مياه وصرف، طرق. يحدد التخصصات من نوع المشروع، ويبني جدول الكميات من مكتبة بنود مفككة (مواد + عمالة + معدات + باطن)، ويسعّر بأسعار موارد موثقة، ويجري الفحوص الهندسية حسب التخصص وباريتو والحساسية، ويغذي منصة التسعير. Use for pricing any construction project type with an engineering breakdown of every BOQ item.
metadata:
  version: "1"
---

# التسعير الهندسي العام

## الفكرة
- **مكتبة البنود** `library/library.json`: لكل تخصص بنود مفككة بمعدلات استهلاك وإنتاجية إرشادية — **بدون أسعار**.
- **أسعار الموارد** تُدخل لكل مشروع في `resources` (مرة واحدة لكل مورد، وتنعكس على كل البنود).
- نفس الملف يعمل في الأدوات وفي المنصة `pricing-platform/index.html`.

## سير العمل
1. **حدد نوع المشروع** (`build_project.py types`) — مثلاً «إلكتروميكانيك» = كهرباء + تكييف + سباكة وحريق. إن لم يذكره المستخدم صراحةً فاستنتجه من الوثائق واذكر ذلك.
2. **اقرأ قسم التخصص** في `references/disciplines.md` (الأقسام، التفكيك، المخفي، الفحوص).
3. **ابنِ جدول الكميات:**
   - إن وُجد جدول للمالك: طابق كل بند مع قالب من المكتبة (`template`) واحتفظ بترقيم ووصف ووحدة المالك حرفياً؛ عدّل المكونات لتطابق الوصف والمواصفات. البند بلا قالب يُفكك يدوياً بنفس المنطق.
   - إن لم يوجد جدول (تقدير مبدئي): `build_project.py new --type <type>` يولّد كل بنود التخصصات بكمية صفر — أدخل الكميات من المخططات أو اطلبها، واحذف غير المطلوب.
4. **أسعار الموارد** من المستخدم أو عروض الموردين أو مصدر مؤرخ؛ اكتب المصدر في `resources.<key>.source`. الأداة ترفض البناء إن نقص سعر.
5. **التشغيل:**
   ```bash
   python3 .claude/skills/cost-estimating/scripts/build_project.py build project.json --out priced_input.json --sheet sheet.md
   python3 .claude/skills/saudi-project-pricing/scripts/pricing_calc.py priced_input.json --csv priced_boq.csv
   ```
6. **المصاريف والإضافات والمراجعة** حسب `saudi-project-pricing` (المنهجية، النظامية، قوائم التحقق).

## صيغة البند
```json
{"code": "EL-01", "template": "el-light-point", "section": "تمديدات", "description": "...", "unit": "نقطة", "qty": 420,
 "components": [{"res": "conduit_20", "qty": 7, "waste": 0.05}, {"res": "crew_electrician", "productivity": 12}]}
```
- `{"res", "qty", "waste"}` — مورد بالكمية لكل وحدة بند. `{"res", "productivity"}` — فرقة/معدة: سعر المورد يومي، والإنتاجية وحدات بند/يوم.
- المكوّن الحر (بدون `res`) بصيغة `pricing_calc.py` المعتادة مقبول أيضاً.
- `resources.<key>`: `{"name", "type": material|labor|equipment|subcontract, "unit", "group", "rate", "source"}` — `group` يجمع الموارد في تحليل الحساسية.
- خطوط المياه بالمتر الطولي في `pipelines` + `rates` (انظر `water-pricing`).

## تطوير المكتبة والمنصة
- أضف قوالب/موارد/فحوص إلى `library/library.json` ثم:
  `python3 .claude/skills/cost-estimating/scripts/build_platform.py` (يضمّن المكتبة والأمثلة في المنصة).
- منطق الحساب في المنصة نسخة من `build_project.py` + `water_assemblies.py` + `pricing_calc.py`؛ أي تعديل يُعكس في الطرفين. أمثلة التحقق: الإلكتروميكانيك 2,569,979.64 والمياه 8,600,142.26 ر.س قبل الضريبة.
