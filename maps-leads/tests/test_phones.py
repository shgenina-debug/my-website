import unittest
from leads.phones import normalize, extract_mobiles, wa_link, MOBILE, LANDLINE, UNIFIED, TOLLFREE


class PhoneTests(unittest.TestCase):
    def test_normalize(self):
        cases = {
            "054 567 1704": ("0545671704", MOBILE),
            "+966 54 567 1704": ("0545671704", MOBILE),
            "00966545671704": ("0545671704", MOBILE),
            "966545671704": ("0545671704", MOBILE),
            "545671704": ("0545671704", MOBILE),
            "٠٥٥٧٧١٧١٨٠": ("0557717180", MOBILE),
            "012 612 3456": ("0126123456", LANDLINE),
            "+966 11 465 0000": ("0114650000", LANDLINE),
            "12345": ("12345", "غير معروف"),
            "9200 66669": ("920066669", UNIFIED),
            "+966 9200 66669": ("920066669", UNIFIED),
            "800 124 4444": ("8001244444", TOLLFREE),
        }
        for raw, want in cases.items():
            self.assertEqual(normalize(raw), want, raw)

    def test_wa(self):
        self.assertEqual(wa_link("0557717180"), "https://wa.me/966557717180")

    def test_extract_whatsapp_export(self):
        txt = (
            "19/11/2026, 10:15 - +966 55 123 4567: 🌷 مصنع مياه رذاذ للمياه . ابو بدر مدير . سدير\n"
            "0557717180\n"
            "19/11/2026, 10:16 - أحمد: 056-111-2233 و ‎+966 50 000 1111‎ و ٠٥٤٥٦٧١٧٠٤\n"
            "رقم أرضي 0126123456 مش جوال، وتاريخ 2026 وسعر 5000000\n"
            "0557717180 مكرر\n"
        )
        self.assertEqual(
            extract_mobiles(txt),
            ["0551234567", "0557717180", "0561112233", "0500001111", "0545671704"],
        )


if __name__ == "__main__":
    unittest.main()
