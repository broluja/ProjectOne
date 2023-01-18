"""Order APP Exceptions"""


class OrderAPPException(Exception):
    customer_message = "Something went wrong. Please try again later."

    def __init__(self, *args):
        if args:
            self.customer_message = args[0]
        super().__init__(self.customer_message)


# File Exceptions
class InitializeFileError(OrderAPPException):
    customer_message = "Files not initialized. Run initialize_file.py."


class FileAlreadyCreatedException(OrderAPPException):
    customer_message = "You have already generated this order in Excel file."


# Item Exceptions
class ItemPriceException(OrderAPPException):
    customer_message = "Invalid Item Price. Please use only positive floats."


class InvalidStockNumberException(OrderAPPException):
    customer_message = "Invalid Stock number. Please use only positive integers."


class NonExistingItemException(OrderAPPException):
    customer_message = "Item does not exist."


# User Exceptions
class AdminStatusException(OrderAPPException):
    customer_message = "This option is unavailable for you."


class NonExistingUserException(OrderAPPException):
    customer_message = "User does not exist."


# Coupon Exceptions
class InvalidCouponNumberException(OrderAPPException):
    customer_message = "Coupon number is invalid."


class InvalidCouponStatusException(OrderAPPException):
    customer_message = "Invalid Coupon Status"


# Order Exceptions
class NonExistingOrderException(OrderAPPException):
    customer_message = "Order with this ID does not exist."
