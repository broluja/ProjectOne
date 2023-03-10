from models.users import User
from models.items import Item
from app_exceptions.exceptions import *
from utils import mprint


def main():
    user = None
    while not user:
        mprint("\tWelcome to Order APP!", "", "\tA. Register", "\tB. Login", delimiter=" ")
        users_input = input("Enter option or 'end' for exit >>> ").lower()

        if users_input == "a":
            User.register()

        elif users_input == "b":
            user = User.login()

        elif users_input == 'end':
            break

        else:
            mprint("Unavailable option.")

    else:
        users_input = None
        while users_input != "end":
            if user.is_admin():
                mprint("\tWelcome to Order APP!", delimiter=" ", end="")
                print("""
\tCustomer options:\n
\tA. Make Order (or continue current one)
\tB. My Cart
\tC. Clear my Cart
\tD. Save Order
\tE. Cancel saved Order
\tF. My saved Orders
\tG. Go to Payments
\tH. Show my coupon status
\tI. Show all Products
\tJ. Get my order in Excel File
\tK. Logout

\tAdmin options:\n
\tL. List all orders
\tM. Total amount of all orders
\tN. Money on account
\tO. Most popular Products
\tP. Used Coupons
\tQ. Users with unused Coupons
\tR. Add New Product
\tS. Update Product
\tT. Delete Product
\tU. Lock User
\tV. Unlock User\n""")
            else:
                mprint("\tWelcome to Order APP!", delimiter=" ", end="")
                print("""
\tCustomer options:\n
\tA. Make Order or continue current one
\tB. My Cart
\tC. Clear my Cart
\tD. Save Order
\tE. Cancel saved Order
\tF. My saved Orders
\tG. Go to Payments
\tH. Show my coupon status
\tI. Show all Products
\tJ. Get my order in Excel File
\tK. Logout\n""")

            users_input = input("Enter option or 'end' for exit >>> ").lower()

            if users_input == 'a':
                user.make_order()

            elif users_input == 'b':
                user.show_my_cart()
                input("Press any key to continue >> ")

            elif users_input == 'c':
                user.clear_cart()

            elif users_input == 'd':
                user.save_order()

            elif users_input == 'e':
                user.cancel_order()

            elif users_input == 'f':
                user.show_my_saved_orders()
                input("Press any key to continue >> ")

            elif users_input == 'g':
                user.go_to_payments()

            elif users_input == 'h':
                user.show_coupon()

            elif users_input == 'i':
                try:
                    Item.show_products()
                    input("Press any key to continue >> ")
                except OrderAPPException as e:
                    mprint(str(e))

            elif users_input == 'j':
                try:
                    user.generate_excel_file()
                except OrderAPPException as e:
                    mprint(str(e))

            elif users_input == 'k':
                if user.has_made_payments():
                    mprint(f"Logging out... Goodbye {user.username} ???")
                    return main()

            elif users_input == 'l':
                try:
                    user.get_orders()
                    input("Press any key to continue >> ")
                except OrderAPPException as e:
                    mprint(str(e))

            elif users_input == 'm':
                try:
                    user.get_brutto_orders()
                except OrderAPPException as e:
                    mprint(str(e))

            elif users_input == 'n':
                try:
                    user.get_total_money_paid()
                except OrderAPPException as e:
                    mprint(str(e))

            elif users_input == 'o':
                try:
                    user.get_popular_items()
                except OrderAPPException as e:
                    mprint(str(e))

            elif users_input == 'p':
                try:
                    user.get_used_coupons()
                    input("Press any key to continue >> ")
                except OrderAPPException as e:
                    mprint(str(e))

            elif users_input == 'q':
                try:
                    user.get_users_with_active_coupons()
                    input("Press any key to continue >> ")
                except OrderAPPException as e:
                    mprint(str(e))

            elif users_input == 'r':
                try:
                    user.add_new_item()
                except AdminStatusException as e:
                    mprint(str(e))

            elif users_input == 's':
                try:
                    user.update_items_count()
                except AdminStatusException as e:
                    mprint(str(e))

            elif users_input == 't':
                try:
                    user.delete_item()
                except AdminStatusException as e:
                    mprint(str(e))

            elif users_input == 'u':
                try:
                    user.lock_user()
                except AdminStatusException as e:
                    mprint(str(e))

            elif users_input == 'v':
                try:
                    user.lock_user(reverse=True)
                except AdminStatusException as e:
                    mprint(str(e))

            elif users_input != 'end':
                mprint("Unavailable option.")


if __name__ == "__main__":
    main()
