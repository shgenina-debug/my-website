# my-website — فهرس الوكلاء والمشاريع

هذا المستودع يجمع وكلاء Claude ومهاراته، وملفات المشاريع. المستندات المنشورة (Artifacts) مفهرسة هنا بروابطها.

## 1. الوكلاء والمهارات

| التصنيف | الاسم | النوع | المكان | الاستخدام |
|---|---|---|---|---|
| التسعير والمناقصات | saudi-project-pricing | وكيل | `.claude/agents/saudi-project-pricing.md` | تسعير مشاريع المقاولات في السعودية وإعداد العروض المالية |
| التسعير والمناقصات | saudi-project-pricing | مهارة | `.claude/skills/saudi-project-pricing/` | المنهجية والمراجع النظامية وقوائم التحقق والحاسبة `pricing_calc.py` |
| الهندسة العكسية | reverse-engineer-anything | مهارة | `.claude/skills/reverse-engineer-anything/` | تحليل التطبيقات والملفات التنفيذية عبر خادم REA |
| الهندسة العكسية | rea | خادم MCP | `.mcp.json` | أدوات REA التي تعتمد عليها المهارة |
| تصميم الواجهات | frontend-design | مهارة | فرع `claude/frontend-design-skill-yf3pk9` (غير مدمج) | توجيه التصميم البصري للمواقع والواجهات |

طريقة الاستخدام في Claude Code: «استخدم وكيل saudi-project-pricing لتسعير …». المهارات تُستدعى تلقائياً حسب الطلب.

## 2. المشاريع

### أ. مناقصات وعروض فنية ومالية

| المشروع | الجهة | المستندات | الملفات في المستودع |
|---|---|---|---|
| فرع خدمة العملاء المتنقل | شركة المياه الوطنية | 8 مستندات — انظر [فهرس المشروع](projects/nwc-mobile-branch/README.md) | `projects/nwc-mobile-branch/` |
| نظام خفض الضغط لوحدات الجمع التلقائي | — | [العرض الفني (Autosampler)](https://claude.ai/artifact/ViYmYYEZGAcTViFc2VLuuT) | — |
| الحل البديل للخزانات أحادية الجدار | — | [الحل البديل](https://claude.ai/artifact/3v6KWGc4tt4bQJuHFKdLgD) | — |
| توزيع غازات أجهزة GC/IC/ICP | — | [GC IC ICP Gas Distribution](https://claude.ai/artifact/MsDd1y7ENAWFRWMW1KUHuq) | — |
| معالجة ملاحظات تأهيل السلامة (42974) | شركة الهيدروجين الأخضر التجارية | [المعالجة](https://claude.ai/artifact/9ZZBH6EkfESZSWQt8iybVD) | — |

### ب. السلامة والصحة المهنية

- [الهيكل التنظيمي للسلامة](https://claude.ai/artifact/DpxwaaxMgoswwLSqwAokYF)
- [منظومة السلامة والصحة المهنية – نماذج المنشأة](https://claude.ai/artifact/DY8b9qS4TXBgS5KD4oNE4f)

### ج. الأدلة الفنية والتدريب

- [دليل أفضل الممارسات — كهرباء وتيار خفيف وBMS (السعودية)](https://claude.ai/artifact/SDtFsE66qgHgALDFCnwPiD)
- [Chromatography Maintenance Engineer – Beginner Training Manual](https://claude.ai/artifact/EXeFvYbtq7uB3KHKUokKXW)

### د. الهوية والتسويق (حسب الجهة)

| الجهة | المستندات |
|---|---|
| ORITEC / ORITECH | [ORITECH Brand Identity](https://claude.ai/artifact/Ghg68EFCLu8BLEeDS5qWBZ) · [ORITEC](https://claude.ai/artifact/CBEZJFUKWDVC8VTRawpkKw) · [ORITECH Intro — AI Video Prompt Pack](https://claude.ai/artifact/N8hmvNY9tosLnhDJrzDHw2) · [oritech sh₂mg](https://claude.ai/artifact/UtFBKRT4dKAHsR2C6SszHS) · كود الموقع في فرع `claude/frontend-design-skill-yf3pk9` |
| مجموعة إنفايرون | [البروفايل](https://claude.ai/artifact/GoBUJEVR4AEpdjAnzqMzLu) · [البروشور](https://claude.ai/artifact/XsvZfWLuwwVFqatDynQgmR) |
| قناة حفريات | [الهوية](https://claude.ai/artifact/8Y7X1d2RaPQudkD5Kg5WDs) · [دليل الإنتاج من الصفر](https://claude.ai/artifact/7JfozhpJ1PqJFsmcrq9bTT) · [كورس BMS من الصفر للاحتراف](https://claude.ai/artifact/WQPxvzsYcX6tn3cCsjXKse) |
| منتجات | [OH85N-S Outdoor Display Brochure](https://claude.ai/artifact/GaaMnXK7n4dLavq1kchhuf) |

### هـ. تطبيقات ومواقع

- [Deal Desk CRM](https://claude.ai/artifact/DocoJpjzt8ZW2yXHCUqYkC)
- [Business Website](https://claude.ai/artifact/7W8F4pWTa67ubTq4XavBjE)
- [رفيق](https://claude.ai/artifact/3eLvYVSrMkDZaQzdVpmSS5)
- [Coach Pulse](https://claude.ai/artifact/3p2PQicgvvT9pHEfUZibvJ)

### و. شخصي

- [خطة التضخيم النظيف](https://claude.ai/artifact/Auk38KqyhqZCqNCd7gYLiV)

## 3. هيكل المستودع

```
.claude/
  agents/                     الوكلاء (Claude Code يقرأها من هنا)
  skills/                     المهارات (مجلد لكل مهارة)
projects/
  nwc-mobile-branch/          فرع خدمة العملاء المتنقل — المستندات والتسعير
.mcp.json                     خوادم MCP
```

الوكلاء والمهارات يجب أن تبقى في `.claude/` ليتعرف عليها Claude Code، لذلك تصنيفها في الجدول أعلاه لا في المجلدات. كل مشروع جديد له ملفات يُضاف في `projects/<اسم-المشروع>/` مع `README.md` يفهرس مستنداته.

## 4. الفروع

| الفرع | المحتوى | الحالة |
|---|---|---|
| `main` | الوكلاء والمهارات المدمجة | أساسي |
| `claude/frontend-design-skill-yf3pk9` | مهارة frontend-design + موقع ORITEC | غير مدمج |
