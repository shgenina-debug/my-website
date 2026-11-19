import json
import unittest

from leads.gmaps import parse_page, build_url


def raw_place(title, phone, extra=None):
    p = [None] * 190
    p[4] = [None] * 9
    p[4][7], p[4][8] = 4.5, 85
    p[7] = ["/url?q=https://example.sa/&opi=1", "example.sa"]
    p[9] = [None, None, 21.4, 39.2]
    p[10] = "0x15c3c94d1f601755:0xd0e25af2e47f66af"
    p[11] = title
    p[13] = ["مصنع", "مورّد زجاجات المياه"]
    p[18] = title + "، المحجر، جدة 22423"
    p[34] = [None, None, None, None, [None, None, None, None, "مغلق · يفتح يوم السبت عند الساعة ٨ ص"]]
    p[78] = "ChIJVRdgH03JwxURr2Z_5PJa4tA"
    p[178] = [[phone, 1], ["+966 " + phone[1:], 2]]
    p[183] = [None, [None, None, None, "جدة", None, None, "SA"]]
    for k, v in (extra or {}).items():
        p[k] = v
    return p


class ParseTests(unittest.TestCase):
    def test_parse(self):
        items = [["header"], [None] * 14 + [raw_place("مصنع أنهار الري", "054 377 7051")],
                 [None] * 14 + [raw_place("مصنع مقفول", "055 000 0000", {33: ["مغلق نهائيًا"]})]]
        body = ")]}'\n" + json.dumps([["q", items]])
        places, raw = parse_page(body)
        self.assertEqual(raw, 2)
        a, b = places
        self.assertEqual(a["name"], "مصنع أنهار الري")
        self.assertEqual(a["phones"], ["054 377 7051", "+966 54 377 7051"])
        self.assertEqual(a["category"], "مصنع")
        self.assertEqual(a["address"], "المحجر، جدة 22423")
        self.assertEqual(a["city"], "جدة")
        self.assertEqual((a["rating"], a["reviews"]), (4.5, 85))
        self.assertEqual(a["website"], "https://example.sa/")
        self.assertEqual(a["maps_url"], "https://www.google.com/maps?cid=%d" % 0xd0e25af2e47f66af)
        self.assertFalse(a["closed"], "مغلق الآن (خارج ساعات العمل) مش معناه مقفول")
        self.assertTrue(b["closed"])

    def test_url_has_lang_country_offset(self):
        u = build_url("مصنع مياه جدة", 21.4858, 39.1925, 30000, 40)
        self.assertIn("hl=ar", u)
        self.assertIn("gl=sa", u)
        self.assertIn("%218i40", u)


if __name__ == "__main__":
    unittest.main()
