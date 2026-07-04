`timescale 1ns / 1ps

module atm_fsm (
    input wire clk,
    input wire rst,
    input wire [15:0] acc_in,
    input wire [3:0]  pin_in,
    input wire [7:0]  amount_in,
    input wire withdraw_flag,
    input wire balance_flag,

    output reg [7:0] balance_out,
    output reg [7:0] dispense_out,
    output reg auth_error,
    output reg locked_out,
    output reg card_eject,
    output wire [3:0] debug_state
);

//====================================================
// State Encoding
//====================================================
localparam S_HOME            = 4'd0;
localparam S_CARD_READ       = 4'd1;
localparam S_PIN_ENTRY       = 4'd2;
localparam S_AUTH_CHECK      = 4'd3;
localparam S_MENU            = 4'd4;
localparam S_BALANCE         = 4'd5;
localparam S_WITHDRAW        = 4'd6;
localparam S_DISPENSE        = 4'd7;
localparam S_TRANSACTION_END = 4'd8;
localparam S_EJECT_CARD      = 4'd9;
localparam S_LOCKED          = 4'd10;
localparam S_ERROR           = 4'd15;

//====================================================
// Parameters
//====================================================
localparam MAX_PIN_ATTEMPTS   = 3;
localparam MAX_WITHDRAW       = 8'd100;
localparam VALID_ACC_NUM      = 16'h1234;
localparam VALID_PIN_NUM      = 4'h9;
localparam INITIAL_BALANCE    = 8'd250;

//====================================================
// Registers
//====================================================
reg [3:0] current_state;
reg [3:0] next_state;

reg [1:0] pin_attempt_count;
reg       locked;
reg [7:0] account_balance;

// Latched inputs
reg [15:0] inserted_acc;
reg [3:0]  entered_pin;
reg [7:0]  requested_amount;

// Debug output for verification/testing
assign debug_state = current_state;

//====================================================
// Sequential Logic
//====================================================
always @(posedge clk or posedge rst) begin
    if (rst) begin
        current_state      <= S_HOME;
        pin_attempt_count  <= 2'd0;
        locked             <= 1'b0;
        account_balance    <= INITIAL_BALANCE;

        inserted_acc       <= 16'd0;
        entered_pin        <= 4'd0;
        requested_amount   <= 8'd0;
    end
    else begin
        current_state <= next_state;

        //------------------------------------------------
        // Latch inputs
        //------------------------------------------------
        if (current_state == S_HOME && acc_in != 16'd0)
            inserted_acc <= acc_in;

        if (current_state == S_PIN_ENTRY && pin_in != 4'd0)
            entered_pin <= pin_in;

        if (current_state == S_WITHDRAW && amount_in != 8'd0)
            requested_amount <= amount_in;

        //------------------------------------------------
        // Authentication handling
        //------------------------------------------------
        if (current_state == S_AUTH_CHECK) begin
            if (entered_pin == VALID_PIN_NUM) begin
                pin_attempt_count <= 2'd0;
            end
            else begin
                pin_attempt_count <= pin_attempt_count + 1'b1;

                if (pin_attempt_count + 1 >= MAX_PIN_ATTEMPTS)
                    locked <= 1'b1;
            end
        end

        //------------------------------------------------
        // Balance update
        //------------------------------------------------
        if (current_state == S_DISPENSE)
            account_balance <= account_balance - requested_amount;

        //------------------------------------------------
        // Clear session after card eject
        //------------------------------------------------
        if (current_state == S_EJECT_CARD) begin
            inserted_acc     <= 16'd0;
            entered_pin      <= 4'd0;
            requested_amount <= 8'd0;
        end
    end
end

//====================================================
// Next State Logic
//====================================================
always @(*) begin
    next_state = current_state;

    case (current_state)

        S_HOME:
            if (acc_in != 16'd0)
                next_state = locked ? S_LOCKED : S_CARD_READ;

        S_CARD_READ:
            if (inserted_acc == VALID_ACC_NUM)
                next_state = S_PIN_ENTRY;
            else
                next_state = S_ERROR;

        S_PIN_ENTRY:
            if (pin_in != 4'd0)
                next_state = S_AUTH_CHECK;

        S_AUTH_CHECK:
            if (entered_pin == VALID_PIN_NUM)
                next_state = S_MENU;
            else if (pin_attempt_count + 1 >= MAX_PIN_ATTEMPTS)
                next_state = S_LOCKED;
            else
                next_state = S_EJECT_CARD;

        S_MENU:
            if (balance_flag)
                next_state = S_BALANCE;
            else if (withdraw_flag)
                next_state = S_WITHDRAW;

        S_BALANCE:
            next_state = S_TRANSACTION_END;

        S_WITHDRAW: begin
            if (requested_amount == 8'd0)
                next_state = S_WITHDRAW;
            else if (requested_amount % 8'd10 != 8'd0)
                next_state = S_ERROR;
            else if (requested_amount > MAX_WITHDRAW)
                next_state = S_ERROR;
            else if (requested_amount > account_balance)
                next_state = S_ERROR;
            else
                next_state = S_DISPENSE;
        end

        S_DISPENSE:
            next_state = S_TRANSACTION_END;

        S_TRANSACTION_END:
            next_state = S_EJECT_CARD;

        S_EJECT_CARD:
            next_state = S_HOME;

        S_LOCKED:
            next_state = S_EJECT_CARD;

        S_ERROR:
            next_state = S_EJECT_CARD;

        default:
            next_state = S_HOME;
    endcase
end

//====================================================
// Output Logic
//====================================================
always @(*) begin
    balance_out  = account_balance;
    dispense_out = 8'd0;
    auth_error   = 1'b0;
    card_eject   = 1'b0;
    locked_out   = locked;

    case (current_state)

        S_AUTH_CHECK:
            if (entered_pin != VALID_PIN_NUM)
                auth_error = 1'b1;

        S_BALANCE:
            balance_out = account_balance;

        S_DISPENSE:
            dispense_out = requested_amount;

        S_ERROR:
            auth_error = 1'b1;

        S_EJECT_CARD:
            card_eject = 1'b1;

        S_LOCKED:
            locked_out = 1'b1;

        default: ;
    endcase
end


//====================================================
// Assertions (Icarus Verilog Compatible)
//====================================================
always @(posedge clk) begin
    if (account_balance > INITIAL_BALANCE) begin
        $display("ASSERTION FAILED: Balance corruption detected");
        $finish;
    end
end

always @(posedge clk) begin
    if (dispense_out > MAX_WITHDRAW) begin
        $display("ASSERTION FAILED: Invalid dispense amount");
        $finish;
    end
end



//====================================================
// Waveforms
//====================================================
initial begin
    $dumpfile("sim/atm_waves.vcd");
    $dumpvars(0, atm_fsm);
end

endmodule
