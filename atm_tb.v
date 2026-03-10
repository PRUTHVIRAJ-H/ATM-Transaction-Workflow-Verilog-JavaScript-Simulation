`timescale 1ns / 1ps

module atm_fsm_tb;
     // --- Signals ---
     reg clk;
     reg rst;
     reg [15:0] acc_in;
     reg [3:0] pin_in;
     reg [7:0] amount_in;
     reg withdraw_flag;  // 1: Withdraw / Continue | 0: Balance / No Transaction
     reg balance_flag;

     // Outputs from the DUT (Device Under Test)
     wire [7:0] balance_out;
     wire [7:0] dispense_out;
     wire auth_error;
     wire locked_out;
     wire card_eject;
    
     // --- Intermediate Signal for Monitor Fix ---
     reg [8*16:1] current_state_name;
    
     // --- Constants ---
     parameter CLK_PERIOD = 10;
     parameter VALID_ACC = 16'h1234;
     parameter VALID_PIN = 4'h9;
     parameter INVALID_PIN_1 = 4'h1;
     parameter INVALID_PIN_2 = 4'h2;
     parameter INVALID_PIN_3 = 4'h3;
     // Initial Balance (250) is assumed to be handled inside atm_fsm.v
    
     // --- Instantiate DUT (Design Under Test) ---
     atm_fsm dut (.*);

     // --- Clock Generation ---
     initial begin
         clk = 0;
         forever #(CLK_PERIOD/2) clk = ~clk;
     end
    

     // This procedural block continuously updates 'current_state_name' whenever the state changes.
     always @(*) begin
         current_state_name = case_state_name(dut.current_state);
     end

     // --- Waveform Dump and Monitoring ---
     initial begin
         $dumpfile("atm_fsm.vcd");
         $dumpvars(0, atm_fsm_tb);

         // Monitor key signals for debugging (now using the pre-calculated 'current_state_name')
  	 $monitor("\n\
+--------+------------------------+----------------+----------------+---------------------+---------------------+--------+--------+\n\
| Time   | Current State (Name)   | Account No In  | PIN Entered    | Available Balance   | Withdrawn Amount   | Error  | Locked |\n\
+--------+------------------------+----------------+----------------+---------------------+---------------------+--------+--------+\n\
|%0t   %h->%s            %h              %h               %0d                     %0d                    %b              %b    \n\
+--------+------------------------+----------------+----------------+---------------------+---------------------+--------+--------+",
  $time, dut.current_state, current_state_name, acc_in, pin_in, balance_out, dispense_out, auth_error, locked_out);

     end

     // Helper function for state names (Verilog-compatible return type)
     function [8*16:1] case_state_name;
         input [3:0] state;
         begin 
             case (state)
                4'h0: case_state_name = "HOME";
                4'h1: case_state_name = "CARD_READ";
                4'h2: case_state_name = "PIN_ENTRY";
                4'h3: case_state_name = "AUTH_CHECK";
                4'h4: case_state_name = "MENU";
                4'h5: case_state_name = "BALANCE";
                4'h6: case_state_name = "WITHDRAW";
                4'h7: case_state_name = "DISPENSE";
                4'h8: case_state_name = "TRANS_END";
                4'h9: case_state_name = "EJECT";
                4'ha: case_state_name = "LOCKED";
                4'hf: case_state_name = "ERROR";
                default: case_state_name = "UNKNOWN";
             endcase
         end 
     endfunction

     // --- Simulation Scenario ---

     initial begin
         // Initial Reset
         rst = 1;
         acc_in = 16'd0;
         pin_in = 4'd0;
         amount_in = 8'd0;
         withdraw_flag = 1'b0;
         balance_flag = 1'b0;
         # (CLK_PERIOD * 2) rst = 0;
         $display("\n--- SCENARIO 1: SUCCESSFUL CARD INSERTION AND PIN VERIFICATION ---");


//  TEST 1 

         // 1.1 Insert Card and Auth
         # (CLK_PERIOD) acc_in = VALID_ACC;
         # (CLK_PERIOD * 2) acc_in = 16'd0; 
         # (CLK_PERIOD * 3) pin_in = VALID_PIN;
         # (CLK_PERIOD * 2) pin_in = 4'd0; 


         // 1.3 Eject Card
         # (CLK_PERIOD * 3);


         $display("\n--- SCENARIO 2: SUCCESSFUL WITHDRAWAL ($50). Balance: 250 -> 200 ---");

         // 2.1 Insert Card and Auth
         # (CLK_PERIOD) acc_in = VALID_ACC;
         # (CLK_PERIOD * 2) acc_in = 16'd0; 
         # (CLK_PERIOD * 3) pin_in = VALID_PIN;
         # (CLK_PERIOD * 2) pin_in = 4'd0; 

         // 2.2 Withdraw $50 
         # (CLK_PERIOD) withdraw_flag = 1'b1; // Select Withdraw
         # (CLK_PERIOD * 3) amount_in = 8'd50; 
         # (CLK_PERIOD * 2) amount_in = 8'd0;

         // 2.3 End Transaction
         # (CLK_PERIOD * 3) balance_flag = 1'b0; 
         # (CLK_PERIOD * 3);


         $display("\n--- SCENARIO 3: SUCCESSFUL WITHDRAWAL ($100). Balance: 200 -> 100 ---");

         // 3.1 Insert Card and Auth
         # (CLK_PERIOD) acc_in = VALID_ACC;
         # (CLK_PERIOD * 2) acc_in = 16'd0; 
         # (CLK_PERIOD * 3) pin_in = VALID_PIN;
         # (CLK_PERIOD * 2) pin_in = 4'd0; 

         // 3.2 Withdraw $100 
         # (CLK_PERIOD) withdraw_flag = 1'b1; 
         # (CLK_PERIOD * 3) amount_in = 8'd100; // Depletes balance to 100
         # (CLK_PERIOD * 2) amount_in = 8'd0;

         // 3.3 End Transaction
         # (CLK_PERIOD * 3) balance_flag = 1'b0; 
         # (CLK_PERIOD * 3);


         $display("\n--- SCENARIO 4: SUCCESSFUL WITHDRAWAL ($100). Balance: 100 -> 0 ---");

         // 4.1 Insert Card and Auth
         # (CLK_PERIOD) acc_in = VALID_ACC;
         # (CLK_PERIOD * 2) acc_in = 16'd0; 
         # (CLK_PERIOD * 3) pin_in = VALID_PIN;
         # (CLK_PERIOD * 2) pin_in = 4'd0; 

         // 4.2 Withdraw $100 
         # (CLK_PERIOD) withdraw_flag = 1'b1; 
         # (CLK_PERIOD * 3) amount_in = 8'd100; // Depletes balance to 0
         # (CLK_PERIOD * 2) amount_in = 8'd0;

         // 4.3 End Transaction
         # (CLK_PERIOD * 3) balance_flag = 1'b0; 
         # (CLK_PERIOD * 3);


         $display("\n--- SCENARIO 5: FAILURE: INSUFFICIENT FUNDS (Attempt to withdraw $50 from 0) ---");

         // 5.1 Insert Card and Auth
         # (CLK_PERIOD) acc_in = VALID_ACC;
         # (CLK_PERIOD * 2) acc_in = 16'd0; 
         # (CLK_PERIOD * 3) pin_in = VALID_PIN;
         # (CLK_PERIOD * 2) pin_in = 4'd0; 

         // 5.2 Select Withdraw
         # (CLK_PERIOD) withdraw_flag = 1'b1; 

         // 5.3 Enter Amount $50 (Should trigger ERROR state due to insufficient funds)
         # (CLK_PERIOD * 3) amount_in = 8'd50; 
         # (CLK_PERIOD * 2) amount_in = 8'd0;

         // 5.4 End Transaction (Eject Card after Error)
         # (CLK_PERIOD * 3) balance_flag = 1'b0; 
         # (CLK_PERIOD * 3);


         $display("\n--- SCENARIO 6: SECURITY LOCKOUT TEST (3 Failed PIN Attempts) ---");

         // 6.1 Attempt 1 (Fail)
         # (CLK_PERIOD) acc_in = VALID_ACC;
         # (CLK_PERIOD * 2) acc_in = 16'd0; 
         # (CLK_PERIOD * 3) pin_in = INVALID_PIN_1; // Fail 1
         # (CLK_PERIOD * 2) pin_in = 4'd0; 
         # (CLK_PERIOD * 3); 

         // 6.2 Attempt 2 (Fail)
         # (CLK_PERIOD) acc_in = VALID_ACC;
         # (CLK_PERIOD * 2) acc_in = 16'd0; 
         # (CLK_PERIOD * 3) pin_in = INVALID_PIN_2; // Fail 2
         # (CLK_PERIOD * 2) pin_in = 4'd0; 
         # (CLK_PERIOD * 3); 

         // 6.3 Attempt 3 (LOCKOUT TRIGGER)
         # (CLK_PERIOD) acc_in = VALID_ACC;
         # (CLK_PERIOD * 2) acc_in = 16'd0; 
         # (CLK_PERIOD * 3) pin_in = INVALID_PIN_3; // Fail 3 -> LOCK
         # (CLK_PERIOD * 2) pin_in = 4'd0; 
         # (CLK_PERIOD * 3); 

         // 6.4 Test Locked State
         $display("SCENARIO 7: Testing attempted login on LOCKED account ---");
         # (CLK_PERIOD) acc_in = VALID_ACC;
         # (CLK_PERIOD * 2) acc_in = 16'd0; 

         # (CLK_PERIOD * 5); 

         $finish;
    end
 
endmodule
