# Instructions
- https://esphome.github.io/esp-web-tools/

# Create Single .bin firmware

```

esptool=$HOME/Library/Arduino15/packages/esp32/tools/esptool_py/4.5.1/esptool 

sketch_name=fugu-mppt-fw.ino
sketch_build_folder=/private/var/folders/nl/jtl1vjrd30b9y_r9gbv3sjsc0000gn/T/arduino/sketches/4F3E39EE5F9472F09B33E5FD2884F799
boot_bin=$HOME/Library/Arduino15/packages/esp32/hardware/esp32/2.0.7/tools/partitions/boot_app0.bin


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