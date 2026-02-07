// Testbench for ALU
`timescale 1ns/1ps

module alu_tb;
    parameter WIDTH = 8;
    parameter CLK_PERIOD = 10;

    logic                clk;
    logic                rst_n;
    logic [WIDTH-1:0]    a;
    logic [WIDTH-1:0]    b;
    logic [2:0]          op;
    logic                valid_in;
    logic [WIDTH-1:0]    result;
    logic                valid_out;
    logic                overflow;

    // Instantiate DUT
    alu #(.WIDTH(WIDTH)) dut (
        .clk(clk),
        .rst_n(rst_n),
        .a(a),
        .b(b),
        .op(op),
        .valid_in(valid_in),
        .result(result),
        .valid_out(valid_out),
        .overflow(overflow)
    );

    // Clock generation
    initial begin
        clk = 0;
        forever #(CLK_PERIOD/2) clk = ~clk;
    end

    // Test sequence
    initial begin
        $dumpfile("alu_tb.vcd");
        $dumpvars(0, alu_tb);

        // Initialize
        rst_n = 0;
        a = 0;
        b = 0;
        op = 0;
        valid_in = 0;
        
        repeat(2) @(posedge clk);
        rst_n = 1;
        @(posedge clk);

        // Test ADD operation
        $display("Testing ADD operation");
        a = 8'd10;
        b = 8'd20;
        op = 3'b000;  // ADD
        valid_in = 1;
        @(posedge clk);
        @(posedge clk);
        $display("ADD: %0d + %0d = %0d", a, b, result);

        // Test SUB operation
        $display("Testing SUB operation");
        a = 8'd50;
        b = 8'd30;
        op = 3'b001;  // SUB
        @(posedge clk);
        @(posedge clk);
        $display("SUB: %0d - %0d = %0d", a, b, result);

        // Test AND operation
        $display("Testing AND operation");
        a = 8'b10101010;
        b = 8'b11001100;
        op = 3'b010;  // AND
        @(posedge clk);
        @(posedge clk);
        $display("AND: %b & %b = %b", a, b, result);

        // Test OR operation
        $display("Testing OR operation");
        op = 3'b011;  // OR
        @(posedge clk);
        @(posedge clk);
        $display("OR: %b | %b = %b", a, b, result);

        // Test overflow
        $display("Testing overflow");
        a = 8'd200;
        b = 8'd100;
        op = 3'b000;  // ADD
        @(posedge clk);
        @(posedge clk);
        $display("ADD with overflow: %0d + %0d = %0d, overflow = %b", a, b, result, overflow);

        // Finish
        repeat(10) @(posedge clk);
        $display("All tests completed!");
        $finish;
    end

    // Timeout watchdog
    initial begin
        #10000;
        $display("ERROR: Simulation timeout!");
        $finish;
    end

endmodule
