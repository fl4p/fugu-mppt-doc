import influxdb
import urllib3.exceptions
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# read from influxdb.env

influxdb_client = influxdb.InfluxDBClient(

    host="influx.fabi.me", username="", password="", ssl=True,
    port=8086,
    #username="hass", password="caravana",
    database='open_pe',
)
power_in_monitor_device = 'ESP32_ADS'
power_out_monitor_device = 'ESP32_INA228'


expected_samples_per_second = 10