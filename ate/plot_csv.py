files = [
    #'power_test_22khz_2ccoil_diodeFix.csv',
   # 'power_test_22khz_2ccoil_diodeFix2.csv',
   # 'power_test_29khz_2ccoils.csv',

    #'power_test_39khz_2ccoil.csv',

    #'power_test_39khz_2ccoil_20230517.csv',
    #'power_test_39khz_2ccoil_TK6R8A08QM.csv',
    #'power_test_39khz_2ccoil_TK6R8A08QM_100r.csv',

    'power_test_39khz_2ccoil_TK6R8A08QM_100r_2.csv',
    'power_test_39khz_2ccoil_TK6R8A08QM_50r.csv',
    'power_test_39khz_2ccoil_TK6R8A08QM_100r_3.csv',
    'power_test_39khz_2ccoil_TK6R8A08QM_50r_2.csv',
    'power_test_fugu_boxed01.csv',
    #'power_test_22khz_2ccoil_diodeFix3.csv',
]

import matplotlib.pyplot as plt
import pandas as pd

seriess = {}
for fn in files:
    df = pd.read_csv('results/'+fn)
    s = pd.Series(df.eff.values, index=df.P_out.values)
    label = fn.split('.')[0].replace('power_test_','').replace('_', ' ')
    label += ' Uo=%.1fV' % df.V_out.mean()
    s.plot(label=label, marker='.')

plt.xlabel('P_in')
plt.ylabel('eff')
plt.grid(1, which="both")
plt.legend()
#plt.semilogx()
plt.show()
