import unittest

from inventory import reserve


class InventoryTests(unittest.TestCase):
    def test_valid_reservation_does_not_mutate_input(self):
        stock = {"pen": 5, "paper": 3}
        self.assertEqual(reserve(stock, {"pen": 2}), {"pen": 3, "paper": 3})
        self.assertEqual(stock, {"pen": 5, "paper": 3})

    def test_missing_sku_rejected_even_for_zero_quantity(self):
        with self.assertRaises(ValueError):
            reserve({"pen": 5}, {"pencil": 0})

    def test_negative_or_excessive_quantity_rejected(self):
        for quantity in (-1, 6):
            with self.subTest(quantity=quantity), self.assertRaises(ValueError):
                reserve({"pen": 5}, {"pen": quantity})


if __name__ == "__main__":
    unittest.main()
