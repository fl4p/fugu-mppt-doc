# Snubber Design Notes
[Altium Acadamy YT: Where to Place Snubbers in a Buck Converter](https://www.youtube.com/watch?v=c8UW640WRcc)

[TOSHIBA AN: Parasitic Oscillation and Ringing of Power MOSFETs](https://toshiba.semicon-storage.com/info/application_note_en_20180726_AKX00066.pdf?did=59456)

[ROHM AN: Snubber Circuit for Buck Converter IC](https://fscdn.rohm.com/en/products/databook/applinote/ic/power/switching_regulator/buck_snubber_app-e.pdf)


# FUGU
46V 5A / 28V

* Following the guide at https://fscdn.rohm.com/en/products/databook/applinote/ic/power/switching_regulator/buck_snubber_app-e.pdf
The LS ringing frequency is 12.5 MHz.
Adding and 27 nF capacitor brings it down to 6.5 MHz
According to formular (4), L_P = 6 nH.
Z = 0.47ohm



# Ringing Snapshots
I=4.8
scope_13: HS (IPP FET)
scope_15,16: LS (ST FET)
yellow: Vgs_L   blue: Vds_L
green: Vgs_H    red: Vds_H
![Test Setup](assets/gate-drive/scope_13.png)
![Test Setup](assets/gate-drive/scope_16.png)

changed: 
- added 100nF foil bypass
- changed LS fet
- shorter FET wires
- scope19, scope20
![Test Setup](assets/gate-drive/scope_19.png)
![Test Setup](assets/gate-drive/scope_20.png)

changed:
- removed hs discharge
- scope 22/23
![Test Setup](assets/gate-drive/scope_22.png)
*HS (green) is not fully switched off when LS (yellow) turns on.*

![Test Setup](assets/gate-drive/scope_23.png)


