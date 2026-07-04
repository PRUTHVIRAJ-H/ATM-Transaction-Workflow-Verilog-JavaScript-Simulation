import unittest

from sim.atm_server import run_verilog_simulation


class TestTransitionCoverage(unittest.TestCase):

    def test_transition_coverage(self):

        transitions = set()

        scenarios = [
            [
                {"kind": "insert_card", "account": 0x1234},
                {"kind": "enter_pin", "pin": 9},
                {"kind": "select_balance"},
            ],
            [
                {"kind": "insert_card", "account": 0x1234},
                {"kind": "enter_pin", "pin": 9},
                {"kind": "withdraw", "amount": 50},
            ],
            [
                {"kind": "insert_card", "account": 0x1234},
                {"kind": "enter_pin", "pin": 1},
            ],
        ]

        for s in scenarios:
            result = run_verilog_simulation(s)
            transitions.update(result["transitions"])

        self.assertGreater(
            len(transitions),
            5,
        )


if __name__ == "__main__":
    unittest.main()

