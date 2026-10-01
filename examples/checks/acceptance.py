"""Independent acceptance cases. Run from a task's temporary repository copy."""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path.cwd()))


def subject(module: str, function: str):
    return getattr(importlib.import_module(module), function)


class CalculatorAcceptance(unittest.TestCase):
    def test_zero_and_negative_numbers(self):
        add = subject("calculator", "add")
        self.assertEqual(add(0, 7), 7)
        self.assertEqual(add(-4, -6), -10)


class SlugifyAcceptance(unittest.TestCase):
    def test_mixed_case_and_spaces(self):
        slugify = subject("slug", "slugify")
        self.assertEqual(slugify("MiXeD  Case"), "mixed-case")
        self.assertEqual(slugify("Already"), "already")


class ConfigAcceptance(unittest.TestCase):
    def test_first_separator_and_whitespace(self):
        parse_line = subject("config", "parse_line")
        self.assertEqual(parse_line(" KEY = a=b=c "), ("KEY", "a=b=c"))
        self.assertEqual(parse_line("EMPTY="), ("EMPTY", ""))


class PaginationAcceptance(unittest.TestCase):
    def test_single_item_pages(self):
        page = subject("pagination", "page")
        self.assertEqual(page(["a", "b", "c"], 1, 1), ["a"])
        self.assertEqual(page(["a", "b", "c"], 3, 1), ["c"])
        self.assertEqual(page(["a", "b", "c"], 4, 1), [])


class RetryAcceptance(unittest.TestCase):
    def test_one_attempt_failure_is_raised(self):
        retry = subject("retry", "retry")
        calls = []

        def fail():
            calls.append(1)
            raise LookupError("last error")

        with self.assertRaisesRegex(LookupError, "last error"):
            retry(fail, 1)
        self.assertEqual(len(calls), 1)

    def test_stops_after_success(self):
        retry = subject("retry", "retry")
        calls = []

        def succeed():
            calls.append(1)
            return "done"

        self.assertEqual(retry(succeed, 4), "done")
        self.assertEqual(len(calls), 1)


class DedupeAcceptance(unittest.TestCase):
    def test_case_sensitive_first_seen_order(self):
        unique_in_order = subject("dedupe", "unique_in_order")
        self.assertEqual(unique_in_order(["B", "a", "B", "A", "a"]), ["B", "a", "A"])


class MedianAcceptance(unittest.TestCase):
    def test_negative_even_length_and_singleton(self):
        median = subject("median", "median")
        self.assertEqual(median([-7, -3, -1, 9]), -2)
        self.assertEqual(median([4]), 4)


class QueryAcceptance(unittest.TestCase):
    def test_encodes_unicode_key_space_and_percent(self):
        build_query = subject("query", "build_query")
        self.assertEqual(build_query({"城市": "New York", "rate%": "50%"}),
                         "%E5%9F%8E%E5%B8%82=New+York&rate%25=50%25")


class InventoryAcceptance(unittest.TestCase):
    def test_unknown_zero_quantity_is_rejected(self):
        reserve = subject("inventory", "reserve")
        stock = {"pen": 2}
        with self.assertRaises(ValueError):
            reserve(stock, {"missing": 0})
        self.assertEqual(stock, {"pen": 2})

    def test_empty_request_returns_copy(self):
        reserve = subject("inventory", "reserve")
        stock = {"pen": 2}
        result = reserve(stock, {})
        self.assertEqual(result, stock)
        self.assertIsNot(result, stock)


class FilenameAcceptance(unittest.TestCase):
    def test_final_suffix_and_dotfile(self):
        extension = subject("filename", "extension")
        self.assertEqual(extension("archive.tar.GZ"), "gz")
        self.assertEqual(extension(".profile"), "")
        self.assertEqual(extension("name."), "")


CASES = {
    "calculator-add": CalculatorAcceptance,
    "slugify-normalization": SlugifyAcceptance,
    "config-value-equals": ConfigAcceptance,
    "pagination-one-based": PaginationAcceptance,
    "retry-attempt-budget": RetryAcceptance,
    "dedupe-stable-order": DedupeAcceptance,
    "median-even-length": MedianAcceptance,
    "query-encoding": QueryAcceptance,
    "inventory-unknown-sku": InventoryAcceptance,
    "filename-final-extension": FilenameAcceptance,
}


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in CASES:
        raise SystemExit("Usage: acceptance.py TASK_ID")
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CASES[sys.argv[1]]))
    raise SystemExit(0 if result.wasSuccessful() else 1)
