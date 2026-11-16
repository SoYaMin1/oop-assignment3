"""
main.py

Interactive demo of the PersonalAccount class (sample test with user inputs).

Run:
    python main.py          # interactive menu
    python main.py --demo   # automatic demo without input
"""

import sys

from bank_account import PersonalAccount


def read_float(prompt):
    """Ask the user for a number until a valid one is entered."""
    while True:
        raw = input(prompt).strip().replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            print("  Please enter a number, e.g. 150.50")


def read_int(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("  Please enter a whole number.")


def create_account():
    print("=== Create a new account ===")
    while True:
        try:
            number = read_int("Account number: ")
            holder = input("Account holder name: ")
            return PersonalAccount(number, holder)
        except (TypeError, ValueError) as error:
            print(f"  Error: {error}")


def interactive():
    account = create_account()
    print(f"\nCreated: {account}\n")

    menu = (
        "\nChoose an action:\n"
        "  1 - Deposit\n"
        "  2 - Withdraw\n"
        "  3 - Check balance\n"
        "  4 - Print transaction history\n"
        "  5 - Show account info\n"
        "  6 - Change account holder\n"
        "  0 - Exit"
    )

    while True:
        print(menu)
        choice = input("> ").strip()
        try:
            if choice == "1":
                amount = read_float("Amount to deposit: ")
                account.deposit(amount)
                print(f"  Deposited {amount:.2f}. Balance: {account.get_balance():.2f}")
            elif choice == "2":
                amount = read_float("Amount to withdraw: ")
                account.withdraw(amount)
                print(f"  Withdrew {amount:.2f}. Balance: {account.get_balance():.2f}")
            elif choice == "3":
                print(f"  Current balance: {account.get_balance():.2f}")
            elif choice == "4":
                account.print_transaction_history()
            elif choice == "5":
                print(f"  {account}")
            elif choice == "6":
                account.set_account_holder(input("New holder name: "))
                print(f"  Holder changed to {account.get_account_holder()}")
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("  Unknown option.")
        except (TypeError, ValueError) as error:
            print(f"  Error: {error}")


def demo():
    """Non-interactive demonstration of all features."""
    account = PersonalAccount(1001, "Aidar Baktybekov")
    print(account)

    print("\n1. Deposit 1000 and 250.50")
    account.deposit(1000)
    account.deposit(250.50)

    print("2. Withdraw 300")
    account.withdraw(300)

    print("3. Operators: account + 100, account - 50")
    account = account + 100
    account = account - 50

    print("4. Try to withdraw 5000 (more than balance)")
    try:
        account.withdraw(5000)
    except ValueError as error:
        print(f"   Rejected: {error}")

    print(f"\nBalance: {account.get_balance():.2f}\n")
    account.print_transaction_history()
    print(f"\n{account}")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        interactive()
