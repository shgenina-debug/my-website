---
name: water-pricing
description: تسعير مشاريع المياه والصرف الصحي بتفكيك هندسي للبنود (Breakdown) — حساب هندسة الخندق (العرض، العمق، الحفر، الصخر، الفرشة، التغليف، الردم، الفائض، التدعيم، الأسفلت) لكل متر من الخط، تحويلها إلى مكونات تكلفة، فحوص هندسية ومعقولية الإنتاجية، ثم التسعير الكامل عبر حاسبة saudi-project-pricing ومنصة التسعير التفاعلية. Use for pricing water/sewer pipelines, house connections and networks with engineering breakdown and analysis.
metadata:
  version: "1"
---

# تسعير مشاريع المياه بالتفكيك الهندسي

يبني على منهجية `saudi-project-pricing` (اقرأ `SKILL.md` و`references/methodology.md` هناك) ويضيف طبقة هندسية خاصة بالخطوط والشبكات.

## سير العمل
1. **استلام جدول الكميات** وتصنيف البنود:
   - بنود خطوط (م.ط) شاملة الحفر والردم ← تُدخل في `pipelines` لتُفكك هندسياً.
   - بنود عددية (توصيلات، محابس، غرف، حنفيات) ← تُدخل في `boq` بمكوناتها مباشرة.
   - بنود الحفر/الأسفلت إن كانت منفصلة في جدول المالك ← لا تكررها داخل بند الخط (احذف معدلها من `rates` أو اجعل البند الخطي بدونها). **انتبه للازدواج**.
2. **المعطيات الهندسية لكل خط**: المادة، DN، القطر الخارجي الفعلي OD (من كتالوج المصنع)، الطول، الغطاء فوق ظهر الأنبوب، سطح الأرض (أسفلت/ترابي)، نسبة الصخر (من تقرير التربة)، المياه الجوفية، استيراد مواد الردم أم لا.
3. **مكتبة الأسعار `rates`**: سعر لكل نشاط (م³ حفر، م³ فرشة، م² تدعيم، م² أسفلت...) — **من عروض الموردين ومقاولي الباطن وسجلات الشركة فقط**. الأداة ترفض العمل إذا نقص سعر بدلاً من افتراضه.
4. **الإنتاجية**: من سجلات الشركة، مع معاملات تعديل (`productivity_factors`) للظروف — قارنها بـ `water-projects-knowledge/references/productivity-norms.md`.
5. **التشغيل**:
   ```bash
   python3 .claude/skills/water-pricing/scripts/water_assemblies.py project.json --out priced_input.json --sheet engineering_sheet.md
   python3 .claude/skills/saudi-project-pricing/scripts/pricing_calc.py priced_input.json --csv priced_boq.csv
   ```
6. **المنصة التفاعلية**: `pricing-platform/index.html` تقرأ وتصدر نفس صيغة JSON — للتعديل السريع، سيناريوهات الربح، الحساسية، وتحليل باريتو أمام صاحب القرار.

## التحليل الهندسي المطلوب في كل تسعير
- **الورقة الهندسية**: عرض وعمق الخندق وكميات كل نشاط لكل متر وللإجمالي، والافتراضات التصميمية.
- **الفحوص**: الغطاء الأدنى، الحاجة للتدعيم (> 1.5 م)، الخنادق العميقة (> 4 م)، المياه الجوفية، الأنابيب المرنة، معقولية الإنتاجية.
- **تحليل باريتو**: البنود التي تشكل ~80% من القيمة — هي التي تستحق تدقيق الكميات وعروض أسعار متعددة.
- **الحساسية**: الأنبوب، الأسفلت، التدعيم، العمالة عادة الأعلى أثراً.
- **المدة مقابل الإنتاجية**: الطول ÷ (الإنتاجية الفعلية × عدد الفرق) يجب أن يتسق مع مدة العقد؛ إن لم يتسق فزِد الفرق (وتكلفتها في مصاريف الموقع) أو نبّه.
- **مؤشرات مرجعية**: سعر المتر الطولي الكلي لكل قطر/مادة، ونسبة الأنبوب من سعر المتر — قارنها بمشاريع الشركة السابقة.

## صيغة `pipelines`
```json
{"code": "W-01", "description": "...", "material": "HDPE|DI|GRP|UPVC", "dn_mm": 160, "od_m": 0.16,
 "length_m": 9500, "cover_m": 1.2, "surface": "asphalt|soil", "rock_ratio": 0.0, "ground_water": false,
 "import_backfill": false, "pipe_rate_per_m": 48, "fittings_allowance": 0.08,
 "lay_crew_daily_cost": 1450, "lay_equipment_daily_cost": 450, "lay_productivity_m_day": 220,
 "productivity_factors": [{"name": "حي مأهول", "factor": 0.75}]}
```
مفاتيح `rates`: `excavation_m3`, `rock_excavation_m3`, `bedding_m3`, `surround_m3`, `backfill_m3`, `disposal_m3`, `shoring_m2`, `asphalt_m2`, `dewatering_m`, `testing_m`, `tape_m` — كل منها `{"type": "...", "key": "...", "rate": ...}`.
الافتراضات التصميمية قابلة للتعديل في `design` (انظر `DEFAULT_DESIGN` في السكربت).
