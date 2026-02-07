* RC Circuit for Time Constant Measurement
* Demonstrates AC and transient analysis

.title RC Low-Pass Filter

* Circuit components
vin in 0 dc 0 ac 1 pulse(0 5 0 1n 1n 500n 1u)
r1 in out 1k
c1 out 0 1u

* DC Analysis
.dc vin 0 5 0.1
.print dc v(out)

* AC Analysis (frequency response)
.ac dec 10 1 1meg
.print ac vdb(out) vp(out)

* Transient Analysis
.tran 10n 3u
.print tran v(in) v(out)

* Measurements
.meas tran vout_max max v(out)
.meas tran tau_rc when v(out)=3.16

.control
run
* plot db(v(out))  [disabled for batch mode]
* plot v(in) v(out)  [disabled for batch mode]
.endc

.end
