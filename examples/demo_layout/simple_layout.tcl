# Magic Layout TCL Script
# This script demonstrates layout operations in Magic

# Create a simple layout
box 0 0 100 100
paint ndiff
label "drain" s

box 0 110 100 210
paint pdiff
label "source" s

box 40 220 60 280
paint poly
label "gate" s

# Add contacts
box 40 40 60 60
paint ndc

box 40 150 60 170
paint pdc

# Save the layout
save simple_cell

# Generate SPICE netlist
extract all
ext2spice lvs
ext2spice

puts "Layout created and extracted!"
