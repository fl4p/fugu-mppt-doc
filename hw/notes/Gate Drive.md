
IR2104 has a source current of min = 130mA  and typ = 210 mA.
Min gate drive resistor is 47ohm.
150N10F7 (4.2mOhm, Qg(50V,110A,10V)=117nC).
With 100ohm the gate rise time is 3.4us.
With 47ohm the gate rise time is 2.5us.


To reduce switching loss further, we need a bigger driver.
Choose IR2184. This one costs ~$2, delivers 1.9A source current, same pinout.


Infineon
* [Half-Bridge Drivers](https://www.infineon.com/cms/en/product/power/gate-driver-ics/half-bridge-drivers/) with dead-time
* https://www.infineon.com/cms/de/applications/renewables/photovoltaic/power-optimizer-solutions/
* [Half-bridge drivers, >=0.4A, >=90V, DSO-8/SOIC-8]
* https://www.infineon.com/cms/en/product/power/gate-driver-ics/?filterValues=~(358~(~%27Half*20Bridge~%27High-side*20and*20low-side)~290_114_nom~(leftBound~0.4~rightBound~30)~496_nom~(leftBound~90~rightBound~728)~packageName~(~%27PG-DSO-8~%27PG-DSO-8-59~%27SOIC*208N))&visibleColumnIds=name,opn,orderOnline,2c803337c8bf4224ab0f03561e1c0e7c,productStatusInfo,496_nom,290_114_nom,290_113_nom,350_nom,358,551,852,851,608,415,packageName,640_nom,157_nom,853_min,853_max,854_min,854_max,856_nom,855_nom,860_150_nom,860_151_nom,1517

* IR2011 (200V,1A,independent,$1)
* IR2184 ()
* 
These are hard to find in stock:
* 2ED2182S06F (650V,2.5A,600ns,400ns dead-time, HIN/LIN)
* 2ED2183S06F (650V,2.5A,600ns,400ns dead-time, HIN/*LIN)
* 2ED2184S06F (650V,2.5A,600ns,400ns dead-time, IN/*SD, $2.2)


Microchip
- MIC4605-1YM
- MIC4605-1YMT (with EN pin)

China:
* TF2184M(600V,1.4A,200ns,400ns dead-time,IN/SD*)



* IRS21867S (600V,4A,independent,$1.4,discontinued)
* 2EDL8x2x