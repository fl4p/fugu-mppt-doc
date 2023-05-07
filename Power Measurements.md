# Measurments Equipment

I use to power monitors on bread board.
Both monitors are single-point calibrated with Keithley DMM6500.

A cooling Fan is important. Semiconductors lose conductivity with increasing temperature.
For consistent test results, temperatures must stay constant.

Fugu Idle Power: 1.2W

## Power Monitor 1
- ESP32 
- INA226 with dedicated 3.3V supply (MCP1700 LDO)
- Shunt Resistor CIQI 40A / 75mV 0.5%
- LiPo power supply

## Power Monitor 2
- ESP32-S3
- ADS1117 
- SSA-100
- LiFePo4

![Test Setup](assets/power-test-1/2023-05-04%2016.06.54_anotate.jpg)

# Temperature Considerations
![Test](assets/power-test-1/temperature.png)


# Test 1
Source: Power supply 58V, 4A
Battery: 8s LiFePo4

V_in = 58V
V_out = 27V
I_in = 4090 mA
P_in = 233 W

- Gate Driver: IR2104, 100ohm
- STP150N10F7 MOSfets
- Gate Rise Time: LS: 2.99us, HS: 3.49us
- Coil 1.6mm copper wire (16AWG) with 10cm connection cable 

Result:
Loss = 4.3%


*The 2 power monitors, shunts and the charger with separated coil.*

![Test](assets/power-test-1/TR000087.JPG)
*Thermal image of the PCB and the coil. The lustre terminal at the coil was not properly connected producing a lot of heat (85°C)*

![Test](assets/power-test-1/TR000088.JPG)

# Test 1.1
Changed:
* HS Gate Drive resistor 100 -> 47ohm
* Rise Time 3.39us -> 2.46us

-> Loss = 3.9 % (before: 4.3%)

# Test 1.2
Changed:
* HS replaced STP150N10F7 (4.2mOhm) with IPP024N08NF2SAKMA1 (2.4mOhm) 
* Gate Rise Time: 1.5us
* Gate Fall Time: 0.46us
![Test](assets/power-test-1/test1.1_vg_IPP.png)
* 
-> Loss (cold) = 3.17 %  (before: 3.9%)
-> Loss (hot)  = 3.5 %

# Test 1.3
* 1.8 inductor wire: loss 3.13%

# Test 1.4
double core inductor with 1.6 wire: loss 3.12 %



# Test Series

* V_in=58V
* V_out= 27V (8s lifepo4)
* HW configuration same as Test 1.2
* Various duty cycles.


![Test](assets/power-test-1/eff%20over%20P_in.svg)
*Plot of conversion efficiency over input power*


