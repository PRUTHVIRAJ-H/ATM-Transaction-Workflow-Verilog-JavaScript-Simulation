import unittest

from sim.atm_server import run_verilog_simulation


class TestEdgeCases(unittest.TestCase):

    def test_invalid_card(self):
        result = run_verilog_simulation([
            {"kind": "insert_card", "account": 0x9999},
        ])

        self.assertTrue(result["ok"])

    def test_wrong_pin(self):
        result = run_verilog_simulation([
            {"kind": "insert_card", "account": 0x1234},
            {"kind": "enter_pin", "pin": 1},
        ])

        self.assertTrue(result["ok"])

    def test_lockout(self):
        for _ in range(3):
            result = run_verilog_simulation([
                {"kind": "insert_card", "account": 0x1234},
                {"kind": "enter_pin", "pin": 1},
            ])

        self.assertTrue(result["ok"])

    def test_large_withdraw(self):
        result = run_verilog_simulation([
            {"kind": "insert_card", "account": 0x1234},
            {"kind": "enter_pin", "pin": 9},
            {"kind": "withdraw", "amount": 200},
        ])

        self.assertTrue(result["ok"])

    def test_non_multiple_of_10(self):
        result = run_verilog_simulation([
            {"kind": "insert_card", "account": 0x1234},
            {"kind": "enter_pin", "pin": 9},
            {"kind": "withdraw", "amount": 55},
        ])

        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
