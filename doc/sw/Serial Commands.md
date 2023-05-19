# Serial Commands

You can send commands to the Fugu Device over the serial port. Type the command in the serial monitor and then press
enter. The device will acknowledge the command.

* `reset`: Restart the ESP32 MCU
* `dt X`: disable MPP-Tracking and set manual duty cycle (example `dt 500`)
* `+X` and `-X`: increases and decreases the duty cycle by `X` steps (example: `+1`)
* `sweep`