* On the Esp32-S3, using Arduino's ledc API causes
  error `esp32 s3 requested frequency and duty resolution can not be achieved` with 39 kHz and 11bit precision. 10 bit
  works, but gives poor regulation performance. To fix it, need to directly use ESP32-IDF API `ledc_timer_config`
  and `ledc_channel_config`.
