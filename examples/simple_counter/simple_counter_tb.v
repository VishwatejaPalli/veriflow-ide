`timescale 1ns/1ps

module simple_counter_tb;
    localparam WIDTH = 4;

    reg clk = 0;
    reg rst_n = 0;
    wire [WIDTH-1:0] value;

    simple_counter #(.WIDTH(WIDTH)) dut (
        .clk(clk),
        .rst_n(rst_n),
        .value(value)
    );

    // Clock generation
    always #5 clk = ~clk; // 100 MHz clock

    initial begin
        $dumpfile("examples/simple_counter/simple_counter.vcd");
        $dumpvars(0, simple_counter_tb);

        $display("Starting simulation...");
        rst_n = 0;
        #20;
        rst_n = 1;

        repeat (20) begin
            @(posedge clk);
            $display("time=%0t value=%0d", $time, value);
        end

        $display("Simulation done.");
        $finish;
    end
endmodule
