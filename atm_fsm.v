`timescale 1ns / 1ps

module atm_fsm (
    input wire clk,
    input wire rst,
    input wire [15:0] acc_in,
    input wire [3:0] pin_in,
    input wire [7:0] amount_in,
    input wire withdraw_flag,
    input wire balance_flag,
    output reg [7:0] balance_out,
    output reg [7:0] dispense_out,
    output reg auth_error,
    output reg locked_out,
    output reg card_eject
);

    // --- State Definitions ---
    parameter S_HOME            = 4'b0000;
    parameter S_CARD_READ       = 4'b0001;
    parameter S_PIN_ENTRY       = 4'b0010;
    parameter S_AUTH_CHECK      = 4'b0011;
    parameter S_MENU            = 4'b0100;
    parameter S_BALANCE         = 4'b0101;
    parameter S_WITHDRAW        = 4'b0110;
    parameter S_DISPENSE        = 4'b0111;
    parameter S_TRANSACTION_END = 4'b1000;
    parameter S_EJECT_CARD      = 4'b1001;
    parameter S_LOCKED          = 4'b1010;
    parameter S_ERROR           = 4'b1111;

    // --- Security Parameters ---
    parameter MAX_PIN_ATTEMPTS = 3;
    parameter MAX_WITHDRAW_AMOUNT = 8'd100;
    parameter VALID_ACC_NUM = 16'h1234;
    parameter VALID_PIN_NUM = 4'h9;

    // --- Internal Registers ---
    reg [3:0] current_state, next_state;
    reg [1:0] pin_attempt_count;
    reg locked;
    reg [7:0] account_balance;

    // 1. State and Memory Register (Synchronous Logic)
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            current_state <= S_HOME;
            pin_attempt_count <= 2'd0;
            locked <= 1'b0;
            account_balance <= 8'd250; 
        end else begin
            current_state <= next_state;
            case (next_state)
                S_AUTH_CHECK: begin
                    if (pin_in != VALID_PIN_NUM) begin
                        pin_attempt_count <= pin_attempt_count + 1;
                        if (pin_attempt_count == 2) locked <= 1'b1;
                    end else begin
                        pin_attempt_count <= 2'd0;
                    end
                end
                S_DISPENSE: begin
                    account_balance <= account_balance - amount_in;
                end
                default: ;
            endcase
        end
    end

    // 2. Next State Logic (Combinational)
    always @(*) begin
        next_state = current_state;
        case (current_state)
            S_HOME: begin
                if (acc_in != 16'd0) 
                    next_state = (locked) ? S_LOCKED : S_CARD_READ;
            end
            S_CARD_READ: next_state = (acc_in == VALID_ACC_NUM) ? S_PIN_ENTRY : S_ERROR;
            S_PIN_ENTRY: if (pin_in != 4'd0) next_state = S_AUTH_CHECK;
            S_AUTH_CHECK: begin
                if (pin_in == VALID_PIN_NUM) next_state = S_MENU;
                else if (pin_attempt_count == MAX_PIN_ATTEMPTS - 1) next_state = S_LOCKED;
                else next_state = S_EJECT_CARD;
            end
            S_MENU: begin
                if (balance_flag) next_state = S_BALANCE;
                else if (withdraw_flag) next_state = S_WITHDRAW;
            end
            S_BALANCE: next_state = S_TRANSACTION_END;
            S_WITHDRAW: begin
                if (amount_in == 8'd0) next_state = S_WITHDRAW;
                else if (amount_in % 8'd10 != 0 || amount_in > MAX_WITHDRAW_AMOUNT || amount_in > account_balance)
                    next_state = S_ERROR;
                else next_state = S_DISPENSE;
            end
            S_DISPENSE: next_state = S_TRANSACTION_END;
            S_TRANSACTION_END: next_state = (balance_flag) ? S_MENU : S_EJECT_CARD;
            S_EJECT_CARD: next_state = S_HOME;
            S_LOCKED: next_state = S_EJECT_CARD;
            S_ERROR: next_state = S_EJECT_CARD;
            default: next_state = S_HOME;
        endcase
    end

    // 3. Output Logic
    always @(*) begin
        locked_out = locked;
        dispense_out = 8'd0;
        card_eject = 1'b0;
        auth_error = 1'b0;
        balance_out = account_balance;
        
        case (current_state)
            S_AUTH_CHECK: if (pin_in != VALID_PIN_NUM) auth_error = 1'b1;
            S_DISPENSE: dispense_out = amount_in;
            S_EJECT_CARD: card_eject = 1'b1;
            S_LOCKED: locked_out = 1'b1;
            S_ERROR: auth_error = 1'b1;
            S_WITHDRAW: if (amount_in != 0 && (amount_in % 10 != 0 || amount_in > MAX_WITHDRAW_AMOUNT || amount_in > account_balance))
                            auth_error = 1'b1;
            default: ;
        endcase
    end
endmodule
