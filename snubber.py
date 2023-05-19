"""
https://fscdn.rohm.com/en/products/databook/applinote/ic/power/switching_regulator/buck_snubber_app-e.pdf
"""
import math

f_r = 20e6  # ringing freq
C_p0 = 3.8e-9  # half-freq cap (see PDF)
V_in = 58
f_sw = 39_000

# f_r = 12.5e6 # ringing freq
# C_p0 = 25e-9 # half-freq cap (see PDF)


print('f_r=%.1f MHz' % (f_r * 1e-6))
print('C_p0=%.1f nF' % (C_p0 * 1e9))
print('V_in=%.1f V' % V_in)
print('f_sw=%.1f kHz' % (f_sw * 1e-3))

C_p2 = C_p0 / 3
L_p = 1 / ((2 * math.pi * f_r) ** 2 * C_p2)
Z = (L_p / C_p2)

print()
print('Compute:')
print('C_p2 = %.1f nF' % (C_p2 * 1e9))
print('L_p  = %.1f nH' % (L_p * 1e9))
print('Z    = %.1f Ohm' % (Z))

print()
print('SNB:')
print('R_SNB >= %.1f Ohm' % Z)
print('C_SNB  = %.1f nF .. %.1f nF' % (1 * C_p2 * 1e9, 4 * C_p2 * 1e9))

print('Power:')
C_SNB = 3 * C_p2
P_snb = C_SNB * V_in ** 2 * f_sw
print('P_snb(max)= %.1f W' % (P_snb))
