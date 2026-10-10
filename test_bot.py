"""Kalkulyator dvigateli va mantiqini tekshirish uchun testlar."""

import unittest
from calculator import SafeCalculator


class TestSafeCalculator(unittest.TestCase):
    def test_basic_arithmetic(self):
        self.assertEqual(SafeCalculator.calculate("2 + 2")[0], "4")
        self.assertEqual(SafeCalculator.calculate("10 - 3")[0], "7")
        self.assertEqual(SafeCalculator.calculate("6 * 7")[0], "42")
        self.assertEqual(SafeCalculator.calculate("100 / 4")[0], "25")
        self.assertEqual(SafeCalculator.calculate("17 // 3")[0], "5")
        self.assertEqual(SafeCalculator.calculate("17 % 5")[0], "2")

    def test_precedence_and_parentheses(self):
        self.assertEqual(SafeCalculator.calculate("2 + 3 * 4")[0], "14")
        self.assertEqual(SafeCalculator.calculate("(2 + 3) * 4")[0], "20")
        self.assertEqual(SafeCalculator.calculate("2 * (3 + 4 * 2)")[0], "22")

    def test_percentage(self):
        self.assertEqual(SafeCalculator.calculate("100 + 15%")[0], "115")
        self.assertEqual(SafeCalculator.calculate("200 - 20%")[0], "160")
        self.assertEqual(SafeCalculator.calculate("500 * 10%")[0], "50")
        self.assertEqual(SafeCalculator.calculate("25%")[0], "0.25")

    def test_scientific_functions(self):
        self.assertEqual(SafeCalculator.calculate("sqrt(144)")[0], "12")
        self.assertEqual(SafeCalculator.calculate("√144")[0], "12")
        self.assertEqual(SafeCalculator.calculate("2^10")[0], "1024")
        self.assertEqual(SafeCalculator.calculate("5!")[0], "120")
        self.assertEqual(SafeCalculator.calculate("factorial(5)")[0], "120")
        self.assertEqual(SafeCalculator.calculate("sin(90)")[0], "1")
        self.assertEqual(SafeCalculator.calculate("cos(0)")[0], "1")
        self.assertEqual(SafeCalculator.calculate("log10(1000)")[0], "3")
        self.assertEqual(SafeCalculator.calculate("log2(8)")[0], "3")
        self.assertEqual(SafeCalculator.calculate("abs(-42)")[0], "42")

    def test_formatting_and_normalization(self):
        res, _ = SafeCalculator.calculate("1 000 000 + 500 000")
        self.assertIn("1500000", res)
        self.assertEqual(SafeCalculator.calculate("3,5 * 2")[0], "7")
        self.assertEqual(SafeCalculator.calculate("2(3 + 4)")[0], "14")
        self.assertEqual(SafeCalculator.calculate("(2 + 3)(4 + 1)")[0], "25")

    def test_safety_and_errors(self):
        # 0 ga bo'lish
        _, err = SafeCalculator.calculate("10 / 0")
        self.assertIn("0 ga bo'lish", err)

        # Xavfli kod chaqiruvlari bloklanishi kerak
        _, err = SafeCalculator.calculate("__import__('os').system('ls')")
        self.assertIsNotNone(err)

        _, err = SafeCalculator.calculate("open('/etc/passwd')")
        self.assertIsNotNone(err)

        # Manfiy son faktoriali
        _, err = SafeCalculator.calculate("factorial(-5)")
        self.assertIsNotNone(err)

        # Juda katta daraja (DoS himoyasi)
        _, err = SafeCalculator.calculate("9^999999")
        self.assertIsNotNone(err)

    def test_ui_and_keyboards(self):
        import keyboards
        from handlers import render_display

        # Standart klaviatura mavjudligi
        std_kb = keyboards.get_calc_inline_keyboard("std")
        self.assertGreater(len(std_kb.inline_keyboard), 0)

        # Ilmiy klaviatura mavjudligi
        sci_kb = keyboards.get_calc_inline_keyboard("sci")
        self.assertGreater(len(sci_kb.inline_keyboard), 0)

        # Reply klaviatura
        reply_kb = keyboards.get_main_reply_keyboard()
        self.assertGreater(len(reply_kb.keyboard), 0)

        # Display render
        session = {"expr": "125 + 75", "last_result": "200", "just_evaluated": True, "mode": "std"}
        rendered = render_display(session)
        self.assertIn("125 + 75", rendered)
        self.assertIn("= 200", rendered)

    def test_webapp_integration(self):
        import json
        from handlers import add_to_history, user_histories

        payload = json.dumps({"expression": "25 * 4", "result": "100"})
        data = json.loads(payload)
        self.assertEqual(data["expression"], "25 * 4")
        self.assertEqual(data["result"], "100")

        # Test history addition from webapp
        add_to_history(99999, data["expression"], data["result"])
        self.assertIn(99999, user_histories)
        self.assertEqual(user_histories[99999][0]["result"], "100")


if __name__ == "__main__":
    unittest.main()
