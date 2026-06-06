import unittest
from datetime import date

from stock_system import StockSystem
from web_app import StockWebApp


class TestStockWebApp(unittest.TestCase):
    def test_get_state_returns_products_and_borrowers(self) -> None:
        app = StockWebApp()
        state = app.get_state()
        self.assertIn("products", state)
        self.assertIn("borrowers", state)
        self.assertIn("requisitions", state)
        self.assertGreater(len(state["products"]), 0)
        self.assertGreater(len(state["borrowers"]), 0)

    def test_borrow_and_return_actions_use_existing_stock_logic(self) -> None:
        system = StockSystem()
        system.add_product("P1", "TypeA", "pcs", "Gray", 5)
        system.add_borrower("Borrower A")
        app = StockWebApp(system)

        state_after_borrow = app.run_action(
            "borrow",
            {
                "borrower": "Borrower A",
                "customer": "Customer A",
                "project_or_location": "Site A",
                "purpose": "Demo",
                "requisition_date": date(2026, 6, 6).isoformat(),
                "items": {"P1": 2},
            },
        )
        self.assertEqual(system.products["P1"].quantity, 3)
        self.assertEqual(len(state_after_borrow["requisitions"]), 1)
        requisition_id = state_after_borrow["requisitions"][0]["requisition_id"]

        app.run_action(
            "return",
            {
                "requisition_id": requisition_id,
                "receiver_name": "Staff A",
            },
        )
        self.assertEqual(system.products["P1"].quantity, 5)
        self.assertTrue(system.requisitions[requisition_id].returned)

    def test_unknown_action_is_rejected(self) -> None:
        app = StockWebApp()
        with self.assertRaises(ValueError):
            app.run_action("no_such_action", {})


if __name__ == "__main__":
    unittest.main()
