# فريق وكلاء المقاولات

هذا المستودع يضم فريق وكلاء متخصصين لشركة مقاولات سعودية: التسعير العام لكل أنواع المشاريع (إلكتروميكانيك، معماري، إنشائي، مباني، طرق، شبكات)، مع تخصص في مشاريع المياه والصرف الصحي (شركة المياه الوطنية وجهات القطاع).

## الوكلاء ومتى يُستخدم كل منهم
| الوكيل | المهمة |
|---|---|
| `tender-scout` | البحث عن المنافسات والفرص، تقييمها (Go/No-go)، تحديث سجل الفرص |
| `pricing-engineer` | التسعير الهندسي العام لأي نوع مشروع (إلكتروميكانيك، معماري، إنشائي، مبنى متكامل، شبكات مياه، طرق): تفكيك البنود، أسعار الموارد، باريتو، حساسية، فحوص حسب التخصص، ومنصة التسعير |
| `proposal-writer` | العرض الفني والعرض المالي ومصفوفة المطابقة وقائمة التحقق |
| `nwc-technical-responder` | الردود الفنية على استفسارات وملاحظات المالك والاستشاري، والاستفسارات قبل التقديم |

## سير العمل المعتاد لمنافسة
1. `tender-scout` يجد الفرصة ويقيّمها → قرار Go.
2. `proposal-writer` يفكك الكراسة (`00-tender-breakdown.md`) ويحدد الانحرافات.
3. `nwc-technical-responder` يصيغ الاستفسارات قبل موعد إغلاقها.
4. `pricing-engineer` يسعّر ويسلّم الأرقام والافتراضات.
5. `proposal-writer` يكتب العرض الفني والمالي بالأرقام المعتمدة ويمرر قائمة التحقق.
6. بعد الترسية: `nwc-technical-responder` للردود والاعتمادات طوال التنفيذ.

## قواعد مشتركة لكل الوكلاء
- اقرأ `.claude/company/profile.md` أولاً — هو المصدر الوحيد لبيانات الشركة.
- لا أرقام أو خبرات أو مراجع مخترعة؛ الناقص يُكتب `[[ مطلوب: ... ]]`.
- المرجع الحاكم هو وثائق المنافسة/العقد، ثم معايير شركة المياه الوطنية، ثم المواصفات الدولية.
- العربية افتراضياً، مع المصطلح الإنجليزي بين قوسين عند الحاجة.

## المجلدات
- `opportunities/` سجل الفرص • `proposals/<منافسة>/` العروض • `pricing/<مشروع>/` التسعير • `responses/` الردود الفنية.
- `pricing-platform/index.html` منصة التسعير العامة (تعمل بدون إنترنت، وتقرأ/تصدر نفس JSON الأدوات). المكتبة والأمثلة مضمّنة فيها بـ `build_platform.py` — لا تعدّل الجزء المضمّن يدوياً.

## الأدوات والاختبار السريع
```bash
E=.claude/skills/cost-estimating; P=.claude/skills/saudi-project-pricing/scripts/pricing_calc.py
python3 $E/scripts/build_project.py types
python3 $E/scripts/build_project.py build $E/examples/electromechanical_project.json --out /tmp/em.json && python3 $P /tmp/em.json
python3 $E/scripts/build_project.py build .claude/skills/water-pricing/examples/water_network_project.json --out /tmp/w.json && python3 $P /tmp/w.json
python3 $E/scripts/build_project.py import $E/examples/sample_boq.xlsx --type building_full --out /tmp/imp.json   # 12 من 13 بنداً بمطابقة
python3 $E/scripts/build_platform.py   # بعد أي تعديل على library.json أو الأمثلة
python3 .claude/skills/tender-scouting/scripts/score_opportunities.py .claude/skills/tender-scouting/templates/pipeline.csv
```
منطق الحساب في `pricing-platform/index.html` نسخة مطابقة من `build_project.py` + `water_assemblies.py` + `pricing_calc.py`، ومنطق استيراد Excel (اكتشاف الأعمدة والمطابقة) نسخة من `boq_import.py` — أي تعديل في أحدهما يُعكس في الآخر، ويجب أن يبقى مجموع الأمثلة متطابقاً قبل الضريبة: الإلكتروميكانيك 2,569,979.64 ر.س، والمياه 8,600,142.26 ر.س.
