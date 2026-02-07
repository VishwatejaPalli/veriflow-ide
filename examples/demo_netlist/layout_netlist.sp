* Layout-extracted netlist for LVS
* This represents the physical layout

.subckt inverter in out vdd gnd
M1 out in gnd gnd nmos w=1.0u l=0.18u
M2 out in vdd vdd pmos w=2.0u l=0.18u
C1 out gnd 5f
.ends

* Test circuit
X1 input output vdd gnd inverter

.end
