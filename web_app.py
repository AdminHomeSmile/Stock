from __future__ import annotations

import json
import logging
import threading
from datetime import date
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from stock_system import StockSystem, create_default_stock_system


class StockWebApp:
    def __init__(self, system: StockSystem | None = None) -> None:
        self.system = system or create_default_stock_system()
        self._lock = threading.RLock()

    def get_state(self) -> dict[str, Any]:
        with self._lock:
            products = [
                {
                    "name": product.name,
                    "product_type": product.product_type,
                    "unit": product.unit,
                    "color": product.color,
                    "quantity": product.quantity,
                }
                for product in sorted(self.system.products.values(), key=lambda p: p.name)
            ]
            requisitions = [
                {
                    "requisition_id": requisition.requisition_id,
                    "borrower": requisition.borrower,
                    "customer": requisition.customer,
                    "project_or_location": requisition.project_or_location,
                    "purpose": requisition.purpose,
                    "requisition_date": requisition.requisition_date.isoformat(),
                    "items": dict(requisition.items),
                    "returned": requisition.returned,
                    "receiver_name": requisition.receiver_name,
                }
                for requisition in sorted(self.system.requisitions.values(), key=lambda r: r.requisition_id)
            ]
            return {
                "products": products,
                "borrowers": sorted(self.system.allowed_borrowers),
                "requisitions": requisitions,
            }

    def run_action(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            if action == "add_product":
                quantity = int(payload["quantity"])
                self.system.add_product(
                    name=str(payload["name"]).strip(),
                    product_type=str(payload["product_type"]).strip(),
                    unit=str(payload["unit"]).strip(),
                    color=str(payload["color"]).strip(),
                    quantity=quantity,
                )
            elif action == "add_borrower":
                self.system.add_borrower(str(payload["borrower_name"]).strip())
            elif action == "borrow":
                requested_date = str(payload.get("requisition_date", "")).strip()
                requisition_date = date.fromisoformat(requested_date) if requested_date else date.today()
                raw_items = payload.get("items", {})
                items = {str(name): int(quantity) for name, quantity in raw_items.items()}
                self.system.requisition_sample(
                    borrower=str(payload["borrower"]).strip(),
                    customer=str(payload["customer"]).strip(),
                    project_or_location=str(payload["project_or_location"]).strip(),
                    purpose=str(payload["purpose"]).strip(),
                    requisition_date=requisition_date,
                    items=items,
                )
            elif action == "return":
                self.system.return_items(int(payload["requisition_id"]), str(payload["receiver_name"]).strip())
            else:
                raise ValueError("unknown action")
            return self.get_state()


INDEX_FILE = Path(__file__).with_name("web").joinpath("index.html")


class StockHTTPRequestHandler(BaseHTTPRequestHandler):
    app = StockWebApp()
    max_body_size = 1_000_000

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            self._send_html(INDEX_FILE.read_text(encoding="utf-8"))
            return
        if self.path == "/api/state":
            self._send_json({"ok": True, "state": self.app.get_state()})
            return
        self._send_json({"ok": False, "error": "not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/api/action":
            self._send_json({"ok": False, "error": "not found"}, status=HTTPStatus.NOT_FOUND)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > self.max_body_size:
                raise ValueError("request body too large")
            raw_body = self.rfile.read(content_length)
            body = json.loads(raw_body.decode("utf-8") or "{}")
            state = self.app.run_action(str(body.get("action", "")), dict(body.get("payload", {})))
            self._send_json({"ok": True, "state": state})
        except (TypeError, KeyError, ValueError) as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        except Exception:  # noqa: BLE001
            logging.exception("Unhandled /api/action error")
            self._send_json({"ok": False, "error": "internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, content: str) -> None:
        body = content.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        if args and isinstance(args[1], int) and args[1] < 400:
            return
        super().log_message(format, *args)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), StockHTTPRequestHandler)
    print(f"Open http://{host}:{port} in your browser")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
