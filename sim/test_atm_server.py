import os
import subprocess
import tempfile
import unittest

from sim.atm_server import build_testbench, run_verilog_simulation


class AtmServerTests(unittest.TestCase):
    def test_build_testbench_contains_result_reporting(self):
        tb = build_testbench([
            {"kind": "insert_card"},
            {"kind": "enter_pin", "pin": 9},
            {"kind": "select_balance"},
        ])
        self.assertIn("$display(\"RESULT", tb)
        self.assertIn("atm_fsm dut", tb)

    def test_run_verilog_simulation_returns_balance(self):
        result = run_verilog_simulation([
            {"kind": "insert_card"},
            {"kind": "enter_pin", "pin": 9},
            {"kind": "select_balance"},
        ])
        self.assertTrue(result["ok"], result.get("error"))
        self.assertEqual(result["balance"], 250)


if __name__ == "__main__":
    unittest.main()
