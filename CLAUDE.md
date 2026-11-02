# فريق وكلاء مشاريع المياه

هذا المستودع يضم فريق وكلاء متخصصين لشركة مقاولات تعمل في مشاريع المياه والصرف الصحي في السعودية (شركة المياه الوطنية وجهات القطاع).

## الوكلاء ومتى يُستخدم كل منهم
| الوكيل | المهمة |
|---|---|
| `tender-scout` | البحث عن المنافسات والفرص، تقييمها (Go/No-go)، تحديث سجل الفرص |
| `water-pricing-engineer` | تسعير هندسي لمشاريع المياه: تفكيك البنود، تحليل الأسعار، باريتو، حساسية، اتساق المدة، ومنصة التسعير |
| `saudi-project-pricing` | تسعير عام لمشاريع المقاولات (مباني وغيرها) |
| `proposal-writer` | العرض الفني والعرض المالي ومصفوفة المطابقة وقائمة التحقق |
| `nwc-technical-responder` | الردود الفنية على استفسارات وملاحظات المالك والاستشاري، والاستفسارات قبل التقديم |

## سير العمل المعتاد لمنافسة
1. `tender-scout` يجد الفرصة ويقيّمها → قرار Go.
2. `proposal-writer` يفكك الكراسة (`00-tender-breakdown.md`) ويحدد الانحرافات.
3. `nwc-technical-responder` يصيغ الاستفسارات قبل موعد إغلاقها.
4. `water-pricing-engineer` يسعّر ويسلّم الأرقام والافتراضات.
5. `proposal-writer` يكتب العرض الفني والمالي بالأرقام المعتمدة ويمرر قائمة التحقق.
6. بعد الترسية: `nwc-technical-responder` للردود والاعتمادات طوال التنفيذ.

## قواعد مشتركة لكل الوكلاء
- اقرأ `.claude/company/profile.md` أولاً — هو المصدر الوحيد لبيانات الشركة.
- لا أرقام أو خبرات أو مراجع مخترعة؛ الناقص يُكتب `[[ مطلوب: ... ]]`.
- المرجع الحاكم هو وثائق المنافسة/العقد، ثم معايير شركة المياه الوطنية، ثم المواصفات الدولية.
- العربية افتراضياً، مع المصطلح الإنجليزي بين قوسين عند الحاجة.

## المجلدات
- `opportunities/` سجل الفرص • `proposals/<منافسة>/` العروض • `pricing/<مشروع>/` التسعير • `responses/` الردود الفنية.
- `pricing-platform/index.html` منصة التسعير التفاعلية (تعمل بدون إنترنت، وتقرأ/تصدر نفس JSON الأدوات).

## الأدوات والاختبار السريع
```bash
python3 .claude/skills/water-pricing/scripts/water_assemblies.py .claude/skills/water-pricing/examples/water_network_project.json --out /tmp/w.json
python3 .claude/skills/saudi-project-pricing/scripts/pricing_calc.py /tmp/w.json
python3 .claude/skills/tender-scouting/scripts/score_opportunities.py .claude/skills/tender-scouting/templates/pipeline.csv
```
منطق الحساب في `pricing-platform/index.html` نسخة مطابقة من السكربتين أعلاه — أي تعديل في أحدهما يُعكس في الآخر، ومجموع المثال يجب أن يبقى متطابقاً (8,600,142.26 ر.س قبل الضريبة).
