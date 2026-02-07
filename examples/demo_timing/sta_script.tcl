
# Read liberty files (you'll need actual .lib files for real analysis)
# read_liberty example.lib

# Read Verilog netlist
read_verilog ../demo_alu/alu_synth.v

# Link design
link_design alu

# Read constraints
read_sdc simple_path.sdc

# Report timing
report_checks -path_delay max -format full_clock_expanded
report_checks -path_delay min -format full_clock_expanded

# Report other metrics
report_check_types -max_slew -max_capacitance -max_fanout
report_clock_skew

# Report summary
report_tns
report_wns

puts "Timing analysis complete!"
