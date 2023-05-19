

# Coil Current

Measuring the current through the coil can help debugging diode emulation of the Low-Side switch.
If diode emulation fails, the Low-Side switch is on for too long and the current crosses zero, becoming negative.
This can destroy the switch due to excess current. It can also generate dangerously high voltages at the buck
input terminals, because it will turn the buck into a (reverse) boost converter.

![Test Setup](../assets/coil-current/test-setup.jpg)
*Measuring coil current with a current clamp and coil voltage with a differential probe*



Here is a series of coil current (red) and voltage (green) wave forms for various High-Side and Low-Side duty cycles. 

* V_in 40V
* V_out = 26.5V
* PWM_MAX 2048 (11bit)

`PWM(H|L)=   0| 123`:
![scope](../assets/coil-current/scope_29.png)

`PWM(H|L)=   123| 123`:
![scope](../assets/coil-current/scope_30.png)

`PWM(H|L)=   200| 123`:
![scope](../assets/coil-current/scope_31.png)

`PWM(H|L)= 600| 123`: (I_in=200mA)
![scope](../assets/coil-current/scope_42.png) 

`PWM(H|L)= 800| 361`:
![scope](../assets/coil-current/scope_34.png)

`PWM(H|L)=1000| 450`:
![scope](../assets/coil-current/scope_35.png)

`PWM(H|L)=1200| 543`: (I_in=600ma)
![scope](../assets/coil-current/scope_44.png)

`PWM(H|L)=1250| 566`:
![scope](../assets/coil-current/scope_45.png)

`PWM(H|L)=1390| 629`: (coil current starts to "lift-off")
![scope](../assets/coil-current/scope_46.png)

`PWM(H|L)=1400| 624`
![scope](../assets/coil-current/scope_47.png)

