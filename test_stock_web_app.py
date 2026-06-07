import unittest

from api.index import app, reset_system


class TestStockWebApp(unittest.TestCase):
    def setUp(self) -> None:
        reset_system()
        self.client = app.test_client()

    def test_list_products_returns_default_products(self) -> None:
        response = self.client.get("/api/products")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["products"]), 4)

    def test_add_product_endpoint(self) -> None:
        response = self.client.post(
            "/api/products",
            json={
                "name": "Sample Product",
                "product_type": "Demo",
                "unit": "pcs",
                "color": "blue",
                "quantity": 5,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["product"]["name"], "Sample Product")

    def test_requisition_and_return_flow(self) -> None:
        create_response = self.client.post(
            "/api/requisitions",
            json={
                "borrower": "Thisalinee Bunlert",
                "customer": "ABC Co., Ltd.",
                "project_or_location": "Project A",
                "purpose": "Demo",
                "items": {"Sealant MS 541": 2},
                "requisition_date": "2026-06-06",
            },
        )

        self.assertEqual(create_response.status_code, 201)
        requisition_id = create_response.get_json()["requisition"]["requisition_id"]

        requisitions_response = self.client.get("/api/requisitions")
        self.assertEqual(requisitions_response.status_code, 200)
        self.assertEqual(len(requisitions_response.get_json()["requisitions"]), 1)

        return_response = self.client.post(
            "/api/returns",
            json={"requisition_id": requisition_id, "receiver_name": "Staff A"},
        )

        self.assertEqual(return_response.status_code, 200)
        self.assertTrue(return_response.get_json()["requisition"]["returned"])

    def test_add_borrower_endpoint(self) -> None:
        response = self.client.post("/api/borrowers", json={"borrower_name": "New Borrower"})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["borrower_name"], "New Borrower")


if __name__ == "__main__":
    unittest.main()
