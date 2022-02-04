from .db import insert, selectall
from model.Customer import Customer
from .db_manager import check_table_exists


check_table_exists("customer")


def save_customer(customer: Customer) -> None:
    insert("customer", customer._asdict())


def get_all_cutomers() -> tuple[Customer]:
    rows = selectall("customer", list(Customer._fields))
    return tuple(
        Customer(row[0], row[1], row[2])
        for row in rows
    )
