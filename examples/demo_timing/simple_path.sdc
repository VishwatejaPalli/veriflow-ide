# SDC (Synopsys Design Constraints) for OpenSTA
# This demonstrates timing constraints

# Clock definition
create_clock -name clk -period 10.0 [get_ports clk]

# Input/Output delays
set_input_delay -clock clk -max 2.0 [get_ports {a b op valid_in}]
set_input_delay -clock clk -min 1.0 [get_ports {a b op valid_in}]

set_output_delay -clock clk -max 3.0 [get_ports {result valid_out overflow}]
set_output_delay -clock clk -min 1.0 [get_ports {result valid_out overflow}]

# Clock uncertainty (jitter)
set_clock_uncertainty -setup 0.5 [get_clocks clk]
set_clock_uncertainty -hold 0.3 [get_clocks clk]

# Transition times
set_clock_transition 0.1 [get_clocks clk]

# Load constraints
set_load 0.1 [all_outputs]

# Drive strength
set_driving_cell -lib_cell BUF_X1 [all_inputs]
