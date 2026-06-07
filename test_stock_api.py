import unittest

from api import index as api_module
from stock_system import create_default_stock_system


class TestStockApi(unittest.TestCase):
    def setUp(self) -> None:
        api_module.system = create_default_stock_system()
        self.client = api_module.app.test_client()

    def test_list_products_returns_default_items(self) -> None:
        response = self.client.get("/products")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 4)
        self.assertTrue(any(product["name"] == "Sealant MS 541" for product in data))

    def test_add_borrower_borrow_return_and_list_requisitions(self) -> None:
        borrower_response = self.client.post("/borrowers", json={"borrower_name": "API Borrower"})
        self.assertEqual(borrower_response.status_code, 201)

        add_product_response = self.client.post(
            "/products",
            json={
                "name": "Sealant X 999",
                "product_type": "Sealant",
                "unit": "หลอด",
                "color": "Gray",
                "quantity": 10,
            },
        )
        self.assertEqual(add_product_response.status_code, 201)

        requisition_response = self.client.post(
            "/requisitions",
            json={
                "borrower": "API Borrower",
                "customer": "XYZ Co., Ltd.",
                "project_or_location": "Plant 2",
                "purpose": "Trial",
                "requisition_date": "2026-06-06",
                "items": {"Sealant X 999": 4},
            },
        )
        self.assertEqual(requisition_response.status_code, 201)
        requisition = requisition_response.get_json()
        self.assertEqual(requisition["requisition_id"], 1)
        self.assertFalse(requisition["returned"])

        list_requisitions_response = self.client.get("/requisitions")
        self.assertEqual(list_requisitions_response.status_code, 200)
        requisitions = list_requisitions_response.get_json()
        self.assertEqual(len(requisitions), 1)
        self.assertEqual(requisitions[0]["items"]["Sealant X 999"], 4)

        return_response = self.client.post(
            "/returns",
            json={"requisition_id": 1, "receiver_name": "Staff A"},
        )
        self.assertEqual(return_response.status_code, 200)
        returned = return_response.get_json()
        self.assertTrue(returned["returned"])
        self.assertEqual(returned["receiver_name"], "Staff A")

    def test_requisition_validation_is_exposed_as_bad_request(self) -> None:
        response = self.client.post(
            "/requisitions",
            json={
                "borrower": "Unknown User",
                "customer": "ABC Co., Ltd.",
                "project_or_location": "Sample Project",
                "purpose": "Demo",
                "items": {"Sealant MS 541": 1},
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "borrower is not in allowed list")


if __name__ == "__main__":
    unittest.main()
