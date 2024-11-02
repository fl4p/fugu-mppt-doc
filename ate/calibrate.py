import datetime
import json
import os.path
import sys
import time

from ate.config import power_in_monitor_device, power_out_monitor_device, expected_samples_per_second, influxdb_client
from ate.pwrmon import StatSample, fetch_power_multi, check_measurement_noise_constraint
from ate.util import get_logger

logger = get_logger()


def log_gains(gains):
    now = datetime.datetime.utcnow()
    points = [{
        "measurement": 'calibration',
        "time": now,
        "fields": gains,
        "tags": dict(ref=gains['ref'])
    }]
    res = influxdb_client.write_points(points, time_precision='ms')
    assert res


def main():
    measurement_time_seconds = 120 # 120

    calibration_gains = dict()

    power_in: StatSample
    power_out: StatSample

    logger.info('Reference is %s', power_in_monitor_device)

    if os.path.exists('calibration_gains.json'):
        with open('calibration_gains.json', 'r') as fp:
            log_gains(json.load(fp))

    skip_confirm = False
    while not (calibration_gains.get('u') and calibration_gains.get('i')):
        sys.stdin.flush()
        logger.handlers[0].flush()
        sys.stdout.flush(), sys.stderr.flush()
        time.sleep(0.1)
        skip_confirm or input('Press ENTER to proceed\n')
        skip_confirm = False
        sys.stdout.flush(), sys.stderr.flush()
        logger.info('%d seconds...', measurement_time_seconds)
        time.sleep(measurement_time_seconds)

        power_in, power_out = fetch_power_multi((power_in_monitor_device, power_out_monitor_device),
                                                window='%.0fms' % (measurement_time_seconds * 1000),
                                                min_count=expected_samples_per_second * measurement_time_seconds,
                                                make_positive=True,
                                                # calibration_gains={"u": 0.9992967, "i": 0.99908488, "ref": "ESP32_ADS", "dut": "ESP32_INA226"}
                                                )

        if not check_measurement_noise_constraint(power_in, "input") or \
                not check_measurement_noise_constraint(power_out, "out"):
            logger.warning('Measurement constraints not met, retry in 4s')
            time.sleep(4)
            skip_confirm = True
            continue

        logger.info('in: %s', power_in)
        logger.info('out: %s', power_out)

        if abs(power_in.I) > 0.01 or abs(power_out.I) > 0.01:
            if 'i' in calibration_gains:
                logger.error('Current already calibrated, please open circuit and try again')
                continue

            if abs(power_in.I) < 1 or abs(power_out.I) < 1:
                logger.error('Current too small!')
                continue

            logger.info('Iin=%.4fA Iout=%.4fA', power_in.I, power_out.I)
            logger.info('Iout/Iin=%.5f (%+.3f %%)', power_out.I / power_in.I,
                        (power_out.I - power_in.I) / power_in.I * 100)

            gain = round(power_out.I / power_in.I, 8)

            if gain < 0.95 or gain > 1.05:
                logger.error('currents too different!')
                continue

            calibration_gains['i'] = round(power_out.I / power_in.I, 8)
            calibration_gains['I_ref'] = round(power_in.I, 4)
        else:
            if 'u' in calibration_gains:
                logger.info('Voltage already calibrated, please close circuit and try again')
                continue

            logger.info('Vin=%.4fV Vout=%.4fV', power_in.U, power_out.U)
            logger.info('Vout/Vin=%.5f (%+.5f %%)', power_out.U / power_in.U,
                        (power_out.U - power_in.U) / power_in.U * 100)

            if power_out.U / power_in.U > 1.05 or power_out.U / power_in.U < 0.95:
                logger.error('Voltages too different!')
                continue

            calibration_gains['u'] = round(power_out.U / power_in.U, 8)
            calibration_gains['U_ref'] = round(power_in.U, 4)

    logger.info('Calibration complete, gains: %s', calibration_gains)

    calibration_gains['ref'] = power_in_monitor_device
    calibration_gains['dut'] = power_out_monitor_device

    if os.path.exists('calibration_gains.json'):
        with open('calibration_gains.json', 'r') as fp:
            print('prev gains:', json.load(fp))
        os.rename('calibration_gains.json', 'calibration_gains.json.prev')

    with open('calibration_gains.json', 'w') as fp:
        json.dump(calibration_gains, fp)

    logger.info('Wrote calibration_gains.json')

    log_gains(calibration_gains)


main()
