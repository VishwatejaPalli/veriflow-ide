# Netgen LVS Setup File
# Configure device matching rules

permute default
property default
ignore class c
ignore class r

# Equivalence classes
equate "-circuit1 nmos" "-circuit2 nmos"
equate "-circuit1 pmos" "-circuit2 pmos"

# Flatten hierarchies if needed
# flatten class {mymodule}

# Set tolerances
property "w" tolerance 0.01
property "l" tolerance 0.01
