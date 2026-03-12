```mermaid
stateDiagram-v2
    [*] --> S_IDLE
    S_IDLE --> S_ACCOUNT_VAL : Card Inserted
    S_ACCOUNT_VAL --> S_PIN_ENTRY : Valid Account
    S_ACCOUNT_VAL --> S_IDLE : Invalid Account
    
    S_PIN_ENTRY --> S_PIN_CHECK : PIN Entered
    S_PIN_CHECK --> S_MENU : Correct PIN
    S_PIN_CHECK --> S_PIN_ENTRY : Wrong PIN (Attempt < 3)
    S_PIN_CHECK --> S_LOCKED : Wrong PIN (Attempt = 3)
    
    S_LOCKED --> [*] : Security Lockout Triggered
    
    S_MENU --> S_AMT_INPUT : Select Withdrawal
    S_AMT_INPUT --> S_BAL_CHECK : Amount Entered
    S_MENU --> S_BAL_CHECK : Select Balance Check
    
    S_BAL_CHECK --> S_DISPENSE : Sufficient Balance
    S_BAL_CHECK --> S_MENU : Insufficient Funds
    
    S_DISPENSE --> S_RECEIPT
    S_RECEIPT --> S_EJECT
    S_EJECT --> S_IDLE
```

# ATM Transaction Workflow - FSM Project

A comprehensive hardware-level simulation of an Automated Teller Machine (ATM) using a 12-state Finite State Machine (FSM). This project bridges the gap between low-level Verilog logic and high-level interactive visualization.

## 🚀 Features
- *Multi-State Security*: Implements a complex 12-state FSM for robust transaction handling.
- *Authentication*: Validates 16-bit account numbers and 4-bit PINs.
- *Security Lockout*: Real-time tracking of failed attempts with a permanent S_LOCKED state after 3 failures.
- *Hardware-Level Constraints*: Validates balance registers and withdrawal increments (multiples of 10).
- *Hybrid Simulation*: Verilog logic verified via GTKWave testbenches alongside an interactive HTML/CSS/JS functional simulator.
