import math
from time import sleep
from typing import Iterable, Tuple

import influxdb
import pandas as pd
import serial

from ate.util import get_logger

serial_port = '/dev/tty.usbserial-110'

influxdb_client = influxdb.InfluxDBClient(
    host='homeassistant.local',
    port=8086,
    username="home_assistant", password="h0me",
    # username="hass", password="caravana",
    database='open_pe',
)
power_in_monitor_device = 'ESP32_ADS'
power_out_monitor_device = 'ESP32_INA226'
temp_query = "SELECT mean(mcu_temp) as temp FROM mppt " \
             "  WHERE time > now() - 20s and device = 'esp32_proto_mppt_esp32s3-70408218853'"

logger = get_logger()


class StatSample:
    def __init__(self, mean, max, min, stddev, count, U=math.nan, I=math.nan, time=None):
        self.mean = mean
        self.max = max
        self.min = min
        self.stddev = stddev
        self.count = count
        self.time = time

        self.U = U
        self.I = I

    @property
    def pp(self):
        """
        Peak-to-Peak
        :return:
        """
        return self.max - self.min

    def __str__(self):
        d = dict(pp=self.pp)
        d.update(self.__dict__)
        return f'PwrSampl(%(mean).1f,min=%(min).1f,max=%(max).1f,pp=%(pp).3f,stddev=%(stddev).3f,count=%(count)i)' % d

    def invert_sign(self):
        self.mean *= -1
        mx = self.max
        self.max = -self.min
        self.min = -mx
        self.I *= -1


def fetch_power(monitor_device, window, min_count=10):
    q = f"SELECT mean(P),max(P),min(P),stddev(P),count(P) FROM smart_shunt " \
        f"  WHERE time > now() - {window} and device = '{monitor_device}'"
    res = influxdb_client.query(q)

    if not res:
        logger.warning('Empty results for power query')
        return None

    row = next(res['smart_shunt'])
    if not (row['count'] > min_count):
        logger.warning('Not enough input power readings %d, want %d', row['count'], min_count)
        return None
    return StatSample(**row)


def fetch_power_multi(monitor_devices: Iterable, window, min_count=10) -> Tuple[StatSample, StatSample]:
    devices_where = ' OR '.join(map(lambda d: f" device = '{d}' ", monitor_devices))
    q = f"SELECT mean(P),max(P),min(P),stddev(P),count(P), mean(U) as U, mean(I) as I FROM smart_shunt " \
        f"  WHERE time > now() - {window} and ({devices_where}) GROUP BY device"
    res = influxdb_client.query(q)

    if not res:
        logger.warning('Empty results for power query')
        return None

    ret = []
    for d in monitor_devices:
        row = next(res['smart_shunt', dict(device=d)], None)
        if row is None:
            logger.warning('Empty results for power query device %d', d)
            ret.append(None)
            continue
        if not (row['count'] > min_count):
            logger.warning('Not enough input power readings %d, want %d', row['count'], min_count)
            ret.append(None)
            continue
        ret.append(StatSample(**row))

    return ret


def fetch_temp():
    res = influxdb_client.query(temp_query)
    return next(res[res.keys()[0]], dict(temp=math.nan))['temp']


ser = serial.Serial(serial_port, baudrate=115200)


def set_duty_cycle(duty_cycle):
    cmd = b'dc %d\n' % duty_cycle
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(cmd)

    l = ""
    for _ in range(1, 5):
        l = ser.readline()
        if cmd.strip() in l.strip():
            return True
        # logger.warning('received data %s', l)

    raise Exception('unexpected serial data %s' % l)


def check_measurement_noise_constraint(p: StatSample, name):
    rpp = p.pp / p.mean
    if rpp > 0.02:
        logger.warning('%s %s peak-2-peak too high %.4f', name, p, rpp)
        return False

    rstd = p.stddev / p.mean
    if rstd > 0.005:
        logger.warning('%s %s stddev too high %.4f', name, p, rstd)
        return False

    return True


def main():
    max_power = 500
    max_duty_cycle = 1024 * 2

    # power_step = 50

    duty_cycle = 400
    measurement_time_seconds = 8
    expected_samples_per_second = 10

    rows = []

    while True:
        logger.info('Set duty cycle %d', duty_cycle)
        set_duty_cycle(duty_cycle)

        sleep(2 + measurement_time_seconds)

        power_in: StatSample
        power_out: StatSample

        power_in, power_out = fetch_power_multi((power_in_monitor_device, power_out_monitor_device),
                                                window='%.0fms' % (measurement_time_seconds * 1000),
                                                min_count=expected_samples_per_second * measurement_time_seconds)

        if not power_in or not power_out:
            logger.warning('missing power readings')
            continue

        if power_in.mean < 0:
            power_in.invert_sign()
            power_out.invert_sign()

        if not check_measurement_noise_constraint(power_in, 'in') or not \
                check_measurement_noise_constraint(power_out, 'out'):
            continue

        # print(power_in)
        # print(power_out)

        temp = fetch_temp()

        eff = power_out.mean / power_in.mean
        loss_pct = (power_in.mean - power_out.mean) / power_in.mean
        logger.info('DS=%4i P_in=%4.1f  Eff = %.2f%%, Loss = %.2f%%,  Temp = %.1f°C', duty_cycle, power_in.mean,
                    eff * 100, loss_pct * 100, temp)

        row = dict(
            DS=duty_cycle,

            V_in=power_in.U,
            I_in=power_in.I,
            P_in=power_in.mean,

            V_out=power_out.U,
            I_out=power_out.I,
            P_out=power_out.mean,

            eff=eff,
            temp=temp,
        )

        rows.append(row)

        if power_in.mean >= max_power:
            logger.info('Reached max power')
            break

        if duty_cycle < 950:
            duty_cycle += 50
        elif duty_cycle < 975:
            duty_cycle += 5
        else:
            duty_cycle += 1

        if duty_cycle > max_duty_cycle:
            break

    set_duty_cycle(200)

    df = pd.DataFrame(rows).round(4)
    df.to_csv('power_test.csv')


main()

"""
- check temp
- check stddev
- check peak2peak
- check data availability
"""
