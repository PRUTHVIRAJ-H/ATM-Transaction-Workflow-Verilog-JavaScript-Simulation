#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parent.parent
ATM_FSM = ROOT / "src" / "atm_fsm.v"


def build_testbench(actions: Iterable[Dict[str, Any]]) -> str:
    lines: List[str] = [
        "    #20;",
        "    rst = 1;",
        "    acc_in = 16'd0;",
        "    pin_in = 4'd0;",
        "    amount_in = 8'd0;",
        "    withdraw_flag = 1'b0;",
        "    balance_flag = 1'b0;",
        "    #20;",
        "    rst = 0;",
        "    #40;",
    ]

    for action in actions:
        kind = action["kind"]

        if kind == "insert_card":
            acc = int(action.get("account", 0x1234))
            lines += [
                f"    acc_in = 16'h{acc:04x};",
                "    #40;",
                "    acc_in = 16'd0;",
                "    #40;",
            ]

        elif kind == "enter_pin":
            pin = int(action.get("pin", 9))
            lines += [
                f"    pin_in = 4'd{pin};",
                "    #40;",
                "    pin_in = 4'd0;",
                "    #40;",
            ]

        elif kind == "select_balance":
            lines += [
                "    balance_flag = 1'b1;",
                "    #40;",
                "    balance_flag = 1'b0;",
                "    #40;",
            ]

        elif kind == "withdraw":
            amount = int(action.get("amount", 0))
            lines += [
                "    withdraw_flag = 1'b1;",
                f"    amount_in = 8'd{amount};",
                "    #40;",
                "    withdraw_flag = 1'b0;",
                "    amount_in = 8'd0;",
                "    #80;",
            ]

    lines += [
        "    #100;",
        '    $display("RESULT balance=%0d locked=%b auth_error=%b dispense=%0d state=%0d",',
        "        balance_out,",
        "        locked_out,",
        "        auth_error,",
        "        dispense_out,",
        "        dut.current_state);",
        "    $finish;",
    ]

    actions_text = "\n".join(lines)

    return f"""
`timescale 1ns / 1ps

module atm_server_tb;

reg clk;
reg rst;
reg [15:0] acc_in;
reg [3:0] pin_in;
reg [7:0] amount_in;
reg withdraw_flag;
reg balance_flag;

wire [7:0] balance_out;
wire [7:0] dispense_out;
wire auth_error;
wire locked_out;
wire card_eject;
wire [3:0] debug_state;

atm_fsm dut (
    .clk(clk),
    .rst(rst),
    .acc_in(acc_in),
    .pin_in(pin_in),
    .amount_in(amount_in),
    .withdraw_flag(withdraw_flag),
    .balance_flag(balance_flag),
    .balance_out(balance_out),
    .dispense_out(dispense_out),
    .auth_error(auth_error),
    .locked_out(locked_out),
    .card_eject(card_eject),
    .debug_state(debug_state)
);

initial clk = 0;
always #5 clk = ~clk;

always @(posedge clk)
begin
    $display("STATE %0d", debug_state);
end

initial begin
{actions_text}
end

endmodule
"""


def run_verilog_simulation(
    actions: Iterable[Dict[str, Any]]
) -> Dict[str, Any]:

    tb_source = build_testbench(actions)

    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)

        tb_path = tempdir / "atm_server_tb.v"
        sim_path = tempdir / "atm_server"

        tb_path.write_text(tb_source)

        compile_proc = subprocess.run(
            [
                "iverilog",
                "-o",
                str(sim_path),
                str(ATM_FSM),
                str(tb_path),
            ],
            capture_output=True,
            text=True,
        )

        if compile_proc.returncode != 0:
            return {
                "ok": False,
                "error": "compile failed",
                "stderr": compile_proc.stderr,
            }

        run_proc = subprocess.run(
            ["vvp", str(sim_path)],
            capture_output=True,
            text=True,
        )

        visited_states = []

        if run_proc.returncode != 0:
         return {
           "ok": False,
           "error": "simulation failed",
           "stdout": run_proc.stdout,
           "stderr": run_proc.stderr,
           "returncode": run_proc.returncode,
         }

        result = {
            "ok": False,
            "stdout": run_proc.stdout,
        }

        for line in run_proc.stdout.splitlines():

            if line.startswith("STATE"):
                token = line.split()[1]

                try:
                   visited_states.append(int(token))
                except ValueError:
                    pass

                continue


            if not line.startswith("RESULT"):
                continue

            result["ok"] = True

            for token in line.split()[1:]:
                key, value = token.split("=")

                if key in ("balance", "dispense", "state"):
                    result[key] = int(value)

                elif key in ("locked", "auth_error"):
                    result[key] = value == "1"

            break

        if not result["ok"]:
            result["error"] = "RESULT line not found"

        compressed_states = []

        for s in visited_states:
           if not compressed_states or compressed_states[-1] != s:
               compressed_states.append(s)

        result["visited_states"] = compressed_states

        transitions = set()

        for a, b in zip(
            compressed_states,
            compressed_states[1:]):
          transitions.add((a, b))

        result["transitions"] = sorted(transitions)

        return result

