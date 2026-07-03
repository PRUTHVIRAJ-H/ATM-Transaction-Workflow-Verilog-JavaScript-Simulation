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
        "    #20;",
    ]

    for action in actions:
        kind = action.get("kind")
        if kind == "insert_card":
            acc = int(action.get("account", 0))
            lines += [
                f"    acc_in = 16'h{acc:04x};",
                "    #20;",
                "    acc_in = 16'd0;",
                "    #20;",
            ]
        elif kind == "enter_pin":
            pin = int(action.get("pin", 0))
            lines += [
                f"    pin_in = 4'd{pin};",
                "    #20;",
                "    pin_in = 4'd0;",
                "    #20;",
            ]
        elif kind == "select_balance":
            lines += [
                "    balance_flag = 1'b1;",
                "    #20;",
                "    balance_flag = 1'b0;",
                "    #20;",
            ]
        elif kind == "withdraw":
            amount = int(action.get("amount", 0))
            lines += [
                f"    amount_in = 8'd{amount};",
                "    withdraw_flag = 1'b1;",
                "    #20;",
                "    withdraw_flag = 1'b0;",
                "    #20;",
            ]

    lines += [
        "    #20;",
        '    $display("RESULT balance=%0d locked=%b auth_error=%b dispense=%0d", balance_out, locked_out, auth_error, dispense_out);',
        "    $finish;",
    ]

    actions_text = "\n".join(lines)
    return f"""`timescale 1ns / 1ps
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
        .card_eject(card_eject)
    );

    initial clk = 0;
    always #5 clk = ~clk;

    initial begin
{actions_text}
    end
endmodule
"""


def run_verilog_simulation(actions: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    tb_source = build_testbench(actions)

    with tempfile.TemporaryDirectory() as tempdir:
        tb_path = Path(tempdir) / "atm_server_tb.v"
        tb_path.write_text(tb_source, encoding="utf-8")
        sim_path = Path(tempdir) / "atm_server"

        compile_cmd = ["iverilog", "-o", str(sim_path), str(ATM_FSM), str(tb_path)]
        compile_proc = subprocess.run(compile_cmd, capture_output=True, text=True)
        if compile_proc.returncode != 0:
            return {
                "ok": False,
                "error": "iverilog compile failed",
                "stderr": compile_proc.stderr,
            }

        run_proc = subprocess.run(["vvp", str(sim_path)], capture_output=True, text=True)
        if run_proc.returncode != 0:
            return {
                "ok": False,
                "error": "simulation failed",
                "stderr": run_proc.stderr,
            }

    result = {"ok": False, "stdout": run_proc.stdout}
    for line in run_proc.stdout.splitlines():
        if line.startswith("RESULT"):
            parts = line.split()
            for token in parts[1:]:
                if token.startswith("balance="):
                    result["balance"] = int(token.split("=", 1)[1])
                elif token.startswith("locked="):
                    result["locked"] = token.split("=", 1)[1] == "1"
                elif token.startswith("auth_error="):
                    result["auth_error"] = token.split("=", 1)[1] == "1"
                elif token.startswith("dispense="):
                    result["dispense"] = int(token.split("=", 1)[1])
            result["ok"] = True
            break

    if not result["ok"]:
        result["error"] = "RESULT line not found in simulation output"
    return result
