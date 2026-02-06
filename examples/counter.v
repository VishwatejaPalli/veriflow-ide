// Simple 4-bit counter with synchronous reset
module counter(
    input wire clk,
    input wire rst_n,
    output reg [3:0] value
);
    always @(posedge clk) begin
        if (!rst_n) begin
            value <= 4'd0;
        end else begin
            value <= value + 4'd1;
        end
    end
endmodule
