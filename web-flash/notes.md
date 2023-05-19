# Instructions
- https://esphome.github.io/esp-web-tools/

# Create Single .bin firmware

This is an example how to use Arduino IDE build output with the web flasher.
* `sketch_name` is the name of the Arduino sketch
* `sketch_build_folder` you'll find this in the build logs
* `boot_bin` this is usually `boot_app0.bin` from the esp32 SDK

```

esptool=$HOME/Library/Arduino15/packages/esp32/tools/esptool_py/4.5.1/esptool 

sketch_name=fugu-mppt-firmware.ino
sketch_build_folder=/private/var/folders/nl/jtl1vjrd30b9y_r9gbv3sjsc0000gn/T/arduino/sketches/E02D8E02D452FAB8BCD77602569FADEA
boot_bin=$HOME/Library/Arduino15/packages/esp32/hardware/esp32/2.0.9/tools/partitions/boot_app0.bin


$esptool --chip esp32 merge_bin \
  -o merged-firmware.bin \
  --flash_mode dio \
  --flash_freq 80m \
  --flash_size 4MB \
  0x1000 $sketch_build_folder/$sketch_name.bootloader.bin \
  0x8000 $sketch_build_folder/$sketch_name.partitions.bin \
  0xe000 $boot_bin \
  0x10000 $sketch_build_folder/$sketch_name.bin

```


# PlatformIO

Run `pio run -v -e $env -t upload` and look for `esptool.py` in the log output to find the upload command.


```     
chip=esp32s3
variant=$chip # adafruit_feather_esp32s3
env=e1_esp32s3dev
arduino_esp_sdk=$HOME/.platformio/packages/framework-arduinoespressif32
  
$esptool --chip esp32s3 merge_bin \
  -o merged-$env.bin \
  --flash_mode dio \
  --flash_freq 80m \
  --flash_size 4MB \
  0x0000 $arduino_esp_sdk/variants/adafruit_feather_esp32s3/bootloader-tinyuf2.bin \
  0x8000 .pio/build/$env/partitions.bin \
  0xe000 $arduino_esp_sdk/tools/partitions/boot_app0.bin \
  0x2d0000 $arduino_esp_sdk/variants/$variant/tinyuf2.bin \
  0x10000 .pio/build/$env/firmware.bin

```