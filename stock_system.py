from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict


@dataclass
class Product:
    name: str
    product_type: str
    unit: str
    color: str
    quantity: int


@dataclass
class Requisition:
    requisition_id: int
    borrower: str
    customer: str
    project_or_location: str
    purpose: str
    requisition_date: date
    items: Dict[str, int]
    returned: bool = False
    receiver_name: str | None = None


class StockSystem:
    def __init__(self) -> None:
        self.products: Dict[str, Product] = {}
        self.allowed_borrowers: set[str] = set()
        self.requisitions: Dict[int, Requisition] = {}
        self._next_requisition_id = 1

    def add_product(self, name: str, product_type: str, unit: str, color: str, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("quantity must not be negative")
        self.products[name] = Product(
            name=name,
            product_type=product_type,
            unit=unit,
            color=color,
            quantity=quantity,
        )

    def add_borrower(self, borrower_name: str) -> None:
        self.allowed_borrowers.add(borrower_name)

    def requisition_sample(
        self,
        borrower: str,
        customer: str,
        project_or_location: str,
        purpose: str,
        requisition_date: date,
        items: Dict[str, int],
    ) -> Requisition:
        if borrower not in self.allowed_borrowers:
            raise ValueError("borrower is not in allowed list")
        if not items:
            raise ValueError("items must not be empty")

        for product_name, quantity in items.items():
            if quantity <= 0:
                raise ValueError("requested quantity must be positive")
            if product_name not in self.products:
                raise ValueError(f"product not found: {product_name}")
            if self.products[product_name].quantity < quantity:
                raise ValueError(f"not enough stock for: {product_name}")

        for product_name, quantity in items.items():
            self.products[product_name].quantity -= quantity

        requisition = Requisition(
            requisition_id=self._next_requisition_id,
            borrower=borrower,
            customer=customer,
            project_or_location=project_or_location,
            purpose=purpose,
            requisition_date=requisition_date,
            items=dict(items),
        )
        self.requisitions[requisition.requisition_id] = requisition
        self._next_requisition_id += 1
        return requisition

    def return_items(self, requisition_id: int, receiver_name: str) -> None:
        if not receiver_name.strip():
            raise ValueError("receiver name is required")
        if requisition_id not in self.requisitions:
            raise ValueError("requisition not found")
        requisition = self.requisitions[requisition_id]
        if requisition.returned:
            raise ValueError("items already returned")

        for product_name, quantity in requisition.items.items():
            self.products[product_name].quantity += quantity

        requisition.returned = True
        requisition.receiver_name = receiver_name


def create_default_stock_system() -> StockSystem:
    system = StockSystem()

    system.add_product("Sealant MS 541", "Sealant", "หลอด", "N/A", 20)
    system.add_product("Sealant SN 221", "Sealant", "หลอด", "N/A", 120)
    system.add_product("Sealant SA 271", "Sealant", "หลอด", "N/A", 120)
    system.add_product("Sealant AC 181", "Sealant", "หลอด", "N/A", 20)

    for borrower in [
        "Thisalinee Bunlert",
        "Somchan Thongpussa",
        "Sawanya Kijanukul",
        "Jintana Pornpichayanurak",
        "Kittipong Pipattanakosit",
        "Teerawat Sahasathian",
        "Sankamol Khongsawatvorakul",
        "Piyapong Sornpao",
        "Thanawat Pattharaworasej",
        "Manassawee Rakkeat",
        "Rungroj Thongchumkom",
        "Kanitta Faigratoke",
        "Phumphan Tansarojvanich",
        "Nattakit Kanasnakankul",
        "Worapoj Phuckpetch",
        "Thanchanok Juajeen",
    ]:
        system.add_borrower(borrower)

    return system
