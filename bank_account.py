"""
bank_account.py

Personal bank account management module.

Contains two classes:
    * Amount          - a single transaction (deposit or withdrawal).
    * PersonalAccount - a bank account that stores its balance and
                        a history of Amount objects.
"""

from datetime import datetime


class Amount:
    """Represents a single transaction amount.

    Attributes:
        amount (float): The transaction amount (always positive).
        timestamp (datetime): Date and time of the transaction.
        transaction_type (str): 'DEPOSIT' or 'WITHDRAWAL'.
    """

    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    VALID_TYPES = (DEPOSIT, WITHDRAWAL)

    def __init__(self, amount, transaction_type, timestamp=None):
        """Create a new transaction.

        Args:
            amount (float): Positive transaction amount.
            transaction_type (str): 'DEPOSIT' or 'WITHDRAWAL'.
            timestamp (datetime, optional): Transaction time.
                Defaults to the current date and time.

        Raises:
            TypeError: If amount is not a number.
            ValueError: If amount is not positive or the type is invalid.
        """
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("Amount must be a number.")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        transaction_type = str(transaction_type).upper()
        if transaction_type not in self.VALID_TYPES:
            raise ValueError(
                f"Transaction type must be one of {self.VALID_TYPES}."
            )

        self.amount = float(amount)
        self.timestamp = timestamp if timestamp is not None else datetime.now()
        self.transaction_type = transaction_type

    def __str__(self):
        """Readable representation, e.g.
        '2026-11-16 13:45:02 | DEPOSIT    |     500.00'
        """
        return (
            f"{self.timestamp:%Y-%m-%d %H:%M:%S} | "
            f"{self.transaction_type:<10} | {self.amount:>10.2f}"
        )

    def __repr__(self):
        return (
            f"Amount(amount={self.amount!r}, "
            f"transaction_type={self.transaction_type!r}, "
            f"timestamp={self.timestamp!r})"
        )


class PersonalAccount:
    """Represents a personal bank account.

    Attributes:
        account_number (int): Unique account identifier.
        account_holder (str): Name of the account holder.
        balance (float): Current balance (starts at 0.0).
        transactions (list[Amount]): History of all transactions.
    """

    def __init__(self, account_number, account_holder):
        """Create an account with a zero balance and empty history."""
        self.set_account_number(account_number)
        self.set_account_holder(account_holder)
        self._balance = 0.0
        self._transactions = []

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------
    def deposit(self, amount):
        """Deposit money into the account.

        Creates an Amount object of type 'DEPOSIT', stores it in the
        transaction history and increases the balance.

        Args:
            amount (float): Positive amount to deposit.

        Returns:
            Amount: The created transaction.

        Raises:
            TypeError / ValueError: If the amount is invalid.
        """
        transaction = Amount(amount, Amount.DEPOSIT)
        self._transactions.append(transaction)
        self._balance += transaction.amount
        return transaction

    def withdraw(self, amount):
        """Withdraw money from the account.

        Creates an Amount object of type 'WITHDRAWAL', stores it in the
        transaction history and decreases the balance.

        Args:
            amount (float): Positive amount to withdraw.

        Returns:
            Amount: The created transaction.

        Raises:
            TypeError / ValueError: If the amount is invalid.
            ValueError: If the amount exceeds the current balance
                (balance and history stay unchanged).
        """
        transaction = Amount(amount, Amount.WITHDRAWAL)
        if transaction.amount > self._balance:
            raise ValueError(
                f"Insufficient funds: balance is {self._balance:.2f}, "
                f"requested {transaction.amount:.2f}."
            )
        self._transactions.append(transaction)
        self._balance -= transaction.amount
        return transaction

    def print_transaction_history(self):
        """Print every transaction (date, type and amount)."""
        print(f"Transaction history for account #{self._account_number} "
              f"({self._account_holder}):")
        if not self._transactions:
            print("  No transactions yet.")
            return
        print(f"  {'Date/Time':<19} | {'Type':<10} | {'Amount':>10}")
        print("  " + "-" * 45)
        for transaction in self._transactions:
            print(f"  {transaction}")
        print("  " + "-" * 45)
        print(f"  {'Current balance':<32} {self._balance:>10.2f}")

    # ------------------------------------------------------------------
    # Getters / setters
    # ------------------------------------------------------------------
    def get_balance(self):
        """Return the current balance."""
        return self._balance

    def get_transactions(self):
        """Return a copy of the transaction list."""
        return list(self._transactions)

    def get_account_number(self):
        """Return the account number."""
        return self._account_number

    def set_account_number(self, account_number):
        """Set the account number (must be a positive integer)."""
        if isinstance(account_number, bool) or not isinstance(account_number, int):
            raise TypeError("Account number must be an integer.")
        if account_number <= 0:
            raise ValueError("Account number must be positive.")
        self._account_number = account_number

    def get_account_holder(self):
        """Return the account holder's name."""
        return self._account_holder

    def set_account_holder(self, account_holder):
        """Set the account holder's name (non-empty string)."""
        if not isinstance(account_holder, str) or not account_holder.strip():
            raise ValueError("Account holder must be a non-empty string.")
        self._account_holder = account_holder.strip()

    # Read-only properties so the attributes from the assignment are
    # accessible as account.balance / account.transactions etc.
    @property
    def balance(self):
        return self._balance

    @property
    def transactions(self):
        return list(self._transactions)

    @property
    def account_number(self):
        return self._account_number

    @property
    def account_holder(self):
        return self._account_holder

    # ------------------------------------------------------------------
    # Magic methods
    # ------------------------------------------------------------------
    def __str__(self):
        return (
            f"Account #{self._account_number} | "
            f"Holder: {self._account_holder} | "
            f"Balance: {self._balance:.2f} | "
            f"Transactions: {len(self._transactions)}"
        )

    def __repr__(self):
        return (
            f"PersonalAccount(account_number={self._account_number!r}, "
            f"account_holder={self._account_holder!r})"
        )

    def __add__(self, amount):
        """account + 100  ->  same as account.deposit(100).
        Returns the account itself, so `account = account + 100` works.
        """
        self.deposit(amount)
        return self

    def __sub__(self, amount):
        """account - 50  ->  same as account.withdraw(50).
        Returns the account itself, so `account = account - 50` works.
        """
        self.withdraw(amount)
        return self
