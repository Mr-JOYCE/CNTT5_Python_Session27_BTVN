from abc import ABC, abstractmethod


# =====================================================
# ABSTRACT BASE CLASS
# =====================================================

class BaseProduct(ABC):
    """
    Lớp trừu tượng định nghĩa bộ khung chuẩn
    cho tất cả sản phẩm trong kho.
    """

    warehouse_name = "Amazon Logistics"
    base_storage_fee = 5000

    def __init__(self, product_code, product_name):
        self.product_code = product_code

        self.__stock_quantity = 0

        self.product_name = product_name

    # -------------------------------------------------
    # PROPERTY
    # -------------------------------------------------

    @property
    def stock_quantity(self):
        """
        Chỉ cho đọc tồn kho.
        Không cho phép gán trực tiếp.
        """
        return self.__stock_quantity

    def _update_stock(self, quantity):
        """
        Internal method để cập nhật tồn kho.
        """
        self.__stock_quantity = quantity

    # -------------------------------------------------
    # PROPERTY + SETTER
    # -------------------------------------------------

    @property
    def product_name(self):
        return self._product_name

    @product_name.setter
    def product_name(self, value):
        """
        Chuẩn hóa tên sản phẩm:
        - bỏ khoảng trắng thừa
        - in hoa
        """
        self._product_name = " ".join(
            value.strip().upper().split()
        )

    # -------------------------------------------------
    # ABSTRACT METHODS
    # -------------------------------------------------

    @abstractmethod
    def import_stock(self, quantity):
        pass

    @abstractmethod
    def export_stock(self, quantity):
        pass

    # -------------------------------------------------
    # OPERATOR OVERLOADING
    # -------------------------------------------------

    def __add__(self, other):

        if not isinstance(other, BaseProduct):
            return NotImplemented

        return self.stock_quantity + other.stock_quantity

    def __lt__(self, other):

        if not isinstance(other, BaseProduct):
            return NotImplemented

        return self.stock_quantity < other.stock_quantity

    # -------------------------------------------------
    # STATIC METHOD
    # -------------------------------------------------

    @staticmethod
    def validate_product_code(product_code):
        """
        Bắt đầu bằng chữ
        Đúng 10 ký tự
        """

        if len(product_code) != 10:
            return False

        return product_code[0].isalpha()

    # -------------------------------------------------
    # CLASS METHOD
    # -------------------------------------------------

    @classmethod
    def update_warehouse_name(cls, new_name):
        cls.warehouse_name = new_name


# =====================================================
# COLD STORAGE PRODUCT
# =====================================================

class ColdStorageProduct(BaseProduct):

    def __init__(
            self,
            product_code,
            product_name,
            required_temperature
    ):
        super().__init__(
            product_code,
            product_name
        )

        self.required_temperature = required_temperature

    def import_stock(self, quantity):

        self._update_stock(
            self.stock_quantity + quantity
        )

        print("Nhập kho thành công!")

    def export_stock(self, quantity):

        loss = quantity * 0.05

        total = quantity + loss

        if total > self.stock_quantity:
            print("Không đủ tồn kho!")
            return

        self._update_stock(
            self.stock_quantity - total
        )

        print("Xuất kho thành công!")
        print(f"Số lượng yêu cầu: {quantity}")
        print(f"Hao hụt 5%: {loss}")
        print(f"Tổng khấu trừ: {total}")

    def apply_cooling_cost(self):

        cost = self.stock_quantity * 3000

        print(
            f"Chi phí làm lạnh: "
            f"{cost:,.0f} VND"
        )


# =====================================================
# HAZARDOUS PRODUCT
# =====================================================

class HazardousProduct(BaseProduct):

    def __init__(
            self,
            product_code,
            product_name,
            max_safety_limit
    ):
        super().__init__(
            product_code,
            product_name
        )

        self.max_safety_limit = max_safety_limit

    def import_stock(self, quantity):

        future_stock = (
                self.stock_quantity + quantity
        )

        if future_stock > self.max_safety_limit:

            print(
                "Giao dịch thất bại!"
            )
            print(
                f"Vượt hạn mức "
                f"{self.max_safety_limit}"
            )
            return

        self._update_stock(future_stock)

        print("Nhập kho thành công!")

    def export_stock(self, quantity):

        if quantity > self.stock_quantity:
            print("Không đủ tồn kho!")
            return

        self._update_stock(
            self.stock_quantity - quantity
        )

        print("Xuất kho thành công!")


# =====================================================
# HYBRID PREMIUM PRODUCT
# =====================================================

class HybridPremiumProduct(
    ColdStorageProduct,
    HazardousProduct
):

    def __init__(
            self,
            product_code,
            product_name,
            required_temperature,
            max_safety_limit
    ):

        BaseProduct.__init__(
            self,
            product_code,
            product_name
        )

        self.required_temperature = (
            required_temperature
        )

        self.max_safety_limit = (
            max_safety_limit
        )

    def import_stock(self, quantity):

        future_stock = (
                self.stock_quantity + quantity
        )

        if future_stock > self.max_safety_limit:

            print(
                "Giao dịch thất bại!"
            )

            print(
                f"Vượt hạn mức "
                f"{self.max_safety_limit}"
            )

            return

        self._update_stock(future_stock)

        print("Nhập kho thành công!")

    def export_stock(self, quantity):

        loss = quantity * 0.05

        total = quantity + loss

        if total > self.stock_quantity:
            print("Không đủ tồn kho!")
            return

        self._update_stock(
            self.stock_quantity - total
        )

        print("Xuất kho thành công!")
        print(f"Hao hụt: {loss}")


# =====================================================
# DUCK TYPING
# =====================================================

class FedExCarrier:

    def ship_package(
            self,
            product,
            quantity
    ):

        print(
            f"[FedEx] Tiếp nhận "
            f"{product.product_code}"
        )


class DHLCarrier:

    def ship_package(
            self,
            product,
            quantity
    ):

        print(
            f"[DHL] Tiếp nhận "
            f"{product.product_code}"
        )


def dispatch_to_carrier(
        carrier_agent,
        product,
        quantity
):

    try:

        carrier_agent.ship_package(
            product,
            quantity
        )

        product.export_stock(quantity)

        print(
            "Duck Typing thành công!"
        )

    except AttributeError:

        print(
            "Đơn vị vận chuyển "
            "không hợp lệ hoặc "
            "chưa ký kết hợp đồng kỹ thuật"
        )


# =====================================================
# MENU
# =====================================================

products = []
current_product = None

while True:

    print("\n===== AMAZON INVENTORY SIMULATOR PRO =====")
    print("1. Đăng ký sản phẩm")
    print("2. Xem thông tin & MRO")
    print("3. Nhập / Xuất kho")
    print("4. Tính phí làm lạnh")
    print("5. Overloading")
    print("6. Duck Typing")
    print("7. Thoát")

    choice = input("Chọn: ")

    if choice == "1":

        print("\n1. Cold")
        print("2. Hazardous")
        print("3. Hybrid")

        product_type = input("Chọn: ")

        code = input(
            "Nhập mã sản phẩm: "
        )

        if not BaseProduct.validate_product_code(
                code
        ):
            print(
                "Mã sản phẩm không hợp lệ!"
            )
            continue

        name = input(
            "Nhập tên sản phẩm: "
        )

        if product_type == "1":

            temp = float(
                input("Nhiệt độ: ")
            )

            current_product = (
                ColdStorageProduct(
                    code,
                    name,
                    temp
                )
            )

        elif product_type == "2":

            limit = int(
                input(
                    "Hạn mức an toàn: "
                )
            )

            current_product = (
                HazardousProduct(
                    code,
                    name,
                    limit
                )
            )

        elif product_type == "3":

            temp = float(
                input("Nhiệt độ: ")
            )

            limit = int(
                input(
                    "Hạn mức an toàn: "
                )
            )

            current_product = (
                HybridPremiumProduct(
                    code,
                    name,
                    temp,
                    limit
                )
            )

        products.append(
            current_product
        )

        print(
            "Đăng ký thành công!"
        )

    elif choice == "2":

        if current_product is None:
            print(
                "Chưa có sản phẩm!"
            )
            continue

        print("\nLoại:",
              type(current_product).__name__)

        print(
            "Mã:",
            current_product.product_code
        )

        print(
            "Tên:",
            current_product.product_name
        )

        print(
            "Tồn kho:",
            current_product.stock_quantity
        )

        print("\nMRO:")

        for cls in type(
                current_product
        ).mro():
            print(cls.__name__)

    elif choice == "3":

        if current_product is None:
            print("Chưa có sản phẩm!")
            continue

        print("1. Nhập")
        print("2. Xuất")

        action = input("Chọn: ")

        quantity = float(
            input("Số lượng: ")
        )

        if action == "1":
            current_product.import_stock(
                quantity
            )

        else:
            current_product.export_stock(
                quantity
            )

    elif choice == "4":

        if isinstance(
                current_product,
                ColdStorageProduct
        ):
            current_product.apply_cooling_cost()

        else:
            print(
                "Không hỗ trợ!"
            )

    elif choice == "5":

        if len(products) < 2:

            print(
                "Cần ít nhất "
                "2 sản phẩm!"
            )

            continue

        other = products[0]

        if other == current_product:
            other = products[1]

        try:

            print(
                "So sánh:",
                current_product < other
            )

            print(
                "Tổng tồn:",
                current_product + other
            )

        except TypeError:

            print(
                "Lỗi overloading!"
            )

    elif choice == "6":

        if current_product is None:
            print("Chưa có sản phẩm!")
            continue

        print("1. FedEx")
        print("2. DHL")

        partner = input("Chọn: ")

        qty = float(
            input(
                "Số lượng giao: "
            )
        )

        carrier = (
            FedExCarrier()
            if partner == "1"
            else DHLCarrier()
        )

        dispatch_to_carrier(
            carrier,
            current_product,
            qty
        )

    elif choice == "7":

        print(
            "\nCảm ơn đã sử dụng "
            "Amazon Inventory Simulator Pro!"
        )

        break

    else:
        print("Lựa chọn không hợp lệ!")