import datetime
import glob
import json
import math
import os.path
import re
import signal
import time
from threading import Thread
from time import sleep

import backoff
import matplotlib.pyplot as plt
import pandas as pd
import serial

from ate.config import influxdb_client, power_out_monitor_device, power_in_monitor_device, expected_samples_per_second
from ate.pwrmon import StatSample, fetch_power_multi, check_measurement_noise_constraint
from ate.util import get_logger

serial_port = sorted(glob.glob('/dev/tty.usbserial-*'))[-1]

# noinspection SqlDialectInspection
temp_query = "SELECT mean(mcu_temp) as temp FROM mppt " \
             "  WHERE time > now() - 20s and device = 'fugu_esp32s3-344082188534'"

# noinspection SqlDialectInspection
ntc_temp_query = "SELECT mean(ntc_temp) as temp FROM mppt " \
                 "  WHERE time > now() - 20s and device = 'fugu_esp32s3-344082188534'"

logger = get_logger()


def fetch_temp(q):
    res = influxdb_client.query(q)
    if not res:
        logger.warning('Temperature not available!')
        return math.nan
    return next(res[res.keys()[0]], dict(temp=math.nan))['temp']


logger.info('Serial port %s', serial_port)
ser = serial.Serial(serial_port, baudrate=115200)

import collections

ser_deque = collections.deque()
ser_last = collections.deque(maxlen=20)


def ser_receive_loop():
    while ser.is_open:
        l = ser.readline()
        ser_deque.append(l)
        ser_last.append(l)
        try:
            l_str = bytes.decode(l, 'utf-8')
        except:
            l_str = str(l)
        # always log errors, warnings
        if 'shutdown' in l_str or 'error' in l_str or 'warn' in l_str or 'disabled' in l_str or 'disabled' in l_str \
                or b'\x1b[0;33mW ' in l or b'\x1b[0;33mE ' in l:
            logger.warning('Ser: %s', l)
        else:
            logger.debug('Ser: %s', l)
    logger.info('ser_receive_loop ends')


Thread(target=ser_receive_loop, daemon=True).start()


@backoff.on_exception(backoff.expo, Exception, max_time=30)
def send_command(cmd):
    if isinstance(cmd, str):
        cmd += '\n'
        cmd = bytes(cmd, 'utf-8')
    # ser.reset_input_buffer()
    # ser.reset_output_buffer()
    ser_deque.clear()
    ser.write(cmd)

    l = ""
    ok_resp = b"OK: " + cmd.strip()
    for _ in range(1, 20):
        while len(ser_deque):
            l = ser_deque.popleft()
            if ok_resp in l.strip():
                return True
        time.sleep(0.1)

    if len(ser_last) == 0:
        logger.info('Never received anything')

    while len(ser_last):
        logger.warning('Ser: %s', ser_last.popleft())

    raise Exception(f"unexpected serial response '{l}' for command '{cmd}")


def set_duty_cycle(duty_cycle):
    cmd = b'dc %d\n' % duty_cycle
    send_command(cmd)
    logger.info('Set duty cycle %d', duty_cycle)


@backoff.on_exception(backoff.expo, Exception, max_time=10)
def fetch_temp_serial():
    while len(ser_deque):
        l = ser_deque.pop()  # consume from the right to get latest temp reading
        m = re.search(r'[\s,]([\-0-9]{1,3})°C', l.decode('utf-8'))
        if m:
            ser_deque.clear()
            return float(m[1])
    raise Exception('temperature not found in serial data')


cancelled = False


def main():
    max_power = 920  # 920
    max_power_shutdown = 960  # 800, 980
    # max_mcu_temp = 70
    max_ntc_temp = 85
    max_loss = 65
    max_input_current = 16.5

    max_duty_cycle = 1024 * 2
    stop_duty_cycle = max_duty_cycle # 940

    # power_step = 50

    duty_cycle = 500
    measurement_time_seconds = 8  # 16/2  # 16

    rows = []

    max_eff = 0
    prev_power_out = 0

    duty_cycle_step = 80
    non_monotonic = []

    while True:
        print('TODO: -query fw version, -pwm freq -device name')
        test_name = input('Enter test name:')
        csv_fn = 'power_test_%s.csv' % test_name
        if os.path.exists(csv_fn):
            logger.error('File exists, please choose a different name')
        else:
            break

    calib_file = 'calibration_gains.json'
    with open(calib_file, 'r') as fp:
        calibration_gains = json.load(fp)

    calibration_time = datetime.datetime.fromtimestamp(os.stat(calib_file).st_mtime)
    if time.time() - calibration_time.timestamp() > 3600 * 24 * 6:
        logger.warning('Calibration file is older than 6d!')

    assert power_in_monitor_device in calibration_gains.values()
    assert power_out_monitor_device in calibration_gains.values()
    logger.info('Loaded calibration file from %s: %s', calibration_time.isoformat(), calibration_gains)

    t_start = time.time()

    sleep(4)
    fetch_temp_serial()  # wait for loop
    send_command("wifi off")

    set_duty_cycle(duty_cycle)
    send_command("ls-enable")  # enable LS-switch (sync buck)
    send_command("bf-enable")

    while not cancelled:
        try:
            set_duty_cycle(duty_cycle)
            # send_command("bf-enable") # close back-flow switch
        except Exception as e:
            logger.warning('Failed to set duty cycle: %s. Retry.', e)
            sleep(2)
            continue

        # skip first 3 seconds settling time (e.g. LS duty cycle fade-in)
        sleep(3)

        # quick power check to see if we need to reduce duty cycle step size
        power_in, power_out = fetch_power_multi((power_in_monitor_device, power_out_monitor_device),
                                                window='%.0fms' % (1000 * 3),
                                                min_count=round(expected_samples_per_second * 0.5 * 2),
                                                make_positive=True, calibration_gains=calibration_gains
                                                )
        if prev_power_out and power_in and power_out and duty_cycle_step > 1 and (
                (power_out.mean / prev_power_out > 1.8 and power_out.mean - prev_power_out > 35)
                or power_in.mean > max_power_shutdown
        ):
            logger.info("Power step too big (prev %.1fW, now %.1fW), dec step size %d", prev_power_out, power_out.mean,
                        duty_cycle_step)
            duty_cycle -= duty_cycle_step
            duty_cycle_step = max(1, round(duty_cycle_step / 4))
            if power_out.mean - prev_power_out > 300:
                duty_cycle_step = min(duty_cycle_step, 8)
            duty_cycle += duty_cycle_step
            # TODO instead of discarding the measurement, keep it, go back and skip
            continue

        if power_in and power_in.mean > max_power_shutdown:
            logger.info('Reached max power (shutdown)')
            break

        sleep(measurement_time_seconds)

        power_in: StatSample
        power_out: StatSample

        power_in, power_out = fetch_power_multi((power_in_monitor_device, power_out_monitor_device),
                                                window='%.0fms' % (measurement_time_seconds * 1000),
                                                min_count=expected_samples_per_second * measurement_time_seconds,
                                                make_positive=True,
                                                calibration_gains=calibration_gains
                                                )

        if not power_in or not power_out:
            logger.warning('missing power readings, retry')
            continue

        if not check_measurement_noise_constraint(power_in, 'in') or not \
                check_measurement_noise_constraint(power_out, 'out'):
            send_command("wifi off")
            continue

        if power_out.mean < prev_power_out - max(power_out.stddev, 0.05):
            logger.error('Power(out) not monotonic increasing (prev %.2fW, now %.2fW)', prev_power_out, power_out.mean)
            logger.error('Power supply current limited or diode emulation failure?')
            non_monotonic.append((duty_cycle, power_out.mean, prev_power_out))
            # continue

        if prev_power_out and (power_out.mean / prev_power_out < 1.08 or power_out.mean - prev_power_out < 4):
            logger.info("Power step small (prev %.1fW, now %.1fW), inc step size %d", prev_power_out, power_out.mean,
                        duty_cycle_step)
            duty_cycle_step = min(round((5 + duty_cycle_step) * 1.5), 160 if power_out.mean > 200 else 80)
        elif prev_power_out and power_out.mean > 200 and power_out.mean / prev_power_out < 1.25:
            duty_cycle_step += 3

        prev_power_out = power_out.mean

        # mcu_temp = fetch_temp(temp_query)
        # ntc_temp = fetch_temp(ntc_temp_query)
        ntc_temp = fetch_temp_serial()

        eff = power_out.mean / power_in.mean
        loss = power_in.mean - power_out.mean
        loss_pct = (power_in.mean - power_out.mean) / power_in.mean

        logger.info('DC=%4i P_in=%6.1f  Eff = %.2f%%, Loss = %4.2f%% (%3.1fW), Temp(MCU/NTC)= %.1f°C / %.1f°C',
                    duty_cycle,
                    power_in.mean,
                    eff * 100, loss_pct * 100, loss, math.nan, ntc_temp)

        if eff > max_eff:
            max_eff = eff

        row = dict(
            DS=duty_cycle,

            V_in=power_in.U,
            I_in=power_in.I,
            P_in=power_in.mean,

            V_out=power_out.U,
            I_out=power_out.I,
            P_out=power_out.mean,

            eff=eff,
            # temp=mcu_temp,
            ntc_temp=ntc_temp,
            time=math.ceil(time.time() - t_start),
        )

        rows.append(row)

        if power_in.mean >= max_power:
            logger.info('Reached max power')
            break

        # if mcu_temp > max_mcu_temp:
        #    logger.info('Reached max mcu temp')
        #    break

        if ntc_temp > max_ntc_temp:
            logger.info('Reached max ntc temp')
            break

        if loss > max_loss:
            logger.info('Reached max loss')
            break

        if power_in.I > max_input_current:
            logger.info('Reached max input current')
            break

        v_ratio = power_out.U / power_in.U
        duty_cycle_buck_knee = v_ratio * max_duty_cycle + 50

        if duty_cycle < duty_cycle_buck_knee and (
                duty_cycle + duty_cycle_step) > duty_cycle_buck_knee and power_out.mean < 100:
            logger.info('Crossing knee point %d', duty_cycle_buck_knee)
            # duty_cycle_step = min(duty_cycle_step, 20)  # max(1, int(duty_cycle_buck_knee - duty_cycle))
            duty_cycle_step = min(duty_cycle_step, max(1, int(duty_cycle_buck_knee - duty_cycle - 1)))  # -5

        duty_cycle_step = min(duty_cycle_step, min(stop_duty_cycle, max_duty_cycle) - duty_cycle)
        if duty_cycle_step <= 0:
            logger.info('Reached max duty cycle %i', stop_duty_cycle)
            break

        duty_cycle += duty_cycle_step

    logger.info('Test finished after %.1f seconds', time.time() - t_start)

    if non_monotonic:
        logger.warning('Non-monotonic increasing power steps:')
        for (dc, p, p_prev) in non_monotonic:
            logger.warning("At duty cycle %d, %.1fW power (prev %.1fW)", dc, p, p_prev)

    if len(rows) > 1:
        df = pd.DataFrame(rows).round(4)

        df.to_csv(csv_fn)
        logger.info('Wrote %s', csv_fn)

        s = pd.Series(df.eff.values, index=df.P_out.values)
        s.plot(marker='.')
        plt.xlabel('P_in')
        plt.ylabel('eff')
        plt.grid(1)
        plt.title('max eff %.2f%% @ %.1fW' % (s.max() * 100, s.index[s.argmax()]))
        plt.savefig('power_test_%s_eff_curve.png' % test_name)


def signal_handler(_sig, _frame):
    global cancelled
    logger.info('You pressed Ctrl+C!')
    cancelled = True


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    main()
finally:
    set_duty_cycle(200)
