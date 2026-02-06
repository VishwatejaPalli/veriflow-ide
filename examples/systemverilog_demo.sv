// SystemVerilog demo design for OpenHDL-IDE highlighting tests.
// Shows packages, interfaces, logic types, always_ff/always_comb usage, and modports.

package sv_demo_pkg;
	typedef enum logic [1:0] {
		STATE_IDLE,
		STATE_COUNT,
		STATE_TOGGLE
	} state_t;
endpackage : sv_demo_pkg

interface pulse_if #(parameter int WIDTH = 1)(input logic clk);
	logic [WIDTH-1:0] req;
	logic [WIDTH-1:0] ack;

	modport initiator(
		input clk,
		output req,
		input ack
	);

	modport target(
		input clk,
		input req,
		output ack
	);
endinterface : pulse_if

module systemverilog_demo #(
	parameter int CLK_DIV = 24
) (
	input  logic clk,
	input  logic reset_n,
	output logic led,
	pulse_if.initiator pulse_bus
);
	import sv_demo_pkg::*;

	logic [$clog2(CLK_DIV)-1:0] counter;
	logic toggle_bit;
	state_t state;

	// Simple FSM that toggles an LED after CLK_DIV cycles and drives pulse interface.
	always_ff @(posedge clk or negedge reset_n) begin
		if (!reset_n) begin
			counter    <= '0;
			toggle_bit <= 1'b0;
			state      <= STATE_IDLE;
			pulse_bus.req <= '0;
		end else begin
			unique case (state)
				STATE_IDLE: begin
					state   <= STATE_COUNT;
					counter <= '0;
				end
				STATE_COUNT: begin
					counter <= counter + 1'b1;
					if (counter == CLK_DIV - 1) begin
						state <= STATE_TOGGLE;
					end
				end
				STATE_TOGGLE: begin
					toggle_bit   <= ~toggle_bit;
					pulse_bus.req <= ~pulse_bus.req;
					state        <= STATE_COUNT;
					counter      <= '0;
				end
			endcase
		end
	end

	always_comb begin
		led      = toggle_bit;
		pulse_bus.ack = pulse_bus.req;
	end
endmodule : systemverilog_demo
