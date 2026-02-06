// Simple parametrizable counter
`timescale 1ns/1ps

module simple_counter #(
    parameter WIDTH = 4
) (
    input  wire clk,
    input  wire rst_n,
    output reg  [WIDTH-1:0] value
);
    always @(posedge clk) begin
        if (!rst_n)
            value <= '0;
        else
            value <= value + 1'b1;
    end
endmodule
