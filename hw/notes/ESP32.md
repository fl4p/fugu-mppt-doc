Idle power with WiFi on is 1.3W, which might be a little bit too much for small batteries. Need to figure out how to save energy, disable WiFi, put the ESP32 in deep sleep at night, etc.

It is well known that the internal ADC of the ESP32 series are of bad quality. Noisy and non-linear. This could be fixed through filtering, slower MPPT and calibrating the voltage curve. That's why we use the external ADC on the I2C.

Problem with the I2C on the ESP32 is that it appears to run sequentially to the WiFi routines, so there can be lags of a couple of seconds if WiFi is connected (even without sending any data). This will delay the response of the control loop to unacceptable levels, since it handles overvoltage and overcurrent protection.

I've been trying to improve this but no progress so far. Maybe just need to disable WiFi. Also created a post about it on the esp32 Forum. Still waiting for a response.

I thought about alternatives, and there are STM32 chips featuring a 12-bit ADC that are cheaper than the ADS1015 we use. So why would we use the ADS1015?Going further with the STM32, would put in question the ESP32, because there is STM32W with integrated Bluetooth Low-Energy, which probably would reduce the idle power consumption drastically. STM32 appears to be the more robust also, I perceive ESP32 a bit wonky when it comes to controlling power switches through PWM. 

To put it in other words: ESP32 is nice because it has WiFi, but its WiFi has higher energy consumption compared to BLE,
it distorts the internal ADCs and it blocks the I2C to external ADC.