import typing
from collections import defaultdict

from models.items import Item
from models.base_class import BaseClass
from utils import mprint
from app_exceptions.exceptions import *

WHOLESALE_MINIMUM = 1000


class Order(BaseClass):
    """Model for Order."""
    total_objects = None
    filename = "files/orders.txt"

    def __init__(self, user_id: str, items: typing.Dict, status="pending", coupon_used=False, order_id=None):
        self.refresh_base()
        self.__id = order_id if order_id else self.get_new_id()
        self.user_id = user_id
        self.items = items
        self.status = status
        self.coupon_used = coupon_used

    def __repr__(self):
        strng = "Items: \n"
        items = Item.read(Item.filename)
        for item, value in self.items.items():
            strng += f"{items[item]['name']} x {value} pieces\n"
        strng += f"\ntotal: {self.get_total_price()} EUR | status: {self.status}\n"
        if self.coupon_used:
            strng += f"Coupon discount (5%) will be applied on total amount.\n"
            strng += f"Total: {round(self.get_total_price() * 0.95, 2)} EUR"
        elif self.get_total_price() > WHOLESALE_MINIMUM:
            strng += "Wholesale discount (15%) will be applied on total amount.\n"
            strng += f"Total: {round(self.get_total_price() * 0.85, 2)} EUR"
        return strng

    @property
    def order_id(self):
        return self.__id

    def get_new_id(self) -> int:
        """
        Generating ID for new Item.
        :return: ID, int.
        """
        orders = self.read(self.filename)
        if self.total_objects == 0:
            return 1
        while str(self.total_objects) in orders:
            self.total_objects += 1
        return self.total_objects

    @classmethod
    def create_order_object(cls, order_id: str) -> "Order":
        """
        Creates order instance.
        :param order_id: order ID, int.
        :return: order instance.
        """
        orders = cls.read(cls.filename)
        order = orders.get(order_id)
        if not order:
            raise NonExistingOrderException
        order_object = Order(order["user"],
                             items=order["items"],
                             status=order["status"],
                             coupon_used=order["coupon_used"],
                             order_id=int(order_id))
        return order_object

    @classmethod
    def remove(cls, order_id: int) -> None:
        """
        Removing order and restoring items on stock.
        :param order_id: order ID, int.
        :return: None.
        """
        order_id = str(order_id)
        orders = cls.read(cls.filename)
        try:
            items = orders[order_id].get("items")
            for key, value in items.items():
                try:
                    Item.return_to_stock(key, value)
                except OrderAPPException as e:
                    mprint(e.__str__())
            orders.pop(order_id)
            cls.write(orders, cls.filename)
        except OrderAPPException as e:
            mprint(e.__str__())

    @classmethod
    def get_most_popular_items(cls) -> None:
        """
        Printing three most popular items on stdout.
        :return: None.
        """
        try:
            orders = cls.read(cls.filename)
        except OrderAPPException as e:
            mprint(e.__str__())
            return
        popular_items = defaultdict(int)
        for order in orders:
            for key, value in orders[order]["items"].items():
                popular_items[key] += value
        items = list(popular_items.items())
        items.sort(key=lambda x: x[1], reverse=True)
        mprint("Three most popular products are:", delimiter="_")
        for item, qty in items[:3]:
            try:
                product = Item.create_item_object(item)
                print(f"Product: {product.name} | sold: {qty} pieces.")
            except OrderAPPException as e:
                mprint(e.__str__())

    def get_total_price(self, update=False):
        """
        Calculating total amount for order.
        :param update: If update is True, updating items stock.
        :return: None.
        """
        total = 0
        for item, quantity in self.items.items():
            product = Item.create_item_object(item)
            if update:
                try:
                    product.update_stock(item, quantity)
                except OrderAPPException as e:
                    mprint(e.__str__())
            price = product.price * quantity
            total += price
        return round(total, 2)

    def record_order(self, apply_coupon=False):
        """
        Saving new Order to file.
        :param apply_coupon: applies coupon discount if True
        :return: None.
        """
        orders = self.read(self.filename)
        if apply_coupon:
            total_price = round(self.get_total_price(update=True) * 0.95, 2)
            self.coupon_used = True
            mprint(f"Coupon discount of 5% applied on your order. Total balance is: {total_price} EUR")
        elif self.get_total_price() > WHOLESALE_MINIMUM:
            total_price = round(self.get_total_price(update=True) * 0.85, 2)
            mprint(f"Wholesale discount applied on your order. Total balance is: {total_price} EUR")
        else:
            total_price = self.get_total_price(update=True)
            mprint(f"There is no discount on your total amount. Total balance is: {total_price} EUR")
        self.status = "ordered"
        orders[self.order_id] = {
            "user": self.user_id,
            "items": self.items,
            "total": total_price,
            "coupon_used": apply_coupon,
            "status": self.status
        }
        self.write(orders, self.filename)

    def print_info(self, order_id: str) -> None:
        """
        Print Order Info on stdout.
        :param order_id: ID of Order.
        :return: None.
        """
        orders = self.read(self.filename)
        order_id = str(order_id)
        if orders.get(order_id, None):
            total = 0
            items = orders[order_id]["items"]
            mprint(f"Order ID: {order_id}", delimiter="_")
            for item in items:
                item_obj = Item.create_item_object(item)
                total += item_obj.price * items[item]
                print(f"You have ordered {item_obj.name} x {items[item]} pieces.")
            print(f"Total: {total:.2f} EUR")
