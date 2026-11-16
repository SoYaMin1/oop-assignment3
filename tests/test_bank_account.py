"""Run from the project root:
    python -m unittest discover -s tests -v
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bank_account import Amount, PersonalAccount  # noqa: E402


class TestAmount(unittest.TestCase):

    def test_create_deposit(self):
        a = Amount(100, "DEPOSIT")
        self.assertEqual(a.amount, 100.0)
        self.assertIsInstance(a.amount, float)
        self.assertEqual(a.transaction_type, "DEPOSIT")
        self.assertIsInstance(a.timestamp, datetime)

    def test_type_is_case_insensitive(self):
        self.assertEqual(Amount(5, "withdrawal").transaction_type, "WITHDRAWAL")

    def test_custom_timestamp(self):
        ts = datetime(2026, 1, 1, 12, 0, 0)
        self.assertEqual(Amount(10, "DEPOSIT", ts).timestamp, ts)

    def test_invalid_type(self):
        with self.assertRaises(ValueError):
            Amount(10, "TRANSFER")

    def test_zero_and_negative_amount(self):
        with self.assertRaises(ValueError):
            Amount(0, "DEPOSIT")
        with self.assertRaises(ValueError):
            Amount(-5, "DEPOSIT")

    def test_non_numeric_amount(self):
        with self.assertRaises(TypeError):
            Amount("100", "DEPOSIT")
        with self.assertRaises(TypeError):
            Amount(True, "DEPOSIT")

    def test_str(self):
        ts = datetime(2026, 11, 16, 13, 45, 0)
        text = str(Amount(250.5, "DEPOSIT", ts))
        self.assertIn("2026-11-16 13:45:00", text)
        self.assertIn("DEPOSIT", text)
        self.assertIn("250.50", text)


class TestPersonalAccount(unittest.TestCase):

    def setUp(self):
        self.account = PersonalAccount(1001, "Aidar")

    # --- creation -----------------------------------------------------
    def test_initial_state(self):
        self.assertEqual(self.account.get_balance(), 0.0)
        self.assertEqual(self.account.get_account_number(), 1001)
        self.assertEqual(self.account.get_account_holder(), "Aidar")
        self.assertEqual(self.account.transactions, [])

    def test_invalid_constructor_args(self):
        with self.assertRaises(TypeError):
            PersonalAccount("abc", "Aidar")
        with self.assertRaises(ValueError):
            PersonalAccount(-1, "Aidar")
        with self.assertRaises(ValueError):
            PersonalAccount(1, "   ")

    # --- deposit ------------------------------------------------------
    def test_deposit_updates_balance_and_history(self):
        self.account.deposit(500)
        self.assertEqual(self.account.get_balance(), 500.0)
        self.assertEqual(len(self.account.transactions), 1)
        t = self.account.transactions[0]
        self.assertIsInstance(t, Amount)
        self.assertEqual(t.transaction_type, "DEPOSIT")
        self.assertEqual(t.amount, 500.0)

    def test_multiple_deposits(self):
        for value in (100, 200.25, 0.75):
            self.account.deposit(value)
        self.assertAlmostEqual(self.account.get_balance(), 301.0)
        self.assertEqual(len(self.account.transactions), 3)

    def test_invalid_deposit_changes_nothing(self):
        with self.assertRaises(ValueError):
            self.account.deposit(-100)
        with self.assertRaises(ValueError):
            self.account.deposit(0)
        self.assertEqual(self.account.get_balance(), 0.0)
        self.assertEqual(self.account.transactions, [])

    # --- withdraw -----------------------------------------------------
    def test_withdraw_updates_balance_and_history(self):
        self.account.deposit(1000)
        self.account.withdraw(400)
        self.assertEqual(self.account.get_balance(), 600.0)
        last = self.account.transactions[-1]
        self.assertEqual(last.transaction_type, "WITHDRAWAL")
        self.assertEqual(last.amount, 400.0)

    def test_withdraw_entire_balance(self):
        self.account.deposit(250)
        self.account.withdraw(250)
        self.assertEqual(self.account.get_balance(), 0.0)

    def test_withdraw_more_than_balance(self):
        self.account.deposit(100)
        with self.assertRaises(ValueError):
            self.account.withdraw(100.01)
        self.assertEqual(self.account.get_balance(), 100.0)
        self.assertEqual(len(self.account.transactions), 1)

    def test_withdraw_from_empty_account(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(1)

    def test_invalid_withdraw_amount(self):
        self.account.deposit(100)
        with self.assertRaises(ValueError):
            self.account.withdraw(-10)
        self.assertEqual(self.account.get_balance(), 100.0)

    # --- operators ----------------------------------------------------
    def test_add_operator(self):
        result = self.account + 300
        self.assertIs(result, self.account)
        self.assertEqual(self.account.get_balance(), 300.0)
        self.assertEqual(self.account.transactions[-1].transaction_type, "DEPOSIT")

    def test_sub_operator(self):
        self.account + 300
        self.account = self.account - 120
        self.assertEqual(self.account.get_balance(), 180.0)
        self.assertEqual(self.account.transactions[-1].transaction_type, "WITHDRAWAL")

    def test_sub_operator_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account - 1

    def test_inplace_operators(self):
        acc = self.account
        acc += 50
        acc -= 20
        self.assertIs(acc, self.account)
        self.assertEqual(acc.get_balance(), 30.0)

    # --- getters / setters --------------------------------------------
    def test_setters(self):
        self.account.set_account_number(2002)
        self.account.set_account_holder("Bakyt")
        self.assertEqual(self.account.get_account_number(), 2002)
        self.assertEqual(self.account.get_account_holder(), "Bakyt")

    def test_invalid_setters(self):
        with self.assertRaises(TypeError):
            self.account.set_account_number(12.5)
        with self.assertRaises(ValueError):
            self.account.set_account_holder("")

    def test_balance_is_encapsulated(self):
        with self.assertRaises(AttributeError):
            self.account.balance = 1_000_000
        self.account.transactions.append("fake")
        self.assertEqual(self.account.transactions, [])

    # --- output -------------------------------------------------------
    def test_str(self):
        self.account.deposit(99.5)
        text = str(self.account)
        self.assertIn("1001", text)
        self.assertIn("Aidar", text)
        self.assertIn("99.50", text)

    def test_print_transaction_history(self):
        self.account.deposit(1000)
        self.account.withdraw(250)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.account.print_transaction_history()
        output = buffer.getvalue()
        self.assertIn("DEPOSIT", output)
        self.assertIn("WITHDRAWAL", output)
        self.assertIn("1000.00", output)
        self.assertIn("250.00", output)
        self.assertIn("750.00", output)

    def test_print_empty_history(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.account.print_transaction_history()
        self.assertIn("No transactions", buffer.getvalue())

    # --- full scenario ------------------------------------------------
    def test_full_scenario(self):
        self.account.deposit(1000)
        self.account.withdraw(200)
        self.account + 500
        self.account - 300
        with self.assertRaises(ValueError):
            self.account.withdraw(10_000)
        self.assertEqual(self.account.get_balance(), 1000.0)
        types = [t.transaction_type for t in self.account.transactions]
        self.assertEqual(types, ["DEPOSIT", "WITHDRAWAL", "DEPOSIT", "WITHDRAWAL"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
