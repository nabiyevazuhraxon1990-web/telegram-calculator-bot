"""Xavfsiz va aqlli matematik kalkulyator dvigateli (Engine).

Ushbu modul Python AST (Abstract Syntax Tree) orqali ishlaydi.
eval() funksiyasidan foydalanilmaydi, bu esa to'liq xavfsizlikni kafolatlaydi
(hech qanday zararli kod yoki tizim buyruqlarini bajarib bo'lmaydi).
"""

import ast
import math
import operator
import re
from typing import Any, Dict, Optional, Tuple, Union


class SafeCalculator:
    """Xavfsiz matematik ifodalarni hisoblovchi sinf."""

    # Ruxsat etilgan ikkilik (binary) amallar
    SAFE_OPERATORS: Dict[type, Any] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    # Ruxsat etilgan birikmali (unary) amallar (+5, -5)
    SAFE_UNARY_OPERATORS: Dict[type, Any] = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    # Ruxsat etilgan matematik funksiyalar
    SAFE_FUNCTIONS: Dict[str, Any] = {
        "sqrt": math.sqrt,
        "cbrt": math.cbrt,
        "sin": lambda x: math.sin(math.radians(x)),
        "cos": lambda x: math.cos(math.radians(x)),
        "tan": lambda x: math.tan(math.radians(x)),
        "asin": lambda x: math.degrees(math.asin(x)),
        "acos": lambda x: math.degrees(math.acos(x)),
        "atan": lambda x: math.degrees(math.atan(x)),
        "log": math.log,
        "log10": math.log10,
        "log2": math.log2,
        "exp": math.exp,
        "abs": abs,
        "round": round,
        "ceil": math.ceil,
        "floor": math.floor,
        "factorial": lambda n: SafeCalculator._safe_factorial(n),
        "fact": lambda n: SafeCalculator._safe_factorial(n),
        "rad": math.radians,
        "deg": math.degrees,
    }

    # Ruxsat etilgan matematik doimiylar (konstantalar)
    SAFE_CONSTANTS: Dict[str, float] = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
    }

    @staticmethod
    def _safe_factorial(n: Union[int, float]) -> int:
        """Xavfsiz faktorial hisoblash (haddan tashqari katta sonlardan himoyalangan)."""
        if not float(n).is_integer():
            raise ValueError("Faktorial faqat butun sonlar uchun aniqlangan!")
        n_int = int(n)
        if n_int < 0:
            raise ValueError("Manfiy sonning faktoriali mavjud emas!")
        if n_int > 100:
            raise ValueError("Faktorial chegarasi: 100 dan oshmasligi kerak!")
        return math.factorial(n_int)

    @classmethod
    def _eval_node(cls, node: ast.AST) -> Union[int, float]:
        """AST daraxti tugunlarini xavfsiz rekursiv baholash."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise TypeError("Faqat sonli qiymatlar qabul qilinadi!")

        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in cls.SAFE_OPERATORS:
                raise ValueError(f"Ruxsat etilmagan amal: {op_type.__name__}")

            left = cls._eval_node(node.left)
            right = cls._eval_node(node.right)

            # 0 ga bo'lishni oldini olish
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                raise ZeroDivisionError("Nolga bo'lish mumkin emas!")

            # Haddan tashqari katta darajani oldini olish (DoS himoyasi)
            if op_type == ast.Pow:
                if abs(right) > 500:
                    raise ValueError("Daraja juda katta (chegara: 500)!")
                if abs(left) > 10000 and right > 10:
                    raise ValueError("Natija hisoblash chegarasidan oshib ketadi!")

            try:
                res = cls.SAFE_OPERATORS[op_type](left, right)
                # Kompleks son chiqib ketsa
                if isinstance(res, complex):
                    raise ValueError("Haqiqiy sonlar to'plamida hisoblab bo'lmadi!")
                return res
            except OverflowError:
                raise ValueError("Natija juda katta bo'lib ketdi (Overflow)!")

        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in cls.SAFE_UNARY_OPERATORS:
                raise ValueError("Ruxsat etilmagan belgi!")
            operand = cls._eval_node(node.operand)
            return cls.SAFE_UNARY_OPERATORS[op_type](operand)

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Noto'g'ri funksiya chaqiruvi!")
            func_name = node.func.id.lower()
            if func_name not in cls.SAFE_FUNCTIONS:
                raise ValueError(f"Noma'lum funksiya: '{func_name}'")

            args = [cls._eval_node(arg) for arg in node.args]
            try:
                res = cls.SAFE_FUNCTIONS[func_name](*args)
                return res
            except ZeroDivisionError:
                raise ZeroDivisionError("Nolga bo'lish mumkin emas!")
            except ValueError as ve:
                raise ValueError(f"Matematik xato: {ve}")
            except Exception as ex:
                raise ValueError(f"Funksiyani hisoblashda xato: {ex}")

        elif isinstance(node, ast.Name):
            name = node.id.lower()
            if name in cls.SAFE_CONSTANTS:
                return cls.SAFE_CONSTANTS[name]
            raise ValueError(f"Noma'lum o'zgaruvchi: '{name}'")

        else:
            raise ValueError("Qo'llab-quvvatlanmaydigan ifoda tuzilmasi!")

    @classmethod
    def preprocess_expression(cls, raw: str) -> str:
        """Foydalanuvchi kiritgan matnni tozalash va standartlashtirish."""
        expr = raw.strip()

        # O'zbekcha / vizual belgilarni almashtirish
        expr = expr.replace("×", "*").replace("✕", "*").replace("·", "*")
        expr = expr.replace("÷", "/").replace(":", "/")
        expr = expr.replace("−", "-").replace("—", "-").replace("–", "-")
        expr = expr.replace("²", "^2").replace("³", "^3")

        # So'z ko'rinishidagi yozuvlar
        expr = re.sub(r"\bildiz\b", "sqrt", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bfaktorial\b", "factorial", expr, flags=re.IGNORECASE)

        # Raqamlar orasidagi bo'shliqlarni olib tashlash: "1 000 000" -> "1000000"
        expr = re.sub(r"(?<=\d)\s+(?=\d)", "", expr)

        # O'nlik kasr vergulini nuqtaga aylantirish: "3,14" -> "3.14"
        expr = re.sub(r"(?<=\d),(?=\d)", ".", expr)

        # Ildiz belgisini almashtirish: "√64" -> "sqrt(64)", "√(25+5)" -> "sqrt(25+5)"
        expr = re.sub(r"√\s*\(([^)]+)\)", r"sqrt(\1)", expr)
        expr = re.sub(r"√\s*([0-9.]+)", r"sqrt(\1)", expr)

        # Faktorial: "5!" -> "factorial(5)"
        expr = re.sub(r"([0-9.]+)\s*!", r"factorial(\1)", expr)

        # Foizlarni hisoblash qoidalari (agar % dan keyin raqam kelmasa, ya'ni qoldiqli bo'lish emas, foiz bo'lsa):
        # 1) A + B%  ->  A + (A * B / 100)
        # 2) A - B%  ->  A - (A * B / 100)
        expr = re.sub(
            r"([0-9.]+)\s*([\+\-])\s*([0-9.]+)\s*%(?!\s*\d)",
            r"\1 \2 (\1 * \3 / 100)",
            expr,
        )
        # 3) A * B%  ->  A * (B / 100), A / B% -> A / (B / 100)
        expr = re.sub(
            r"([\*\/])\s*([0-9.]+)\s*%(?!\s*\d)",
            r"\1 (\2 / 100)",
            expr,
        )
        # 4) Oddiy B% -> (B / 100)
        expr = re.sub(
            r"([0-9.]+)\s*%(?!\s*\d)",
            r"(\1 / 100)",
            expr,
        )

        # Daraja belgisini Python standartiga o'tkazish: 2^3 -> 2**3
        expr = expr.replace("^", "**")

        # Yashirin ko'paytirishlarni to'ldirish:
        # "2(3+4)" -> "2*(3+4)", "(3+4)2" -> "(3+4)*2", "(1+2)(3+4)" -> "(1+2)*(3+4)"
        expr = re.sub(r"\b(\d+)\s*\(", r"\1 * (", expr)
        expr = re.sub(r"\)\s*(\d+)\b", r") * \1", expr)
        expr = re.sub(r"\)\s*\(", r") * (", expr)

        # "2pi" -> "2*pi", "5sqrt(4)" -> "5*sqrt(4)"
        expr = re.sub(
            r"\b(\d+)\s*(sqrt|cbrt|sin|cos|tan|asin|acos|atan|log10|log2|log|exp|abs|pi|e|tau)\b",
            r"\1 * \2",
            expr,
        )
        expr = re.sub(
            r"\)\s*(sqrt|cbrt|sin|cos|tan|asin|acos|atan|log10|log2|log|exp|abs|pi|e|tau)\b",
            r") * \1",
            expr,
        )

        return expr

    @classmethod
    def format_result(cls, val: Union[int, float]) -> str:
        """Natijani chiroyli va o'qilishi oson formatda ko'rsatish."""
        if isinstance(val, (int, float)):
            # Agar butun son bo'lsa yoki kasr qismi 0 bo'lsa
            if float(val).is_integer():
                int_val = int(val)
                # Katta sonlar uchun minglik ajratgich bilan ko'rsatish
                if abs(int_val) >= 10000:
                    formatted_grouped = f"{int_val:_}".replace("_", " ")
                    return f"{int_val} ({formatted_grouped})"
                return str(int_val)

            # Float sonlar: juda katta yoki juda kichik bo'lsa
            if abs(val) > 1e14 or (abs(val) < 1e-6 and val != 0):
                return f"{val:.6e}"

            # Oddiy o'nlik kasr
            rounded = round(val, 8)
            str_val = f"{rounded:.8f}".rstrip("0").rstrip(".")
            return str_val

        return str(val)

    @classmethod
    def calculate(cls, raw_expr: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Ifodani hisoblaydi.
        Qaytaradi: (formatlangan_natija, xatolik_matni)
        Muvaffaqiyatli bo'lsa, xatolik_matni None bo'ladi.
        """
        if not raw_expr or not raw_expr.strip():
            return None, "Ifoda kiritilmadi!"

        try:
            cleaned = cls.preprocess_expression(raw_expr)
            parsed = ast.parse(cleaned, mode="eval")
            result_val = cls._eval_node(parsed.body)
            formatted = cls.format_result(result_val)
            return formatted, None

        except ZeroDivisionError:
            return None, "0 ga bo'lish mumkin emas!"
        except OverflowError:
            return None, "Son juda katta bo'lib ketdi!"
        except (SyntaxError, ValueError, TypeError) as e:
            msg = str(e)
            if "invalid syntax" in msg.lower() or "unexpected EOF" in msg.lower():
                return None, "Ifoda sintaksisida xatolik bor (qavslar yoki belgilarni tekshiring)!"
            return None, msg
        except Exception as e:
            return None, f"Hisoblashda xatolik yuz berdi: {str(e)}"
