from abc import ABC, abstractmethod


class BaseAccount(ABC):
    """Lớp cơ sở trừu tượng cho tất cả các loại tài khoản.

    Lớp này định nghĩa giao diện bắt buộc cho các hoạt động nạp và rút,
    sử dụng trường số dư riêng tư, và cung cấp các tiện ích chung như
    xác thực tài khoản và quản lý tên ngân hàng.
    """

    bank_name = "Vietcombank"

    def __init__(self, account_number: str, owner_name: str, initial_balance: float = 0.0):
        if not self.validate_account_number(account_number):
            raise ValueError("Account number must be exactly 10 digits.")

        self._account_number = account_number
        self._owner_name = self._normalize_owner_name(owner_name)
        self.__balance = float(initial_balance)

    @property
    def account_number(self) -> str:
        return self._account_number

    @property
    def owner_name(self) -> str:
        return self._owner_name

    @owner_name.setter
    def owner_name(self, new_name: str):
        self._owner_name = self._normalize_owner_name(new_name)

    @staticmethod
    def _normalize_owner_name(name: str) -> str:
        return " ".join(name.strip().upper().split())

    @property
    def balance(self) -> float:
        """Thuộc tính chỉ đọc cho số dư tài khoản.

        Setter được bỏ qua cố ý để đảm bảo số dư chỉ được cập nhật thông qua
        các thao tác nạp hoặc rút tiền.
        """
        return self.__balance

    def _update_balance(self, amount: float) -> None:
        """Hàm trợ giúp nội bộ để điều chỉnh số dư riêng tư một cách an toàn."""
        self.__balance += amount

    @abstractmethod
    def deposit(self, amount: float) -> None:
        """Nạp tiền vào tài khoản."""
        raise NotImplementedError

    @abstractmethod
    def withdraw(self, amount: float) -> None:
        """Rút tiền từ tài khoản."""
        raise NotImplementedError

    def __add__(self, other):
        """Nạp chồng toán tử để cộng số dư của hai tài khoản."""
        if not isinstance(other, BaseAccount):
            return NotImplemented
        return self.balance + other.balance

    def __lt__(self, other):
        """Nạp chồng toán tử để so sánh số dư của hai tài khoản."""
        if not isinstance(other, BaseAccount):
            return NotImplemented
        return self.balance < other.balance

    @staticmethod
    def validate_account_number(account_number: str) -> bool:
        return isinstance(account_number, str) and account_number.isdigit() and len(account_number) == 10

    @classmethod
    def update_bank_name(cls, new_name: str) -> None:
        cls.bank_name = new_name.strip()

    def __str__(self):
        return f"{type(self).__name__}({self.account_number} - {self.owner_name})"


class SavingsAccount(BaseAccount):
    """Tài khoản tiết kiệm hỗ trợ nạp tiền, rút tiền và sinh lãi."""

    def __init__(self, account_number: str, owner_name: str, interest_rate: float = 0.05):
        super().__init__(account_number, owner_name)
        self.interest_rate = float(interest_rate)

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self._update_balance(amount)

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive.")

        penalty = amount * 0.02
        total_withdrawal = amount + penalty
        if total_withdrawal > self.balance:
            raise ValueError("Insufficient balance after penalty.")

        self._update_balance(-total_withdrawal)
        return penalty

    def apply_interest(self) -> float:
        interest_amount = self.balance * self.interest_rate
        self._update_balance(interest_amount)
        return interest_amount


class CreditAccount(BaseAccount):
    """Tài khoản tín dụng cho phép số dư âm trong hạn mức tín dụng."""

    def __init__(self, account_number: str, owner_name: str, credit_limit: float = 20_000_000):
        super().__init__(account_number, owner_name)
        self.credit_limit = float(credit_limit)

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self._update_balance(amount)

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive.")

        projected_balance = self.balance - amount
        if projected_balance < -self.credit_limit:
            raise ValueError("Vượt quá hạn mức thấu chi cho phép")

        self._update_balance(-amount)


class DigitalPremiumMixin:
    """Mixin cung cấp phần thưởng hoàn tiền cho giao dịch trực tuyến cao cấp."""

    def cashback_reward(self, amount: float) -> float:
        if amount > 5_000_000:
            return amount * 0.01
        return 0.0


class HybridAccount(SavingsAccount, DigitalPremiumMixin):
    """Tài khoản đa năng kết hợp tính năng tiết kiệm và hoàn tiền cao cấp."""

    def __init__(self, account_number: str, owner_name: str, interest_rate: float = 0.05):
        super().__init__(account_number, owner_name, interest_rate)

    def deposit(self, amount: float) -> float:
        """Nạp tiền với hoàn tiền cao cấp cho các khoản đủ điều kiện."""
        super().deposit(amount)
        cashback = self.cashback_reward(amount)
        if cashback:
            super().deposit(cashback)
        return cashback


class VNPayGateway:
    def execute_pay(self, account: BaseAccount, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Payment amount must be positive.")
        print(f"[Hệ thống VNPay]: Đang kết nối tới tài khoản {account.account_number}...")
        account.withdraw(amount)
        print("Xác thực thanh toán bằng Duck Typing thành công!")


class ViettelMoneyGateway:
    def execute_pay(self, account: BaseAccount, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Payment amount must be positive.")
        print(f"[Hệ thống Viettel Money]: Đang xử lý thanh toán với tài khoản {account.account_number}...")
        account.withdraw(amount)
        print("Xác thực thanh toán bằng Duck Typing thành công!")


def process_payment(payment_gateway, account: BaseAccount, amount: float) -> None:
    try:
        payment_gateway.execute_pay(account, amount)
    except AttributeError:
        raise AttributeError("Cổng thanh toán không hợp lệ hoặc chưa được tích hợp") from None


def format_currency(value: float) -> str:
    return f"{value:,.0f}"


def parse_decimal_input(prompt_text: str) -> float:
    user_input = input(prompt_text).strip().replace(",", "")
    try:
        value = float(user_input)
    except ValueError:
        raise ValueError("Giá trị phải là một số hợp lệ.")
    if value < 0:
        raise ValueError("Giá trị không được âm.")
    return value


def select_account(accounts: list[BaseAccount]) -> BaseAccount | None:
    if not accounts:
        return None
    print("Danh sách tài khoản:")
    for index, account in enumerate(accounts, start=1):
        print(f"{index}. {account.owner_name} - {account.account_number} ({type(account).__name__}) - Số dư: {format_currency(account.balance)} VND")
    choice = input("Chọn tài khoản theo số thứ tự: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(accounts)):
        raise ValueError("Lựa chọn không hợp lệ.")
    return accounts[int(choice) - 1]


def open_new_account(accounts: list[BaseAccount]) -> BaseAccount:
    print("--- CHỌN LOẠI TÀI KHOẢN ---")
    print("1. Savings Account (Tài khoản Tiết kiệm)")
    print("2. Credit Account (Tài khoản Tín dụng)")
    print("3. Hybrid Account (Tài khoản Đa năng)")
    account_type = input("Chọn loại tài khoản (1-3): ").strip()

    if account_type not in {"1", "2", "3"}:
        raise ValueError("Loại tài khoản không hợp lệ.")

    account_number = input("Nhập số tài khoản 10 chữ số: ").strip()
    if not BaseAccount.validate_account_number(account_number):
        raise ValueError("Số tài khoản không hợp lệ! Phải gồm đúng 10 chữ số.")

    if any(acc.account_number == account_number for acc in accounts):
        raise ValueError("Số tài khoản đã tồn tại trong hệ thống.")

    owner_name = input("Nhập tên chủ tài khoản: ").strip()
    if not owner_name:
        raise ValueError("Tên chủ tài khoản không được để trống.")

    if account_type == "1":
        interest_rate = parse_decimal_input("Nhập lãi suất năm (ví dụ 0.05): ")
        new_account = SavingsAccount(account_number, owner_name, interest_rate)
        print("\nMở tài khoản Tiết kiệm thành công!")
    elif account_type == "2":
        credit_limit = parse_decimal_input("Nhập hạn mức tín dụng (ví dụ 20000000): ")
        new_account = CreditAccount(account_number, owner_name, credit_limit)
        print("\nMở tài khoản Tín dụng thành công!")
    else:
        interest_rate = parse_decimal_input("Nhập lãi suất năm (ví dụ 0.05): ")
        new_account = HybridAccount(account_number, owner_name, interest_rate)
        print("\nMở tài khoản Hybrid thành công!")

    print(f"Chủ tài khoản: {new_account.owner_name}")
    accounts.append(new_account)
    return new_account


def display_account_info(account: BaseAccount) -> None:
    print("--- THÔNG TIN TÀI KHOẢN HIỆN TẠI ---")
    print(f"Loại tài khoản: {type(account).__name__}")
    print(f"Ngân hàng: {account.bank_name}")
    print(f"Số tài khoản: {account.account_number}")
    print(f"Chủ tài khoản: {account.owner_name}")
    print(f"Số dư: {format_currency(account.balance)} VND")
    if isinstance(account, SavingsAccount):
        print(f"Lãi suất: {account.interest_rate * 100:.1f}% / năm")
    print("MRO:")
    for item in type(account).mro():
        print(f"- {item.__name__}")


def perform_transaction(account: BaseAccount) -> None:
    print("--- GIAO DỊCH NẠP / RÚT TIỀN ---")
    print("1. Nạp tiền")
    print("2. Rút tiền")
    transaction_choice = input("Chọn giao dịch (1-2): ").strip()
    if transaction_choice not in {"1", "2"}:
        raise ValueError("Lựa chọn giao dịch không hợp lệ.")

    amount = parse_decimal_input("Nhập số tiền cần xử lý: ")

    if transaction_choice == "1":
        cashback_message = ""
        if isinstance(account, HybridAccount):
            cashback = account.deposit(amount)
            if cashback > 0:
                cashback_message = f"[Ưu đãi Premium]: Bạn được hoàn tiền 1% ({format_currency(cashback)} VND) vào tài khoản!\n"
        else:
            account.deposit(amount)
        print("Nạp tiền thành công!")
        if cashback_message:
            print(cashback_message, end="")
        print(f"Số dư mới: {format_currency(account.balance)} VND")
    else:
        if isinstance(account, SavingsAccount):
            penalty = account.withdraw(amount)
            print("Rút tiền thành công!")
            print(f"Số tiền rút: {format_currency(amount)} VND")
            print(f"Phí phạt rút trước hạn (2%): {format_currency(penalty)} VND")
            print(f"Số dư còn lại: {format_currency(account.balance)} VND")
        else:
            account.withdraw(amount)
            print("Rút tiền thành công!")
            print(f"Số tiền rút: {format_currency(amount)} VND")
            if isinstance(account, CreditAccount):
                print("(Sử dụng hạn mức thấu chi)")
            print(f"Số dư hiện tại: {format_currency(account.balance)} VND")


def apply_interest_to_account(account: BaseAccount) -> None:
    print("--- TÍNH LÃI ĐỊNH KỲ ---")
    if not hasattr(account, "apply_interest"):
        print("Tài khoản hiện tại không hỗ trợ tính lãi suất định kỳ.")
        return
    if isinstance(account, CreditAccount):
        print("Tài khoản tín dụng không hỗ trợ tính lãi suất tích lũy.")
        return

    print(f"Số dư trước tính lãi: {format_currency(account.balance)} VND")
    print(f"Lãi suất năm: {account.interest_rate * 100:.1f}%")
    interest_amount = account.apply_interest()
    print(f"Tiền lãi nhận được: +{format_currency(interest_amount)} VND")
    print(f"Số dư mới sau khi cộng lãi: {format_currency(account.balance)} VND")


def compare_or_combine_accounts(current_account: BaseAccount, accounts: list[BaseAccount]) -> None:
    print("--- ĐỒNG BỘ & SO SÁNH TÀI KHOẢN (OPERATOR OVERLOADING) ---")
    if len(accounts) < 2:
        print("Cần ít nhất 2 tài khoản trong hệ thống để so sánh hoặc gộp.")
        return

    print(f"Tài khoản hiện tại (A): {current_account.owner_name} (Số dư: {format_currency(current_account.balance)} VND)")
    other_account = select_account([acc for acc in accounts if acc is not current_account])
    if other_account is None:
        raise ValueError("Không có tài khoản đối ứng được chọn.")

    comparison = "NHỎ HƠN" if current_account < other_account else "LỚN HƠN hoặc BẰNG"
    total_balance = current_account + other_account
    print(f"[Kết quả So sánh (__lt__)]: Số dư tài khoản A {comparison} số dư tài khoản B.")
    print(f"[Kết quả Tổng hợp (__add__)]: Tổng số tiền sở hữu của cả 2 tài khoản là: {format_currency(total_balance)} VND.")


def payment_gateway_menu() -> object:
    print("--- THANH TOÁN HÓA ĐƠN QUA CỔNG TRUNG GIAN ---")
    print("1. Thanh toán qua VNPay")
    print("2. Thanh toán qua Viettel Money")
    choice = input("Chọn cổng thanh toán (1-2): ").strip()
    if choice == "1":
        return VNPayGateway()
    if choice == "2":
        return ViettelMoneyGateway()
    raise ValueError("Lựa chọn cổng thanh toán không hợp lệ.")


def checkout_bill(account: BaseAccount) -> None:
    gateway = payment_gateway_menu()
    amount = parse_decimal_input("Nhập số tiền hóa đơn: ")
    process_payment(gateway, account, amount)
    print(f"Tài khoản đã thanh toán hóa đơn giá trị: {format_currency(amount)} VND.")
    print(f"Số dư mới: {format_currency(account.balance)} VND.")


def main() -> None:
    accounts: list[BaseAccount] = []
    current_account: BaseAccount | None = None

    while True:
        print("\n===== VIETCOMBANK DIGIBANK PRO SIMULATOR =====")
        print("1. Mở tài khoản mới (Chọn loại tài khoản)")
        print("2. Xem thông tin & Kiểm tra thứ tự kế thừa (MRO)")
        print("3. Giao dịch Nạp / Rút tiền & Tính điểm thưởng (Đa hình)")
        print("4. Tích lũy / Áp dụng lãi suất định kỳ")
        print("5. Kiểm tra tính năng gộp tài khoản & So sánh (Overloading)")
        print("6. Thanh toán hóa đơn qua Cổng trung gian (Duck Typing)")
        print("7. Thoát chương trình")
        print("==============================================")

        choice = input("Chọn chức năng (1-7): ").strip()

        try:
            if choice == "1":
                current_account = open_new_account(accounts)
            elif choice == "2":
                if current_account is None:
                    print("Hệ thống chưa có thông tin tài khoản. Vui lòng mở tài khoản ở Chức năng 1 trước.")
                else:
                    display_account_info(current_account)
            elif choice == "3":
                if current_account is None:
                    print("Hệ thống chưa có tài khoản hoạt động. Vui lòng mở tài khoản trước.")
                else:
                    perform_transaction(current_account)
            elif choice == "4":
                if current_account is None:
                    print("Hệ thống chưa có tài khoản hoạt động. Vui lòng mở tài khoản trước.")
                else:
                    apply_interest_to_account(current_account)
            elif choice == "5":
                if current_account is None:
                    print("Hệ thống chưa có tài khoản hoạt động. Vui lòng mở tài khoản trước.")
                else:
                    compare_or_combine_accounts(current_account, accounts)
            elif choice == "6":
                if current_account is None:
                    print("Hệ thống chưa có tài khoản hoạt động. Vui lòng mở tài khoản trước.")
                else:
                    checkout_bill(current_account)
            elif choice == "7":
                print("Cảm ơn đã trải nghiệm hệ thống Vietcombank Digibank Pro Simulator!")
                break
            else:
                print("Lựa chọn không hợp lệ. Vui lòng chọn số từ 1 đến 7.")
        except ValueError as error:
            print(error)
        except AttributeError as error:
            print(error)
        except TypeError as error:
            print(error)
        except Exception as error:
            print(f"Đã xảy ra lỗi không mong muốn: {error}")


if __name__ == "__main__":
    main()
