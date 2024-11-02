import math
from typing import Tuple, Optional, Iterable

import backoff
import pandas

from ate.config import influxdb_client
from ate.util import get_logger

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
        return f'PwrSampl(%(mean).1f,min=%(min).1f,max=%(max).1f,p2p=%(pp).3f,stddev=%(stddev).3f,count=%(count)i)' % d

    def invert_sign(self):
        self.mean *= -1
        mx = self.max
        self.max = -self.min
        self.min = -mx
        self.I *= -1

    def mul_U(self, k):
        assert 1.1 > k > 0.9
        self.mean *= k
        self.max *= k
        self.min *= k
        self.stddev *= k
        self.U *= k

    def mul_I(self, k):
        assert 1.1 > k > 0.9
        self.mean *= k
        self.max *= k
        self.min *= k
        self.stddev *= k
        self.I *= k


# noinspection SqlDialectInspection
def fetch_power(monitor_device, window, min_count=10):
    q = f"SELECT mean(P),max(P),min(P),stddev(P),count(P) FROM smart_shunt " \
        f"  WHERE time > now() - {window} and device = '{monitor_device}'"
    res = influxdb_client.query(q)

    if not res:
        logger.warning('Empty results for power query %s window=%s', monitor_device, window)
        return None

    row = next(res['smart_shunt'])
    if not (row['count'] > min_count):
        logger.warning('Not enough input power readings %d, want %d', row['count'], min_count)
        return None
    return StatSample(**row)


# noinspection SqlDialectInspection
@backoff.on_exception(backoff.expo, Exception, max_time=60 * 4)
def fetch_power_multi(monitor_devices: Iterable, window, min_count=10, make_positive=False, calibration_gains=None) \
        -> Tuple[Optional[StatSample], ...]:

    if pandas.to_timedelta(window) > pandas.to_timedelta('10s') and not calibration_gains:
        logger.warning('Long measurement but no calibration gains (ignore if you are calibrating')

    devices_where = ' OR '.join(map(lambda d: f" device = '{d}' ", monitor_devices))
    q = f"SELECT mean(P),max(P),min(P),stddev(P),count(P), mean(U) as U, mean(I) as I FROM smart_shunt " \
        f"  WHERE time > now() - {window} and ({devices_where}) GROUP BY device"
    res = influxdb_client.query(q)

    if not res:
        logger.warning('Empty results for power query devices=%s, window=%s', monitor_devices, window)
        return tuple([None] * len(list(monitor_devices)))

    ret = []
    for d in monitor_devices:
        row = next(res['smart_shunt', dict(device=d)], None)
        if row is None:
            logger.warning('Empty results for power query device %s', d)
            ret.append(None)
            continue
        if not (row['count'] > min_count):
            logger.warning('Not enough input power readings %d, want %d', row['count'], min_count)
            ret.append(None)
            continue
        ret.append(StatSample(**row))

    if make_positive and ret[0].mean < 0:
        for r in ret:
            r and r.invert_sign()

    if calibration_gains:
        monitor_devices = list(monitor_devices)
        if len(monitor_devices) != 2:
            raise Exception('only support exactly 2 devices with calibration_gains')

        if calibration_gains['ref'] not in monitor_devices:
            raise Exception('ref %s not in %s' % (calibration_gains, monitor_devices))

        if calibration_gains['dut'] not in monitor_devices:
            raise Exception('dut %s not in %s' % (calibration_gains, monitor_devices))

        dut_idx = 1 if monitor_devices[0] == calibration_gains['ref'] else 0
        ret[dut_idx].mul_U(1 / calibration_gains['u'])
        ret[dut_idx].mul_I(1 / calibration_gains['i'])

    return tuple(ret)


def check_measurement_noise_constraint(p: StatSample, name):
    wifi_pp = 0.5
    wifi_stddev = 0.1

    if abs(p.mean) < 0.001:
        logger.warning('%s mean power too small %.4f', name, p.mean)
        return False

    rpp = p.pp / p.mean
    rpp_max = 0.1 # 0.03
    if rpp > rpp_max and p.pp > wifi_pp: # 0.03
        logger.warning('%s %s peak-2-peak too high %.4f > %.4f', name, p, rpp, rpp_max)
        return False

    rstd = p.stddev / p.mean
    rstd_max = 0.02 # 0.0065
    if rstd > rstd_max and p.stddev > wifi_stddev:
        logger.warning('%s %s stddev too high %.4f > %.4f', name, p, rstd, rstd_max)
        return False

    return True
