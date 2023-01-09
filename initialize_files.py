"""Run this file before running main to initialize files."""
from models.items import Item
from utils import init_file, populate_items


if __name__ == "__main__":
    init_file("files/items.txt")
    populate_items("files/items.csv", Item)
    init_file("files/coupons.txt")
    init_file("files/orders.txt")
    init_file("files/users.txt")
