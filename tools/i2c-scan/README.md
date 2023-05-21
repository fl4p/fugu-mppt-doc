This app frequently scans addresses from 0 to 0x7F (127).

It'll try to send 0 bytes to any address using `i2c_master_write_byte` and checks for an ACK.

# Building

Make sure environment variable `$IDF_PATH` points to `esp-idf` path.

```
. $IDF_PATH/export.sh
idf.py build
```
