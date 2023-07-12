# Serial Commands

You can send commands to the Fugu Device over the serial port. Type the command in the serial monitor and then press
enter. The device will acknowledge the command.

* `reset`: Restart the ESP32 MCU
* `dt X`: disable MPP-Tracking and set manual duty cycle (example `dt 500`)
* `+X` and `-X`: increases and decreases the duty cycle by `X` steps (example: `+1`)
* `mppt`: enable MPP tracking (after manual duty cycle)
* `sweep`: starts a full scan to find the MPP

You can use the commands for manual testing and scripting.

## Examples
set DCDC PWM duty cycle to 400:
```
dt 400 
```

Increase duty cycle by 20:
```
+20
```

Decrease duty cycle by 20:
```
-20
```

Go back to MPPT tracking:
```
mppt
```
