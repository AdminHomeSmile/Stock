from datetime import date

from stock_system import create_default_stock_system


def print_menu() -> None:
    print("\n=== Stock System ===")
    print("1. Show products")
    print("2. Add product")
    print("3. Add borrower")
    print("4. Borrow items")
    print("5. Return items")
    print("6. Show requisitions")
    print("0. Exit")


def show_products(system) -> None:
    print("\n--- Products ---")
    if not system.products:
        print("No products")
        return
    for p in system.products.values():
        print(f"- {p.name} | type={p.product_type} | unit={p.unit} | color={p.color} | qty={p.quantity}")


def add_product(system) -> None:
    name = input("Product name: ").strip()
    product_type = input("Product type: ").strip()
    unit = input("Unit: ").strip()
    color = input("Color: ").strip()
    quantity = int(input("Quantity: ").strip())
    system.add_product(name, product_type, unit, color, quantity)
    print("Added product.")


def add_borrower(system) -> None:
    borrower = input("Borrower name: ").strip()
    system.add_borrower(borrower)
    print("Added borrower.")


def borrow_items(system) -> None:
    borrower = input("Borrower name: ").strip()
    customer = input("Customer/company: ").strip()
    project_or_location = input("Project/location: ").strip()
    purpose = input("Purpose: ").strip()
    items_raw = input("Items (example: Sealant MS 541=2,Sealant SN 221=3): ").strip()
    items = {}
    for part in items_raw.split(","):
        if not part.strip():
            continue
        name, qty = part.split("=")
        items[name.strip()] = int(qty.strip())
    req = system.requisition_sample(
        borrower=borrower,
        customer=customer,
        project_or_location=project_or_location,
        purpose=purpose,
        requisition_date=date.today(),
        items=items,
    )
    print(f"Borrowed successfully. Requisition ID: {req.requisition_id}")


def return_items(system) -> None:
    requisition_id = int(input("Requisition ID: ").strip())
    receiver_name = input("Receiver name: ").strip()
    system.return_items(requisition_id, receiver_name)
    print("Returned successfully.")


def show_requisitions(system) -> None:
    print("\n--- Requisitions ---")
    if not system.requisitions:
        print("No requisitions")
        return
    for r in system.requisitions.values():
        status = "returned" if r.returned else "borrowed"
        print(f"- ID={r.requisition_id} | borrower={r.borrower} | status={status} | items={r.items}")


def main() -> None:
    system = create_default_stock_system()
    while True:
        print_menu()
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                show_products(system)
            elif choice == "2":
                add_product(system)
            elif choice == "3":
                add_borrower(system)
            elif choice == "4":
                borrow_items(system)
            elif choice == "5":
                return_items(system)
            elif choice == "6":
                show_requisitions(system)
            elif choice == "0":
                print("Bye")
                break
            else:
                print("Invalid choice")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
