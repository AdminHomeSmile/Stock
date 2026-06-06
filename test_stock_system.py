from datetime import date
import unittest

from stock_system import create_default_stock_system


class TestStockSystem(unittest.TestCase):
    def test_default_stock_is_initialized(self) -> None:
        system = create_default_stock_system()
        self.assertEqual(system.products["Sealant MS 541"].quantity, 20)
        self.assertEqual(system.products["Sealant SN 221"].quantity, 120)
        self.assertEqual(system.products["Sealant SA 271"].quantity, 120)
        self.assertEqual(system.products["sealant AC 181"].quantity, 20)

    def test_requisition_deducts_stock(self) -> None:
        system = create_default_stock_system()
        req = system.requisition_sample(
            borrower="Thisalinee Bunlert",
            customer="ABC Co., Ltd.",
            project_or_location="Sample Project",
            purpose="Demo",
            requisition_date=date(2026, 6, 6),
            items={"Sealant MS 541": 2, "Sealant SN 221": 3},
        )
        self.assertEqual(req.requisition_id, 1)
        self.assertEqual(system.products["Sealant MS 541"].quantity, 18)
        self.assertEqual(system.products["Sealant SN 221"].quantity, 117)

    def test_requisition_rejects_unlisted_borrower(self) -> None:
        system = create_default_stock_system()
        with self.assertRaises(ValueError):
            system.requisition_sample(
                borrower="Unknown User",
                customer="ABC Co., Ltd.",
                project_or_location="Sample Project",
                purpose="Demo",
                requisition_date=date(2026, 6, 6),
                items={"Sealant MS 541": 1},
            )

    def test_return_restores_stock_and_requires_receiver(self) -> None:
        system = create_default_stock_system()
        req = system.requisition_sample(
            borrower="Thisalinee Bunlert",
            customer="ABC Co., Ltd.",
            project_or_location="Sample Project",
            purpose="Demo",
            requisition_date=date(2026, 6, 6),
            items={"Sealant MS 541": 1},
        )
        with self.assertRaises(ValueError):
            system.return_items(req.requisition_id, " ")
        system.return_items(req.requisition_id, "Staff A")
        self.assertTrue(system.requisitions[req.requisition_id].returned)
        self.assertEqual(system.requisitions[req.requisition_id].receiver_name, "Staff A")
        self.assertEqual(system.products["Sealant MS 541"].quantity, 20)

    def test_return_rejects_unknown_requisition_id(self) -> None:
        system = create_default_stock_system()
        with self.assertRaises(ValueError):
            system.return_items(999, "Staff A")

    def test_can_add_new_product_and_borrower(self) -> None:
        system = create_default_stock_system()
        system.add_product("Sealant X 999", "Sealant", "หลอด", "Gray", 10)
        system.add_borrower("New Borrower")
        system.requisition_sample(
            borrower="New Borrower",
            customer="XYZ Co., Ltd.",
            project_or_location="Plant 2",
            purpose="Trial",
            requisition_date=date(2026, 6, 6),
            items={"Sealant X 999": 4},
        )
        self.assertEqual(system.products["Sealant X 999"].quantity, 6)


if __name__ == "__main__":
    unittest.main()
