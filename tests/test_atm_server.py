import unittest

from sim.atm_server import (
    build_testbench,
    run_verilog_simulation,
)


class TestAtmServer(unittest.TestCase):

    def test_build_testbench(self):
        tb = build_testbench([
            {"kind": "insert_card", "account": 0x1234},
            {"kind": "enter_pin", "pin": 9},
            {"kind": "select_balance"},
        ])

        self.assertIn("atm_fsm dut", tb)
        self.assertIn("RESULT", tb)

    def test_balance_enquiry(self):
        result = run_verilog_simulation([
            {"kind": "insert_card", "account": 0x1234},
            {"kind": "enter_pin", "pin": 9},
            {"kind": "select_balance"},
        ])

        self.assertTrue(result["ok"])
        self.assertEqual(result["balance"], 250)
        self.assertFalse(result["locked"])
        self.assertFalse(result["auth_error"])


if __name__ == "__main__":
    unittest.main()
