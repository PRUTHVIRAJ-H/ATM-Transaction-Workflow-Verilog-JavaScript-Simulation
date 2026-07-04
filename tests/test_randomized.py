import random
import unittest

from sim.atm_server import run_verilog_simulation


def random_actions():

    actions = []

    actions.append({
        "kind": "insert_card",
        "account": random.choice([
            0x1234,
            0x9999,
        ])
    })

    actions.append({
        "kind": "enter_pin",
        "pin": random.randint(0, 15),
    })

    if random.random() < 0.5:
        actions.append({
            "kind": "select_balance",
        })
    else:
        actions.append({
            "kind": "withdraw",
            "amount": random.randint(0, 200),
        })

    return actions


class TestRandomized(unittest.TestCase):

    def test_random_sequences(self):

        for _ in range(200):
            result = run_verilog_simulation(
                random_actions()
            )

            self.assertTrue(
                result["ok"],
                msg=result,
            )


if __name__ == "__main__":
    unittest.main()

