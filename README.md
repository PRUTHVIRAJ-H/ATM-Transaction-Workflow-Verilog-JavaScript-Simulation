# DDCO-PROJECT---FSM-MODEL-FOR-ATM-MACHINE

# ATM Transaction Workflow - FSM Project

A Verilog implementation of an Automated Teller Machine (ATM) Finite State Machine (FSM). This project simulates the core logic of an ATM, including authentication, balance enquiry, cash withdrawal, and security lockouts.

## Features
- **Authentication**: Validates 16-bit account numbers and 4-bit PINs.
- **Transaction Types**: Supports Balance Enquiry and Withdrawal.
- **Security**: Implements a 3-attempt PIN lockout system.
- **Error Handling**: Validates withdrawal increments (multiples of 10) and account balance limits.

## State Machine Overview
The FSM consists of the following primary states:
- `S_HOME`: Idle state waiting for card insertion.
- `S_AUTH_CHECK`: Validates the entered PIN.
- `S_MENU`: Central navigation for user actions.
- `S_WITHDRAW`: Checks if requested cash is within limits and available balance.
- `S_LOCKED`: Permanent security lock after 3 failed PIN attempts.


## Technical Specifications
- **Tools Used**: Verilog HDL, GTKWave (for waveform analysis).
- **Major Parameters**:
  - `Initial Balance`: $250
  - `Max Withdrawal per Transaction`: $100
  - `Valid PIN`: 4'h9
  - `Valid Account`: 16'h1234

## How to Run
1. Clone the repository.
2. Compile the design using your preferred simulator (e.g., Icarus Verilog):
   ```bash
   iverilog -o atm_sim atm_fsm.v atm_fsm_tb.v
   vvp atm_sim
3 gtkwave atm_fsm.vcd  (for Wavefront)
