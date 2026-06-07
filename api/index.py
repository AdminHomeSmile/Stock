from __future__ import annotations

from datetime import date

from flask import Flask, Response, jsonify, request

from stock_system import create_default_stock_system

app = Flask(__name__)
_system = create_default_stock_system()


def reset_system() -> None:
    global _system
    _system = create_default_stock_system()


def _product_to_dict(product) -> dict:
    return {
        "name": product.name,
        "product_type": product.product_type,
        "unit": product.unit,
        "color": product.color,
        "quantity": product.quantity,
    }


def _requisition_to_dict(requisition) -> dict:
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


def _bad_request(message: str) -> tuple[Response, int]:
    return jsonify({"error": message}), 400


@app.get("/")
def root() -> Response:
    return jsonify({"message": "Stock API is running"})


@app.get("/api/products")
def list_products() -> Response:
    products = [_product_to_dict(product) for product in _system.products.values()]
    return jsonify({"products": products})


@app.post("/api/products")
def add_product() -> tuple[Response, int]:
    payload = request.get_json(silent=True) or {}

    try:
        _system.add_product(
            name=str(payload["name"]),
            product_type=str(payload["product_type"]),
            unit=str(payload["unit"]),
            color=str(payload["color"]),
            quantity=int(payload["quantity"]),
        )
    except KeyError as e:
        return _bad_request(f"missing field: {e.args[0]}")
    except (TypeError, ValueError):
        return _bad_request("invalid product payload")

    return jsonify({"product": _product_to_dict(_system.products[str(payload["name"])])}), 201


@app.post("/api/borrowers")
def add_borrower() -> tuple[Response, int]:
    payload = request.get_json(silent=True) or {}
    borrower_name = str(payload.get("borrower_name", "")).strip()
    if not borrower_name:
        return _bad_request("borrower_name is required")

    _system.add_borrower(borrower_name)
    return jsonify({"borrower_name": borrower_name}), 201


@app.post("/api/requisitions")
def create_requisition() -> tuple[Response, int]:
    payload = request.get_json(silent=True) or {}

    try:
        requisition_date_raw = payload.get("requisition_date")
        requisition_date = date.fromisoformat(requisition_date_raw) if requisition_date_raw else date.today()
        items = {str(product_name): int(quantity) for product_name, quantity in payload["items"].items()}

        requisition = _system.requisition_sample(
            borrower=str(payload["borrower"]),
            customer=str(payload["customer"]),
            project_or_location=str(payload["project_or_location"]),
            purpose=str(payload["purpose"]),
            requisition_date=requisition_date,
            items=items,
        )
    except KeyError as e:
        return _bad_request(f"missing field: {e.args[0]}")
    except (AttributeError, TypeError, ValueError):
        return _bad_request("invalid requisition payload")

    return jsonify({"requisition": _requisition_to_dict(requisition)}), 201


@app.post("/api/returns")
def return_items() -> Response | tuple[Response, int]:
    payload = request.get_json(silent=True) or {}
    try:
        requisition_id = int(payload["requisition_id"])
        receiver_name = str(payload["receiver_name"])
        _system.return_items(requisition_id, receiver_name)
    except KeyError as e:
        return _bad_request(f"missing field: {e.args[0]}")
    except (TypeError, ValueError):
        return _bad_request("invalid return payload")

    requisition = _system.requisitions.get(requisition_id)
    if requisition is None:
        return _bad_request("requisition not found")
    return jsonify({"requisition": _requisition_to_dict(requisition)})


@app.get("/api/requisitions")
def list_requisitions() -> Response:
    requisitions = [_requisition_to_dict(req) for req in _system.requisitions.values()]
    return jsonify({"requisitions": requisitions})
