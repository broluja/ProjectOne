from uuid import uuid4

from models.base_class import BaseClass
from app_exceptions.exceptions import *
from utils import mprint


class Coupon(BaseClass):
    """Model for a coupon."""
    filename = "files/coupons.txt"

    def __init__(self, value=None, is_used=False):
        self.__value = str(uuid4()) if value is None else value
        self.__is_used = is_used
        self.record()

    def __repr__(self):
        return f"{self.value}"

    @property
    def value(self):
        return self.__value

    @property
    def is_used(self):
        return self.__is_used

    @is_used.setter
    def is_used(self, value):
        if not isinstance(value, bool):
            raise InvalidCouponStatusException
        self.__is_used = value

    @classmethod
    def get_status(cls, value) -> bool:
        """
        Get status of coupon.
        :param value: coupon value
        :return: bool.
        """
        coupons = cls.read(cls.filename)
        try:
            return coupons[value].get("used", False)
        except KeyError as exc:
            raise InvalidCouponNumberException from exc

    @classmethod
    def create_coupon_object(cls, value) -> "Coupon":
        """
        Create Coupon instance.
        :param value: coupon value.
        :return:
        """
        coupons = cls.read(cls.filename)
        for coupon in coupons:
            if coupon == value:
                used = coupons[coupon].get("used", False)
                return Coupon(value=value, is_used=used)

    @classmethod
    def refund_coupon(cls, value) -> None:
        """
        Set coupon status to default when user cancel order, and he used coupon.
        Param value: coupon number.
        Return: None.
        """
        coupons = cls.read(cls.filename)
        try:
            coupons[value]["used"] = False
            cls.write(coupons, cls.filename)
        except KeyError as exc:
            raise InvalidCouponNumberException from exc

    def use_coupon(self) -> None:
        """
        Change coupon status and save it to file.
        :return: None.
        """
        try:
            self.is_used = True
            self.record()
        except OrderAPPException as e:
            mprint(e.__str__())

    def record(self) -> None:
        """
        Save a coupon to file.
        :return: None.
        """
        coupons = self.read(self.filename)
        coupons[self.value] = {"used": self.is_used}
        self.write(coupons, self.filename)
