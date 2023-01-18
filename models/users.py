import os
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError

from models.base_class import BaseClass
from models.coupons import Coupon
from models.items import Item
from models.orders import Order, WHOLESALE_MINIMUM
from app_exceptions.exceptions import *
from utils import mprint, create_excel_file

load_dotenv()

ADMIN1 = os.getenv("ADMIN1")
ADMIN2 = os.getenv("ADMIN2")
PASSWORD1 = os.getenv("PASSWORD1")
PASSWORD2 = os.getenv("PASSWORD2")


class User(BaseClass):
    """Model for User"""
    total_objects = None
    filename = "files/users.txt"
    admin_credentials = {ADMIN1: PASSWORD1, ADMIN2: PASSWORD2}

    def __init__(self, username, email, password, user_id=None):
        self.refresh_base()
        self.__id = user_id
        self.__username = username
        self.__email = email
        self.__password = password
        self.__coupon = None
        self.__admin_status = None
        self.order = None
        self.saved_orders = self.load_my_saved_orders()
        if not self.is_registered_email(email):
            self.record_user(self.username, self.email, self.password)

    @property
    def id(self):
        return self.__id

    @property
    def username(self):
        return self.__username

    @property
    def email(self):
        return self.__email

    @property
    def password(self):
        return self.__password

    @property
    def coupon(self):
        return self.__coupon

    @coupon.setter
    def coupon(self, value):
        self.__coupon = value

    @property
    def admin_status(self):
        return self.__admin_status

    @admin_status.setter
    def admin_status(self, value):
        if not isinstance(value, bool):
            raise AdminStatusException("Invalid Admin status.")
        self.__admin_status = value

    def load_my_saved_orders(self) -> list:
        """
        Loads saved orders User have in a file.
        :return: list of orders.
        """
        orders = Order.read(Order.filename)
        my_unpaid_orders = []
        for order in orders:
            if orders[order]["user"] == self.id and orders[order]["status"] != "paid":
                my_unpaid_orders.append(Order.create_order_object(order))
        return my_unpaid_orders

    @classmethod
    def create_user_object(cls, _id) -> "User":
        """
        Creates user instance.
        :param _id: user ID.
        :return: User instance.
        """
        users = cls.read(cls.filename)
        if _id in users:
            user = User(users[_id]["username"], users[_id]["email"], users[_id]["password"], user_id=_id)
            coupon_number = users[_id]["coupon"]
            user.coupon = coupon_number
            if user.is_admin():
                user.admin_status = True
            return user
        else:
            raise NonExistingUserException

    def is_admin(self) -> bool:
        """
        Validate admin user.
        :return: bool.
        """
        for key in self.admin_credentials.keys():
            if self.username == key and self.password == self.admin_credentials[key]:
                return True
        return False

    @classmethod
    def is_registered_email(cls, email: str) -> bool:
        """
        Validate email. Return True if email already in base, else False.
        :param email: str, email for registration
        :return: bool
        """
        try:
            users = cls.read(cls.filename)
            for user in users:
                if users[user]["email"] == email:
                    return True
        except OrderAPPException as e:
            mprint(e.__str__())
        return False

    @staticmethod
    def validate_email(email) -> bool:
        try:
            valid = validate_email(email)
            valid_email = valid.email
            return valid_email
        except EmailNotValidError as e:
            mprint(e.__str__())
            return False

    @classmethod
    def register(cls) -> None:
        """
        Create User account and save it to file.
        :return: None.
        """
        try:
            cls.read(cls.filename)
        except OrderAPPException as e:
            return mprint(e.__str__())

        username = input("Enter username or 'q' for quit >> ")
        if username.lower() == 'q':
            return
        elif not username:
            mprint("You have to use some username.")
            return cls.register()

        email = input("Enter email or 'q' to quit >> ")
        if email.lower() == 'q':
            return
        while cls.is_registered_email(email):
            email = input(f"{email} already registered. Enter new email or 'q' to go back >> ")
            if email.lower() == 'q':
                return
        while not cls.validate_email(email):
            email = input(f"Enter new email or 'q' to go back >> ")
            if email.lower() == 'q':
                return

        password = input("Enter password or 'q' for quit >> ")
        if password.lower() == 'q':
            return
        if not password:
            mprint("Cannot register without password. ♫")
            return cls.register()
        try:
            User(username, email, password)
        except OrderAPPException as e:
            mprint(e.__str__())
            return
        mprint("\tAccount created. You can login now")

    @classmethod
    def login(cls) -> ("User", None):
        """
        Login User to Order APP.
        :return: User instance.
        """
        try:
            users = cls.read(cls.filename)
        except OrderAPPException as e:
            mprint(e.__str__())
            return
        while True:
            email = input("Enter email or 'q' for quit >> ")
            if email.lower() == 'q':
                return
            password = input("Enter password or 'q' for quit >> ")
            if password.lower() == 'q':
                return
            else:
                for user in users:
                    if users[user].get("email") == email and users[user].get("password") == password:
                        mprint(f"Successfully logged in. Welcome {users[user]['username']} ♫ ♪ ")
                        try:
                            return cls.create_user_object(user)
                        except OrderAPPException as e:
                            mprint(e.__str__())
                mprint("Not valid credentials. ☻")

    def refresh_base(self) -> None:
        """
        Getting the number of records in a file to generate next ID number.
        Creating two Admins also if they not already created.
        :return: None.
        """
        try:
            super().refresh_base()
        except OrderAPPException as e:
            mprint(e.__str__())
            return
        if self.total_objects == 0:
            for key, value in self.admin_credentials.items():
                self.record_user(key, f"{key}@order_app.com", value, admin=True)

    def record_user(self, username, email, password, admin=False) -> None:
        """
        Records a New User.
        :param username: str, users username.
        :param email: str, users email.
        :param password: str, users password.
        :param admin: bool, True if user is admin.
        :return: None.
        """
        users = self.read(self.filename)
        while str(self.total_objects) in users:
            self.total_objects += 1
        user_id = self.total_objects
        self.__id = user_id
        try:
            users = self.read(self.filename)
            coupon = Coupon()
            users[user_id] = {"username": username,
                              "email": email,
                              "password": password,
                              "orders": [],
                              "coupon": coupon.value}
            self.write(users, self.filename)
            if not admin:
                mprint(f"\t{username} registered!")
        except OrderAPPException as e:
            mprint(e.__str__())

    def show_coupon(self) -> None:
        """
        Print info on stdout whether user have used his coupon, or, if not, that he can still do it.
        :return: None.
        """
        try:
            coupons = Coupon.read(Coupon.filename)
            if self.coupon in coupons:
                coupon = Coupon.create_coupon_object(self.coupon)
                if coupon.is_used:
                    mprint("You have used your coupon.")
                else:
                    mprint(f"Your can still use your coupon: {coupon.value}")
        except OrderAPPException as e:
            mprint(e.__str__())

    def show_my_cart(self):
        """
        Prints current order in users Cart on stdout.
        :return: None.
        """
        if self.order:
            mprint(self.order)
        else:
            mprint("Your cart is empty!")

    @staticmethod
    def pick_products(order: dict) -> dict:
        """
        Pick products for new order or for continuing old one. Check if there is enough
        products on stock for your order.
        :param order: current order saved in a dictionary.
        :return: dict, order dictionary.
        """
        items = Item.read(Item.filename)
        while True:
            mprint("Pick a Product.", delimiter="_")
            item = input("Enter item code to add it to cart or 'f' to finish >> ").lower()
            if item == 'f':
                return order
            while item not in items:
                item = input("Invalid item code. Enter item code to add it to cart or 'f' to finish >> ").lower()
                if item == 'f':
                    return order
            quantity = input("Enter quantity (integer number) or 'f' to finish >> ").lower()
            if quantity == 'f':
                return order
            while not quantity.isnumeric() or quantity == "0":
                quantity = input("Invalid input. Enter quantity (integer number) >> ").lower()
            quantity = int(quantity)
            if Item.check_stock(item, quantity):
                order[item] += quantity
                mprint(f"Picked {items[item]['name']}, {quantity} pieces", delimiter=" ")
            else:
                mprint(f"Selected quantity ({quantity}) is not available on stock.")

    def user_wants_coupon_discount(self) -> bool:
        """
        Ask User for applying 5% coupon discount if it is not already used.
        :return: bool
        """
        if not self.has_used_coupon():
            choice = input("Do you want to use your 5% coupon? Y or N >> ").lower()
            while choice not in ('y', 'n'):
                choice = input("Please enter Y for 'YES' or N for 'NO'. Do you want to use your 5% coupon? >> ").lower()
            if choice == 'y':
                coupon = input("Enter your coupon (press 'c' to see your coupon number or 'q' to go back) >> ")
                if coupon.lower() == 'c':
                    mprint(f"Your coupon: {self.coupon}")
                elif coupon.lower() == 'q':
                    mprint(f"Going back...", delimiter='.')
                    return self.user_wants_coupon_discount()
                elif coupon == self.coupon:
                    return True
                while coupon != self.coupon:
                    coupon = input("Enter your coupon (press 'c' to see your coupon number or 'q' to go back) >> ")
                    if coupon.lower() == 'c':
                        mprint(f"Your coupon: {self.coupon}")
                    elif coupon.lower() == 'q':
                        mprint(f"Going back...", delimiter='.')
                        return self.user_wants_coupon_discount()
                return True
        else:
            mprint("You have no active coupons.")
            return False

    def make_order(self) -> None:
        """
        Pick Products, create Order and store it in User.
        :return: None.
        """
        try:
            Item.show_products()
        except OrderAPPException as e:
            return mprint(e.__str__())
        if self.order:
            order = self.order.items
        else:
            order = defaultdict(int)
        order = self.pick_products(order)
        if order:
            my_order = Order(self.id, order)
            self.order = my_order
            mprint("Order stored in Cart. Save your order to confirm and make your payment. ☻")

    def save_order(self) -> None:
        """
        Save active order from user's Cart. If user uses coupon discount, update coupons file.
        :return: None.
        """
        if self.order:
            users = self.read(self.filename)
            if self.user_wants_coupon_discount():
                self.order.record_order(apply_coupon=True)
                coupon = Coupon.create_coupon_object(self.coupon)
                coupon.use_coupon()
            else:
                self.order.record_order()
            self.saved_orders.append(self.order)
            users[self.id]["orders"].append(self.order.order_id)
            mprint(f"Order {self.order.order_id} saved.", "Go to payments section ☻")
            self.order = None
            self.write(users, self.filename)
        else:
            mprint("You have no active orders. ♫")

    def update_user_orders(self, order_id: int) -> None:
        """
        Update user's orders and coupon status on canceling order.
        :param order_id: str, Order ID
        :return: None.
        """
        users = self.read(self.filename)
        try:
            order = Order.create_order_object(str(order_id))
        except OrderAPPException as e:
            mprint(e.__str__())
            return
        if order.coupon_used:
            try:
                Coupon.refund_coupon(self.coupon)
            except OrderAPPException as e:
                mprint(e.__str__())
        users[self.id]["orders"].remove(order_id)
        self.write(users, self.filename)

    def show_my_saved_orders(self) -> bool:
        """
        Print users saved orders if there is any.
        :return: bool
        """
        if self.saved_orders:
            mprint("Your saved orders:", delimiter=" ")
            for order in self.saved_orders:
                mprint(f"order ID: {order.order_id}", order, delimiter="_")
            return True
        else:
            mprint("You have no saved orders. ☻")
            return False

    def choose_saved_order(self) -> str:
        """
        Select one of saved orders, if there is any.
        :return: str, order ID
        """
        if self.show_my_saved_orders():
            orders = [str(order.order_id) for order in self.saved_orders]
            order_id = input("Enter order ID or 'q' to quit >> ")
            if order_id == 'q':
                return ""
            while order_id not in orders:
                order_id = input("Invalid order ID! Enter order ID or 'q' to quit >> ")
                if order_id == 'q':
                    return ""
            return order_id

    def cancel_order(self) -> None:
        """
        Cancel order and return products back to stock.
        :return: None.
        """
        if self.saved_orders:
            order_id = self.choose_saved_order()
            if order_id:
                for order in self.saved_orders:
                    if str(order.order_id) == order_id:
                        order.print_info(order.order_id)
                        mprint("Your order has been erased.")
                        self.update_user_orders(order.order_id)
                        Order.remove(order.order_id)
                        self.saved_orders.remove(order)
        else:
            mprint("You have no saved orders. ☻")

    def clear_cart(self) -> None:
        """
        Clear users Cart.
        :return: None.
        """
        if self.order:
            mprint("You have cleared your cart. ♫")
            self.order = None
        else:
            mprint("Your cart is already empty! ☻")

    def print_my_receipt(self, order_id) -> None:
        """
        Printing receipt for specific Order.
        :param order_id: Order ID, str.
        :return: None
        """
        answer = input("Do you want to print your receipt? Y or N >> ").lower()
        if answer == 'n':
            return
        while answer not in ('y', 'n'):
            answer = input("Pres 'Y' for YES or 'N' for NO. >> ").lower()
            if answer == 'n':
                return
        order = Order.create_order_object(order_id)
        now = datetime.now()
        mprint(f"{'Order APP':^80}", delimiter=".")
        print(f"Receipt number: {order_id}")
        print(f"Registered Customer: {self.username}")
        print(f"Date: {now.strftime('%d/%m/%Y')} | Time: {now.strftime('%H:%M:%S')}")
        print(f"{'EUR': >80}")
        for item in order.items:
            product = Item.create_item_object(item)
            qty = order.items[item]
            price = round(product.price * qty, 2)
            length = 76 - len(product.name) - len(str(price))
            line = " " * length
            mprint(f"{product.name} x {qty}{line}{price}", delimiter=".")
        if order.coupon_used:
            print(f"Total: {order.get_total_price():>73}")
            print("Coupon discount 5% used for this order.")
            mprint(f"New Total: {order.get_total_price() * 0.95:>69.2f}")
        elif order.get_total_price() > WHOLESALE_MINIMUM:
            print(f"Total: {order.get_total_price():>73}")
            print("Wholesale discount (15%) will be applied on total amount.")
            mprint(f"New Total: {order.get_total_price() * 0.85:>69.2f}")
        input("Press any key to continue >> ")

    def go_to_payments(self) -> None:
        """
        Select one of the saved orders and make payment.
        :return: None.
        """
        mprint("Pick Order by ID to make payment.", delimiter=".")
        order_id = self.choose_saved_order()
        if not order_id:
            return
        orders = Order.read(Order.filename)
        try:
            orders[order_id]["status"] = "paid"
            Order.write(orders, Order.filename)
            mprint(f"You have paid your order: {order_id}. ☻")
            self.print_my_receipt(order_id)
            for order in self.saved_orders:
                if str(order.order_id) == order_id:
                    self.saved_orders.remove(order)
        except OrderAPPException as e:
            mprint(e.__str__())

    def get_orders(self) -> None:
        """
        Admin Option. Prints all orders saved in file.
        :return: None.
        """
        if self.admin_status:
            orders = Order.read(Order.filename)
            if orders:
                mprint("Made orders:", delimiter=" ")
                for order in orders:
                    try:
                        user = self.create_user_object(orders[order]["user"])
                        print(f"User '{user.username}' ordered:")
                        for item_code, quantity in orders[order]["items"].items():
                            item = Item.create_item_object(item_code)
                            print(f"{item.name} x {quantity}")
                        mprint(f"Total: {orders[order]['total']:.2f} EUR", delimiter="_")
                    except OrderAPPException as e:
                        mprint(e.__str__())
            else:
                mprint("There is no saved orders. ☻")
        else:
            raise AdminStatusException

    def get_brutto_orders(self) -> None:
        """
        Admin Option. Prints total money for all orders.
        :return: None.
        """
        if self.admin_status:
            orders = Order.read(Order.filename)
            total = 0
            for order in orders:
                total += orders[order].get("total", 0)
            mprint(f"Brutto of all orders is {total:.2f} EUR.")
        else:
            raise AdminStatusException

    def get_total_money_paid(self):
        """
        Admin Option. Prints total money paid.
        :return: None.
        """
        if self.admin_status:
            orders = Order.read(Order.filename)
            total = 0
            for order in orders:
                if orders[order]["status"] == "paid":
                    total += orders[order].get("total", 0)
            mprint(f"Brutto money paid: {total:.2f} EUR.")
        else:
            raise AdminStatusException

    def get_used_coupons(self) -> None:
        """
        Admin Option. Prints all used coupons and users.
        :return: None.
        """
        if self.admin_status:
            coupons = Coupon.read(Coupon.filename)
            used_coupons = [coupon for coupon in coupons if coupons[coupon].get("used")]
            users = self.read(self.filename)
            users_with_used_coupon = [(users[user]["username"], users[user]["coupon"]) for user in users if
                                      users[user]["coupon"] in used_coupons]

            for username, coupon in users_with_used_coupon:
                mprint(f"User {username} used coupon: {coupon}", delimiter="_")
            if not used_coupons:
                mprint("There is no users with used coupons. ♫")
        else:
            raise AdminStatusException

    def get_users_with_active_coupons(self) -> None:
        """
        Admin Option. Prints all users with active 5% discount coupons.
        :return: None
        """
        if self.admin_status:
            users = self.read(self.filename)
            user_count = 0
            for user in users:
                coupon_id = users[user].get("coupon")
                coupon = Coupon.create_coupon_object(coupon_id)
                if not coupon.is_used:
                    mprint(f"{users[user]['username']} has active coupon {coupon.value}", delimiter=".")
                    user_count += 1
            if not user_count:
                mprint("There is no users with active coupons. ♫")
        else:
            raise AdminStatusException

    def get_popular_items(self) -> None:
        """
        Admin Option. Prints three most popular Products on stdout.
        :return: None.
        """
        if self.admin_status:
            Order.get_most_popular_items()
        else:
            raise AdminStatusException

    def update_items_count(self) -> None:
        """
        Admin Option. Updating products count on stock.
        :return:
        """
        if self.admin_status:
            items = Item.read(Item.filename)
            for item in items:
                item_object = Item.create_item_object(item)
                print(f"ID: {item_object.item_id} | Product: {item_object.name} | price: {item_object.price} |"
                      f" on stock: {item_object.stock}")
            new_values = Item.select_item()
            if not new_values:
                return
            try:
                Item.update_stock(item_id=new_values[0], quantity=new_values[2], new_price=new_values[1], adding=True)
                mprint("Item updated! ☻")
            except OrderAPPException as e:
                mprint(e.__str__())
        else:
            raise AdminStatusException

    def delete_item(self):
        """
        Admin Option. Delete product.
        :return: None.
        """
        if self.admin_status:
            items = Item.read(Item.filename)
            for item in items:
                item_object = Item.create_item_object(item)
                print(f"ID: {item_object.item_id} | Product: {item_object.name} | price: {item_object.price} |"
                      f" on stock: {item_object.stock}")
            item_id = input("Enter Product`s ID you want to delete or 'q' to quit >> ")
            if item_id.lower() == 'q':
                return
            while item_id not in items:
                item_id = input("Invalid ID. Enter Product`s ID you want to delete or 'q' to quit >> ")
                if item_id.lower() == 'q':
                    return
            product = Item.create_item_object(item_id)
            confirm = input(f"Are you sure you want to delete {product.name}? Y/N >>")
            while confirm.lower() not in ('y', 'n'):
                confirm = input(f"Enter Y for YES or N for NO. Are you sure you want to delete {product.name}? Y/N >> ")
            if confirm.lower() == 'y':
                try:
                    Item.delete_item(item_id)
                    mprint("Item deleted! ☻")
                except OrderAPPException as e:
                    mprint(e.__str__())
            else:
                mprint("Going back...", delimiter='.')
                return self.delete_item()
        else:
            raise AdminStatusException

    def add_new_item(self):
        """
        Admin Option. Adding new Product to file.
        :return:
        """
        if self.admin_status:
            Item.add_new_item()
        else:
            raise AdminStatusException

    def has_made_payments(self) -> bool:
        """
        Check if User has Orders in pending or waiting for Payment.
        :return: bool.
        """
        if self.order:
            mprint("You have order in pending. Save it or clear your Cart before logging out. ♫")
            return False
        elif self.saved_orders:
            mprint("You have saved order waiting for payment. Pay it or cancel before logging out. ♫")
            return False
        return True

    def has_used_coupon(self) -> bool:
        """
        Check if User has used Coupon or not.
        :return: bool.
        """
        try:
            return Coupon.get_status(self.coupon)
        except OrderAPPException as e:
            mprint(e.__str__())
            return True

    def list_my_orders(self) -> str:
        """
        List all Users Orders and asking User to select one for generating Excel File.
        :return: str, order ID
        """
        orders = Order.read(Order.filename)
        my_orders = [order for order in orders if orders[order]["user"] == self.id]
        if my_orders:
            for order in my_orders:
                mprint(f"Order ID: {order}", delimiter=" ")
                try:
                    my_order = Order.create_order_object(order)
                except OrderAPPException as e:
                    mprint(e.__str__())
                    return ""
                mprint(my_order, delimiter="_")
            order_id = input("Enter order ID or 'q' to quit >> ")
            if order_id == 'q':
                return ""
            while order_id not in my_orders:
                order_id = input("Invalid order ID! Enter order ID or 'q' to quit >> ")
                if order_id == 'q':
                    return ""
            return order_id
        else:
            return "No Orders"

    def generate_excel_file(self) -> None:
        """
        Generate Excel file for Order that User made.
        :return: None.
        """
        mprint("My orders: ", delimiter="_")
        order_id = self.list_my_orders()
        if order_id and order_id != "No Orders":
            orders = Order.read(Order.filename)
            try:
                order = Order.create_order_object(order_id)
            except OrderAPPException as e:
                return mprint(e.__str__())
            total = orders[order_id].get("total")
            now = datetime.now()
            frame = []
            for key, value in order.items.items():
                item = Item.create_item_object(key)
                frame.append([item.item_id, item.name, item.price, value, round(item.price * value, 2)])
            frame.append([])
            if not order.coupon_used and order.get_total_price() > WHOLESALE_MINIMUM:
                frame.append(["Applied: ", "Wholesale discount (15%)", "", "Sum", str(total)])
            elif order.coupon_used:
                frame.append(["Applied: ", "Coupon discount (5%)", "", "Sum", str(total)])
            else:
                frame.append(["", "", "", "Sum", str(total)])
            frame.append([])
            coupon_used = "YES" if order.coupon_used else "No"
            frame.append(["Used coupon: ", coupon_used, "", "", ""])
            frame.append(["Date", f"{now.strftime('%d/%m/%Y')}", "", "", ""])
            frame.append(["Time", f"{now.strftime('%H:%M:%S')}", "", "", ""])
            try:
                create_excel_file(frame, order_id)
            except OrderAPPException as e:
                mprint(e.__str__())
            mprint("Look for your file in main Folder ♫")
        elif order_id == "No Orders":
            mprint("You have not made any orders yet ☻")
        else:
            mprint("You can try again later ☻")
