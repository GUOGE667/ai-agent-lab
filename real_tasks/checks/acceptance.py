"""Acceptance checks outside each copied historical source tree."""

from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path.cwd()))


class EnumerateStartAcceptance(unittest.TestCase):
    def test_negative_start_with_generator(self):
        from tqdm.contrib import tenumerate

        values = (item for item in ("x", "y"))
        self.assertEqual(list(tenumerate(values, start=-2, disable=True)),
                         [(-2, "x"), (-1, "y")])


class AnsiTrimAcceptance(unittest.TestCase):
    def test_existing_reset_is_not_repeated(self):
        from tqdm.utils import disp_trim

        escape = "\x1b"
        source = f"*****{escape}[22m*****{escape}[0m**"
        self.assertEqual(disp_trim(source, 10), f"*****{escape}[22m*****{escape}[0m")


class GeneratorBoolAcceptance(unittest.TestCase):
    def test_truth_check_does_not_consume_generator(self):
        from tqdm import tqdm

        values = (item for item in (1, 2))
        progress = tqdm(values, file=io.StringIO())
        try:
            self.assertTrue(bool(progress))
            self.assertEqual(next(values), 1)
        finally:
            progress.close()

    def test_known_totals(self):
        from tqdm import tqdm

        empty = tqdm(total=0, file=io.StringIO())
        nonempty = tqdm(total=2, file=io.StringIO())
        try:
            self.assertFalse(bool(empty))
            self.assertTrue(bool(nonempty))
        finally:
            empty.close()
            nonempty.close()


class ScaleWithoutTotalAcceptance(unittest.TestCase):
    def test_fractional_scale_without_total(self):
        from tqdm import tqdm

        rendered = tqdm.format_meter(3, None, 2, unit_scale=2.5)
        self.assertTrue(rendered.startswith("7.5it"), rendered)

    def test_known_total_still_scaled(self):
        from tqdm import tqdm

        rendered = tqdm.format_meter(2, 4, 1, unit_scale=2)
        self.assertIn("4/8", rendered)


class DisabledBoolAcceptance(unittest.TestCase):
    def test_zero_total_is_false(self):
        from tqdm import tqdm

        self.assertFalse(bool(tqdm(total=0, disable=True)))


class DisabledIteratorAcceptance(unittest.TestCase):
    def test_generator_can_be_consumed(self):
        from tqdm import tqdm

        values = (item for item in ("a", "b"))
        self.assertEqual(list(tqdm(values, disable=True)), ["a", "b"])


class OptionBoundaryAcceptance(unittest.TestCase):
    def test_embedded_dashes_do_not_create_options(self):
        from tqdm._main import RE_SHLEX

        self.assertEqual(RE_SHLEX.findall("prefix--fake --desc demo"), ["desc"])


class CustomBarFormatAcceptance(unittest.TestCase):
    def test_user_segments_around_bar(self):
        from tqdm import tqdm

        rendered = tqdm.format_meter(2, 4, 1, ncols=20, bar_format="LEFT{bar}RIGHT")
        self.assertTrue(rendered.startswith("LEFT"), rendered)
        self.assertTrue(rendered.endswith("RIGHT"), rendered)


class SiBoundaryAcceptance(unittest.TestCase):
    def test_rounding_at_smaller_thresholds(self):
        from tqdm._tqdm import format_sizeof

        self.assertEqual(format_sizeof(9.999), "10.0")
        self.assertEqual(format_sizeof(99.99), "100")


CASES = {
    "tqdm-1-enumerate-start": EnumerateStartAcceptance,
    "tqdm-2-ansi-trim": AnsiTrimAcceptance,
    "tqdm-3-generator-bool": GeneratorBoolAcceptance,
    "tqdm-4-scale-no-total": ScaleWithoutTotalAcceptance,
    "tqdm-5-disabled-bool": DisabledBoolAcceptance,
    "tqdm-6-disabled-iterator": DisabledIteratorAcceptance,
    "tqdm-7-option-boundary": OptionBoundaryAcceptance,
    "tqdm-8-custom-bar-format": CustomBarFormatAcceptance,
    "tqdm-9-si-boundary": SiBoundaryAcceptance,
}


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in CASES:
        raise SystemExit("Usage: acceptance.py TASK_ID")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CASES[sys.argv[1]])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
