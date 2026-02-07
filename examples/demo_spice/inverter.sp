* Simple CMOS Inverter for NgSpice Demonstration
* This demonstrates analog simulation

.title CMOS Inverter Test

* Supply voltage
.param vdd_val=1.8

* MOSFET Models (simplified)
.model nmos_model nmos (level=1 vto=0.4 kp=200u lambda=0.02)
.model pmos_model pmos (level=1 vto=-0.4 kp=100u lambda=0.02)

* Circuit netlist
vdd vdd 0 dc {vdd_val}
vin in 0 pulse(0 {vdd_val} 1n 100p 100p 5n 10n)

* Inverter
mn out in 0 0 nmos_model w=1u l=180n
mp out in vdd vdd pmos_model w=2u l=180n

* Load capacitance
cl out 0 10f

* Analysis
.tran 100p 30n
.print tran v(in) v(out)

* Measure propagation delay
.meas tran tphl trig v(in) val={vdd_val/2} fall=1 targ v(out) val={vdd_val/2} fall=1
.meas tran tplh trig v(in) val={vdd_val/2} rise=1 targ v(out) val={vdd_val/2} rise=1

* Save results
.control
run
* plot v(in) v(out)  [disabled for batch mode]
write inverter_output.raw
quit
.endc

.end
