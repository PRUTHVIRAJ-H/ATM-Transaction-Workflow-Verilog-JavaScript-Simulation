`timescale 1ns / 1ps
module atm_fsm (
    input wire clk,
    input wire rst,
    input wire [15:0] acc_in,      // Account number input (card inserted)
    input wire [3:0] pin_in,       // PIN input (4-bit, 0-15)
    input wire [7:0] amount_in,    // Withdrawal amount input
    input wire withdraw_flag,      // withdrawal flag
    input wire balance_flag,       // balance flag

    output reg [7:0] balance_out,   // final balance
    output reg [7:0] dispense_out,  // cash withdrawn
    output reg auth_error,         // Set on Auth failure or Limit exceeded IN PIN OR WITHDRAW AMOUNT
    output reg locked_out,         // High when account is locked
    output reg card_eject          // High to eject card
);

// --- State Definitions ---
parameter S_HOME              = 4'b0000;
parameter S_CARD_READ         = 4'b0001;
parameter S_PIN_ENTRY         = 4'b0010;
parameter S_AUTH_CHECK        = 4'b0011;    //(BASICALLY PIN VALIDATION)
parameter S_MENU              = 4'b0100;
parameter S_BALANCE           = 4'b0101;
parameter S_WITHDRAW          = 4'b0110;   //(WITHDRAW REQUEST STATE)
parameter S_DISPENSE          = 4'b0111;   //(IF EVERYTHING GOES FINE THEN WITHDRAW YOUR AMOUNT)
parameter S_TRANSACTION_END   = 4'b1000;   //(END THE TRANSACTION)
parameter S_EJECT_CARD        = 4'b1001;   
parameter S_LOCKED            = 4'b1010;
parameter S_ERROR             = 4'b1111;

// --- DEFAULT Security Parameters (JUST FOR CONVINIENCE)---
parameter MAX_PIN_ATTEMPTS  = 3;
parameter MAX_WITHDRAW_AMOUNT = 8'd100; // $100 per transaction
parameter VALID_ACC_NUM     = 16'h1234; // fixed 
parameter VALID_PIN_NUM     = 4'h9;     // 9 is our atm pin

// --- Internal Registers (Memory & State Data) ---
reg [3:0] current_state, next_state;

// AUTHORISATION elements (must be updated in synchronous block)
reg [1:0] pin_attempt_count; 
reg locked; 
reg [7:0] account_balance; 

// --- 1. State and Memory Register (Synchronous Logic) ---
// Updates current_state, pin_attempt_count, locked, and account_balance on clock edge

always @(posedge clk or posedge rst) begin

    if (rst) begin
        current_state <= S_HOME;
        pin_attempt_count <= 2'd0;
        locked <= 1'b0;
        account_balance <= 8'd250; // Initial Balance: $250
    end else begin
        current_state <= next_state;
        
        case (next_state)

        //                      PIN VALIDATION PAR T
            S_AUTH_CHECK: begin 
                // Check for PIN failure to update atempt count
                if (pin_in != VALID_PIN_NUM ) begin
                    pin_attempt_count <= pin_attempt_count + 1;
                end else if (pin_in == VALID_PIN_NUM) begin
                    pin_attempt_count <= 2'd0; // Reset on success
                end
                
                // Set locked flag if max attempts reached after check
                if (pin_in != VALID_PIN_NUM && pin_attempt_count == MAX_PIN_ATTEMPTS - 1) begin
                    locked <= 1'b1;
                end
            end
            
        //                    AMOUNT WITHDRAWL PART
            S_DISPENSE: begin
                // Only update balance if we transition into DISPENSE
                account_balance <= account_balance - amount_in; 
            end
            
            default: begin
                pin_attempt_count <= pin_attempt_count;
                locked <= locked;
                account_balance <= account_balance;
            end
        endcase
    end
end

// --- 2. Next State Logic (Sequential Logic) (MEALEY MODEL : THE NEXT STATE IS DECIDEC BASE ON CURRENT STATE AND INPUT)---
always @(*) begin
    next_state = current_state; // Default: self-loop

    // Set default outputs/next-state values based on current FSM logic
    case (current_state)
        S_HOME: begin
            if (acc_in != 16'd0) begin // Card inserted
                if (locked)
                    next_state = S_LOCKED;
                else
                    next_state = S_CARD_READ;
            end
        end
        
        S_CARD_READ: begin
            if (acc_in == VALID_ACC_NUM)
                next_state = S_PIN_ENTRY;
            else
                next_state = S_ERROR; // Invalid Card
        end
        
        S_PIN_ENTRY: begin
            if (pin_in != 4'd0) // PIN entered
                next_state = S_AUTH_CHECK;
        end
        
        S_AUTH_CHECK: begin
            if (pin_in == VALID_PIN_NUM) begin
                next_state = S_MENU; // Auth Success
            end else begin
                // Failed attempt check
                if (pin_attempt_count == MAX_PIN_ATTEMPTS - 1) begin 
                    next_state = S_LOCKED;
                end else begin
                    next_state = S_EJECT_CARD; // Eject card on fail (ready for next attempt)
                end
            end
        end
        
        S_MENU: begin
            if (balance_flag == 1'b1) // Balance Enquiry
                next_state = S_BALANCE;
            else if (withdraw_flag == 1'b1) // Withdrawal
                next_state = S_WITHDRAW;
        end
        
        S_BALANCE: next_state = S_TRANSACTION_END;
        
        S_WITHDRAW: begin
            if (amount_in == 8'd0) begin
                next_state = S_WITHDRAW; // Still waiting for amount
            end else if (amount_in % 8'd10 != 8'd0) begin
                next_state = S_ERROR; // Invalid increment
            end else if (amount_in > MAX_WITHDRAW_AMOUNT) begin
                next_state = S_ERROR; // Transaction limit exceeded
            end else if (amount_in > account_balance) begin
                next_state = S_ERROR; // Insufficient balance
            end else begin
                next_state = S_DISPENSE;
            end
        end
        
        S_DISPENSE: begin
            // Dispense happens here, sequential balance update queued for next clock
            next_state = S_TRANSACTION_END;
        end
        
        S_TRANSACTION_END: begin
            if (balance_flag == 1'b0) // 0: No more transactions
                next_state = S_EJECT_CARD;
            else if (balance_flag == 1'b1) // 1: Another transaction
                next_state = S_MENU;
        end
        
        S_EJECT_CARD: begin
            next_state = S_HOME; // Back to initial state
        end

        S_LOCKED: begin
            next_state = S_EJECT_CARD; // Locked account is always ejected
        end

        S_ERROR: begin
            next_state = S_EJECT_CARD; // General error also ejects
        end
        
        default: next_state = S_HOME;
    endcase
end

// --- 3. Output Logic (Sequential Logic - Mealy/Moore) ---
// Assigns outputs based on current_state and/or inputs

always @(*) begin
    // Moore Outputs (based on state)
    locked_out = locked;
    
    // Default outputs for transition
    dispense_out = 8'd0;
    card_eject = 1'b0;
    auth_error = 1'b0;
    balance_out = account_balance; // Default to current stored balance

    case (current_state)
        
        S_AUTH_CHECK: begin
            if (pin_in != VALID_PIN_NUM) begin
                auth_error = 1'b1; // Error for failed PIN
            end
        end
        
        S_BALANCE: begin
            balance_out = account_balance; // Output the current balance
        end
        
        S_DISPENSE: begin
            dispense_out = amount_in; // Dispense the requested amount
        end
        
        S_EJECT_CARD: begin
            card_eject = 1'b1; // Eject signal high
        end

        S_LOCKED: begin
            locked_out = 1'b1; // Explicitly set locked output high
        end

        S_ERROR: begin
            auth_error = 1'b1; // Explicitly set auth error high
        end
        
        S_WITHDRAW: begin
            // Check for errors to set error flag (Mealy style)
            if (amount_in != 8'd0 && (amount_in % 8'd10 != 8'd0 || amount_in > MAX_WITHDRAW_AMOUNT || amount_in > account_balance)) begin
                auth_error = 1'b1;
            end
        end
        
        default: ;
    endcase
end


endmodule // atm_fsm
