// Simple ALU Design for Tool Demonstration
// This file demonstrates SystemVerilog syntax for Verible/Verilator

`timescale 1ns/1ps

module alu #(
    parameter int WIDTH = 8
) (
    input  logic                clk,
    input  logic                rst_n,
    input  logic [WIDTH-1:0]    a,
    input  logic [WIDTH-1:0]    b,
    input  logic [2:0]          op,
    input  logic                valid_in,
    output logic [WIDTH-1:0]    result,
    output logic                valid_out,
    output logic                overflow
);

    // Operation codes
    typedef enum logic [2:0] {
        OP_ADD  = 3'b000,
        OP_SUB  = 3'b001,
        OP_AND  = 3'b010,
        OP_OR   = 3'b011,
        OP_XOR  = 3'b100,
        OP_SLL  = 3'b101,
        OP_SRL  = 3'b110,
        OP_SRA  = 3'b111
    } alu_op_t;

    logic [WIDTH:0] add_result;
    logic [WIDTH:0] sub_result;

    // Combinational logic
    always_comb begin
        overflow = 1'b0;
        add_result = {1'b0, a} + {1'b0, b};
        sub_result = {1'b0, a} - {1'b0, b};
        
        unique case (op)
            OP_ADD: begin
                result = add_result[WIDTH-1:0];
                overflow = add_result[WIDTH];
            end
            OP_SUB: begin
                result = sub_result[WIDTH-1:0];
                overflow = sub_result[WIDTH];
            end
            OP_AND: result = a & b;
            OP_OR:  result = a | b;
            OP_XOR: result = a ^ b;
            OP_SLL: result = a << b[2:0];
            OP_SRL: result = a >> b[2:0];
            OP_SRA: result = $signed(a) >>> b[2:0];
            default: result = '0;
        endcase
    end

    // Pipeline register
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            valid_out <= 1'b0;
        end else begin
            valid_out <= valid_in;
        end
    end

    // Verification checks
    `ifndef SYNTHESIS
    always @(posedge clk) begin
        if (rst_n && (op == OP_AND) && overflow) begin
            $error("Overflow occurred on AND operation");
        end
    end
    `endif

endmodule
