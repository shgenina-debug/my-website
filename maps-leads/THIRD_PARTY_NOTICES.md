# إشعارات الطرف الثالث (Third-party notices)

طريقة سحب البيانات في `leads/gmaps.py` (طلب `/search?tbm=map&pb=...` ومواقع الحقول داخل
بيانات المكان مثل الاسم `[11]` والرقم `[178][0][0]` والتصنيف `[13]` والتقييم `[4][7]`)
مأخوذة بالهندسة العكسية من مشروع:

**gosom/google-maps-scraper** — https://github.com/gosom/google-maps-scraper
(الملفات `gmaps/searchjob.go` و`gmaps/multiple.go` و`gmaps/entry.go`)

لم يُنسخ كود Go نفسه؛ أُعيدت كتابة المنطق بلغة Python، مع إضافة التنقل بين صفحات النتائج.
احتراماً للرخصة، هذا نصها الكامل:

```
MIT License

Copyright (c) 2023 Georgios Komninos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
