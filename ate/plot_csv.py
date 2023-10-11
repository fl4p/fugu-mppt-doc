files = [
    # 'power_test_22khz_2ccoil_diodeFix.csv',
    # 'power_test_22khz_2ccoil_diodeFix2.csv',
    # 'power_test_29khz_2ccoils.csv',

    # 'power_test_39khz_2ccoil.csv',

    # 'power_test_39khz_2ccoil_20230517.csv',
    # 'power_test_39khz_2ccoil_TK6R8A08QM.csv',
    # 'power_test_39khz_2ccoil_TK6R8A08QM_100r.csv',

    # 'power_test_39khz_2ccoil_TK6R8A08QM_100r_2.csv',
    # 'power_test_39khz_2ccoil_TK6R8A08QM_50r.csv',
    # 'power_test_39khz_2ccoil_TK6R8A08QM_100r_3.csv',
    # 'power_test_39khz_2ccoil_TK6R8A08QM_50r_2.csv',
    #
    # 'power_test_22khz_2ccoil_diodeFix3.csv',

    # 'power_test_fblab2_40v.csv',
    # 'power_test_flab_50v.csv',
    # 'power_test_flab_50v_vre0.1.csv',
    # 'power_test_flab_40v_vre01.csv',

    # 'power_test_fugu_boxed01.csv',
    # 'power_test_fb5.csv',
    # 'power_test_fb10.csv',

    ##'power_test_flab_2cLTK6R8.csv',
    ##'power_test_flab_14L_TK6R8.csv',

    # 'power_test_flab_16Lnw_TK6R8.csv',
    # 'power_test_flab_16Lnw_TK6R8_G25r.csv',
    # 'power_test_flab_16Lnw_IPP_G25r.csv',

    # 'power_test_flab_182cL_IPP.csv',
    # 'power_test_flab_182cL_IPP_FDP.csv',
    # 'power_test_flab_182cL_TK6R8_FDP.csv',# pick

    # 'power_test_flab_14Lnw_TK6R8_G25r.csv',
    # 'power_test_flab_14Lnw2_TK6R8_G25r.csv',

    # 'power_test_flab_eo1.csv',
    # 'power_test_flab_eo2.csv',
    # 'power_test_flab_eo3.csv',
    # 'power_test_flab_eo4.csv',
    # 'power_test_flab_eo5.csv',
    # 'power_test_flab_eo6.csv',
    # 'power_test_flab_eo7.csv',
    # 'power_test_flab_eo1_1.csv',
    # 'power_test_fbox2.csv',
    # 'power_test_fbox2_cap1.csv',

    # 'power_test_fbox1_rep.csv',
    # 'power_test_fbox2.2.csv',

    # 'power_test_flab_eo7.csv',
    #'power_test_flab_eo8.csv', # pick
    # 'power_test_flab_eo8_cap10tdk.csv',
    # 'power_test_flab_cap20.csv',
    # 'power_test_flab_cap40.csv',
    # 'power_test_flab_2ruby.csv',
    #'power_test_f2.csv', # noise, ringing
    #'power_test_f2_15.csv',
    #'power_test_f2_1hs15.csv', # 1HS fet 150N10F7, T184 coil, 22R gate
    #'power_test_f2_1hs15_11r.csv', # like f2_1hs15 but 11R gate and BF-short
    #'power_test_f2_1hs15_11r_2.csv', # repeat, vin calib,  LS disable

#'power_test_f2_1hs15_11r_5.csv', # repeat, vin calib, LS disable
#'power_test_f2_1hs15_11r_6.csv', # repeat, vin calib,  LS disable
   # 'power_test_f2_1hs15_7r.csv', # 7R HS gate
   # 'power_test_f2_1hs15_11r_3.csv',  # 11R HS gate
   # 'power_test_f2_1hs15_22r.csv', # 22R

    #'power_test_f2_2hs15TK_22r.csv', # 2HS (STP150N10F7 g@22r + TK6R8A g@22r)
    #'power_test_f2_2hs15TK_11r.csv', # 2HS (STP150N10F7 g@22r + TK6R8A g@11r)
    #'power_test_2hs15TK_11r22r.csv', # 2HS (STP150N10F7 g@11r + TK6R8A g@22r)
    #'power_test_2hs15TK_11r11r.csv', # both at 11r, with 2p bflow CDS19505

    #'power_test_f2a.csv',
    #'power_test_f2wrap2.csv',
    #'power_test_f2w8.csv',
    #'power_test_f2w9.csv',


    # from here pwr-mon: ads1115 (16bit), ina228(20bit), precision R, calibrated
    # forget everything before

    'power_test_f2p3.csv', # f2 wrapped T184 (2xHS TK 22r)
    'power_test_f2p5.csv', # f2 wrapped 2staked T120 (1xHS Tk 10r)
    'power_test_f2met.csv', # f2 in aluminum case (2xHS TK 22r), coil: 2T130, 2x1.8mm
    'power_test_f2m_nobatwire2.csv', # like before but bat voltage sense at PCB
]

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use('MacOSX')

#plt.figure()
plt.subplot(211)

dfs = {}
for fn in files:
    df = pd.read_csv('results/' + fn)
    df = df[df.P_out > 1]
    s = pd.Series(df.eff.values, index=df.P_out.values)
    label = '.'.join(fn.split('.')[:-1]).replace('power_test_', '').replace('_', ' ')
    label += ' U(io)=%.1f|%.1fV' % (df.V_in.mean(), df.V_out.mean())
    dfs[label] = df
    s.plot(label=label, marker='.')

plt.xlabel('P_in')
plt.ylabel('eff %')
plt.grid(1, which="both")
plt.legend()
# plt.semilogx()
plt.ylim((0.93, 0.99))


plt.subplot(212)

for label,df in dfs.items():
    s = pd.Series(df.P_in.values-df.P_out.values, index=df.P_out.values)
    s.plot(label=label)
plt.xlabel('P_in')
plt.ylabel('loss W')
#plt.ylim((1, None))
# plt.semilogy()
plt.grid(1, which="both")
plt.legend()

# plt.gca().set_position([0, 0, 1, 1])
plt.savefig("plot_csv.svg")

plt.show()
# plt.savefig('plot_csv.png' )
