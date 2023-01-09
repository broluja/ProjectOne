from models.base_class import BaseClass
from app_exceptions.exceptions import *
from utils import mprint


class Item(BaseClass):
    """Model for Item."""
    filename = "files/items.txt"
    total_objects = None

    def __init__(self, name: str, price: float, stock: int, item_id=None):
        self.refresh_base()
        self.__id = self.total_objects + 1 if item_id is None else item_id
        self.name = name
        self.__price = price
        self.__stock = stock
        if self.item_id not in self.read(self.filename):
            self.record_item()

    def __repr__(self):
        return f"{self.name} - {self.price} EUR"

    @property
    def item_id(self) -> int:
        return self.__id

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, value) -> None:
        if not isinstance(value, float) or value < 0:
            raise ItemPriceException
        self.__price = value

    @property
    def stock(self) -> int:
        return self.__stock

    @stock.setter
    def stock(self, value) -> None:
        if not isinstance(value, int) or value < 0:
            raise InvalidStockNumberException
        self.__stock = value

    @classmethod
    def create_item_object(cls, item_id) -> "Item":
        """
        Creates an instance of item if exists in a file.
        :param item_id: item ID, str.
        :return: item instance.
        """
        products = cls.read(cls.filename)
        if item_id in products:
            return Item(products[item_id]["name"], products[item_id]["price"], products[item_id]["stock"], item_id)
        else:
            raise NonExistingItemException

    @classmethod
    def show_products(cls) -> None:
        """
        Prints all items on stdout.
        :return: None.
        """
        products = cls.read(cls.filename)
        white_space = " " * 55
        mprint(f"{'Order APP Products':^75s}", delimiter=" ")
        mprint("Code - Product" + white_space + "Price (EUR)", delimiter=".")
        to_print = ""
        for item_id in products:
            try:
                item = cls.create_item_object(item_id)
                if item.stock > 0:
                    length = 64 - len(item.name)
                    line = "." * length
                    to_print += f"{item.item_id:<3} - {item.name} {line} {item.price:>8}\n"
                else:
                    to_print += f"{item.item_id:<3} - {item.name} - {'currently not available on stock':>}.\n"
            except OrderAPPException as e:
                mprint(e.__str__())
        mprint(to_print)

    @classmethod
    def check_stock(cls, item_id, quantity) -> bool:
        try:
            item = cls.create_item_object(item_id)
            if item and item.stock >= quantity:
                return True
        except OrderAPPException as e:
            mprint(e.__str__())
            return False

    @classmethod
    def return_to_stock(cls, item_id: str, qty: int) -> None:
        """
        Return items to stock when user cancels his Order.
        :param item_id: item ID, str.
        :param qty: count of item.
        :return: None.
        """
        items = cls.read(cls.filename)
        if item_id in items:
            items[item_id]["stock"] += qty
            cls.write(items, cls.filename)
        else:
            raise NonExistingItemException

    @classmethod
    def select_item(cls) -> tuple:
        """
        Taking admins' data, new price and new stock count.
        :return: tuple with item ID, price and stock.
        """
        items = cls.read(cls.filename)
        item_id = input("Enter products ID or 'q' to quit >> ").lower()
        if item_id == 'q':
            return ()
        while item_id not in items:
            item_id = input("Invalid ID. Enter products ID or 'q' to quit >> ").lower()
            if item_id == 'q':
                return ()
        new_price = input("Enter new price or 'q' to quit >> ").lower()
        if new_price == 'q':
            return ()
        try:
            new_price = float(new_price)
        except ValueError:
            print("Wrong price value.")
            return cls.select_item()
        new_stock = input("Enter new count on stock or 'q' to quit >> ").lower()
        if new_stock == 'q':
            return ()
        while not new_stock.isdigit():
            new_stock = input("Invalid stock value. Enter new count on stock or 'q' to quit >> ").lower()
            if new_stock == 'q':
                return ()
        return item_id, new_price, int(new_stock)

    def record_item(self) -> None:
        """
        Record new Item.
        :return:
        """
        items = self.read(self.filename)
        items[self.item_id] = {"name": self.name, "price": self.price, "stock": self.stock}
        self.write(items, self.filename)

    @classmethod
    def update_stock(cls, item_id: str, quantity: int, new_price: float = None, adding=False) -> None:
        """
        Updating stock count for specific Item.
        :param item_id: Item ID, str.
        :param quantity: new quantity, int.
        :param new_price: new item price, float.
        :param adding: bool, True if we are adding to stock.
        :return: None.
        """
        items = cls.read(cls.filename)
        try:
            if adding:
                items[item_id]["stock"] = quantity
            else:
                items[item_id]["stock"] -= quantity
            if new_price:
                items[item_id]["price"] = float(new_price)
            cls.write(items, cls.filename)
        except KeyError:
            raise NonExistingItemException

    @classmethod
    def add_new_item(cls) -> None:
        """
        Adding new Item to the file.
        :return: None.
        """
        item_name = input("Enter new product`s name or 'q' to quit >> ")
        if item_name.lower() == 'q':
            return
        price = input("Enter new product`s price or 'q' to quit >> ").lower()
        if price == 'q':
            return
        try:
            price = float(price)
        except ValueError:
            print("Not valid price value")
            return cls.add_new_item()
        count = input("Enter stock count or 'q' to quit >> ").lower()
        if count == 'q':
            return
        while not count.isdigit():
            count = input("Invalid stock value. Enter stock count or 'q' to quit >> ").lower()
            if count == 'q':
                return
        Item(name=item_name.title(), price=price, stock=int(count))
        mprint("New Item added! ☻")
