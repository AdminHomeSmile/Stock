from datetime import date

from flask import Flask, jsonify, request

from stock_system import Requisition, create_default_stock_system

app = Flask(__name__)
system = create_default_stock_system()


def _product_to_dict(product) -> dict:
    return {
        "name": product.name,
        "product_type": product.product_type,
        "unit": product.unit,
        "color": product.color,
        "quantity": product.quantity,
    }


def _requisition_to_dict(requisition: Requisition) -> dict:
    return {
        "requisition_id": requisition.requisition_id,
        "borrower": requisition.borrower,
        "customer": requisition.customer,
        "project_or_location": requisition.project_or_location,
        "purpose": requisition.purpose,
        "requisition_date": requisition.requisition_date.isoformat(),
        "items": requisition.items,
        "returned": requisition.returned,
        "receiver_name": requisition.receiver_name,
    }


@app.get("/")
def health() -> tuple:
    return jsonify({"message": "Stock API is running"}), 200


@app.get("/products")
def list_products() -> tuple:
    products = [_product_to_dict(product) for product in system.products.values()]
    return jsonify(products), 200


@app.post("/products")
def add_product() -> tuple:
    payload = request.get_json(silent=True) or {}
    try:
        system.add_product(
            name=payload["name"],
            product_type=payload["product_type"],
            unit=payload["unit"],
            color=payload["color"],
            quantity=int(payload["quantity"]),
        )
    except KeyError as exc:
        return jsonify({"error": f"missing field: {exc.args[0]}"}), 400
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(_product_to_dict(system.products[payload["name"]])), 201


@app.post("/borrowers")
def add_borrower() -> tuple:
    payload = request.get_json(silent=True) or {}
    borrower_name = payload.get("borrower_name", "").strip()
    if not borrower_name:
        return jsonify({"error": "borrower_name is required"}), 400
    system.add_borrower(borrower_name)
    return jsonify({"borrower_name": borrower_name}), 201


@app.post("/requisitions")
def create_requisition() -> tuple:
    payload = request.get_json(silent=True) or {}
    try:
        requisition_date = payload.get("requisition_date")
        parsed_date = date.fromisoformat(requisition_date) if requisition_date else date.today()
        requisition = system.requisition_sample(
            borrower=payload["borrower"],
            customer=payload["customer"],
            project_or_location=payload["project_or_location"],
            purpose=payload["purpose"],
            requisition_date=parsed_date,
            items=payload["items"],
        )
    except KeyError as exc:
        return jsonify({"error": f"missing field: {exc.args[0]}"}), 400
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(_requisition_to_dict(requisition)), 201


@app.post("/returns")
def return_items() -> tuple:
    payload = request.get_json(silent=True) or {}
    try:
        system.return_items(int(payload["requisition_id"]), payload["receiver_name"])
    except KeyError as exc:
        return jsonify({"error": f"missing field: {exc.args[0]}"}), 400
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    requisition = system.requisitions[int(payload["requisition_id"])]
    return jsonify(_requisition_to_dict(requisition)), 200


@app.get("/requisitions")
def list_requisitions() -> tuple:
    requisitions = [_requisition_to_dict(req) for req in system.requisitions.values()]
    return jsonify(requisitions), 200
