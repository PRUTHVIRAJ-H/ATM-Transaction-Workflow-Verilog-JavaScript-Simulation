#!/usr/bin/env python3
"""
Flask-based backend server for ATM FSM simulator.
Accepts JSON actions from the frontend and runs them through the Verilog DUT.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from sim.atm_server import run_verilog_simulation

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# Session storage: track user interactions per session
sessions = {}


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/session/start", methods=["POST"])
def session_start():
    """Start a new ATM session."""
    import uuid
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "actions": [],
        "state": "HOME",
        "message": "Insert your card to begin",
    }
    return jsonify({"session_id": session_id})


@app.route("/api/session/<session_id>/action", methods=["POST"])
def session_action(session_id):
    """Execute an action and get results from the Verilog DUT."""
    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404

    data = request.get_json()
    action = data.get("action")

    if not action:
        return jsonify({"error": "Missing action"}), 400

    session = sessions[session_id]

    # Convert frontend action to backend action format
    backend_action = None
    message = ""

    if action["type"] == "insert_card":
        account = action.get("account")
        if not account:
            return jsonify({"error": "Missing account"}), 400
        backend_action = {"kind": "insert_card", "account": account}
        message = f"Card inserted with account {account}. Verifying..."

    elif action["type"] == "enter_pin":
        pin_digit = action.get("pin")
        if pin_digit is None:
            return jsonify({"error": "Missing PIN digit"}), 400
        backend_action = {"kind": "enter_pin", "pin": int(pin_digit)}
        message = "PIN entered."

    elif action["type"] == "select_balance":
        backend_action = {"kind": "select_balance"}
        message = "Checking balance..."

    elif action["type"] == "withdraw":
        amount = action.get("amount")
        if amount is None:
            return jsonify({"error": "Missing amount"}), 400
        backend_action = {"kind": "withdraw", "amount": int(amount)}
        message = f"Requesting withdrawal of ${amount}..."

    elif action["type"] == "reset":
        sessions[session_id] = {
            "actions": [],
            "state": "HOME",
            "message": "ATM reset. Insert card to begin.",
        }
        return jsonify({
            "state": "HOME",
            "message": "ATM reset. Insert card to begin.",
            "balance": 250,
            "locked": False,
        })

    else:
        return jsonify({"error": f"Unknown action type: {action['type']}"}), 400

    # Add action to session history
    session["actions"].append(backend_action)

    # Run simulation with all accumulated actions
    result = run_verilog_simulation(session["actions"])

    if not result.get("ok"):
        return jsonify({"error": result.get("error", "Simulation failed")}), 500

    # Parse and return results
    balance = result.get("balance", 250)
    locked = result.get("locked", False)
    auth_error = result.get("auth_error", False)
    dispense = result.get("dispense", 0)

    # Determine state based on simulation result
    state = "MENU"
    if locked:
        state = "LOCKED"
    elif auth_error and action["type"] == "enter_pin":
        state = "PIN_ERROR"
    elif dispense > 0:
        state = "DISPENSED"
    elif action["type"] == "select_balance":
        state = "BALANCE_SHOWN"

    return jsonify({
        "state": state,
        "message": message,
        "balance": balance,
        "locked": locked,
        "auth_error": auth_error,
        "dispense": dispense,
    })


@app.route("/api/session/<session_id>", methods=["GET"])
def session_get(session_id):
    """Get current session state."""
    if session_id not in sessions:
        return jsonify({"error": "Session not found"}), 404

    session = sessions[session_id]
    return jsonify({
        "state": session.get("state"),
        "message": session.get("message"),
        "actions": len(session.get("actions", [])),
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
