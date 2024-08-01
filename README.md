# TileboardTuner

## Pedestal adjustment per half

**Setup**
* make sure `Inv_vref` and `Noinv_vref` are individually set to same values accross halfs
* set `dacb` to same values for all channels, eg. `0` (NB: this could be modified in case the adjustment is outside the `trim_inv` range)
* make sure desired `Gain_conv` is set

**Procedure**
* scan `trim_inv` parameter for all channels simultaneously, eg. `0,15,30,45,60`
* fit linear function to `trim_inv` vs mean `adc` per channel
* find maximum of `adc`-intercept per chip half only = target `adc` level (NB: both halfs will be corrected to each other later through `Inv_vref` instead) 
* optional: remove outliers (eg. 68% `adc` quantile) and unresponsive channels before fitting 
* adjust `trim_inv` to match the target `adc` level
* some chip halfs show nonlinear behavior on `trim_inv` for `adc<100` (01/08/24)

## Chip half pedestal adjustment

**Procedure**
* messing with `HZ...` parameters does not seem to be nescessary
* scan `Inv_vref` from 0 to 1000 in steps of 100
* the chip runs into saturation for `Inv_vref` values below 200 and above 800 showing nonlinear dependence on pedestal levels
* target `adc` level should be set above 100, eg. 125 


## TOA adjustment: 1. Toa_vref

**Setup**
* set `En_hyst_tot=0` under `GlobalAnalog` to disable TOT hysterese; influences also pedestal
* set `trim_toa=32` (middle point)

**Procedure**
* scan `Toa_vref` from 170 to 270 in steps of 5 (better 2) without injection
* find minimum setting where TOA is not triggered by pedestals; ie. no `toa` counts above `Toa_vref` threshold
* NB: the pedestal will fire TOA in a very narrow window in `Toa_vref` (<10 for ConvGain4); if `Toa_vref` is **below or above** pedestal no `toa` will be present


## TOA adjustment: 2. trim_toa

**Setup**
* set `En_hyst_tot=0` under `GlobalAnalog` to disable TOT hysterese; influences also pedestal
* set `Calib_2V5=200` (external charge injection amplitude)
* set `IntCtest=0` (interne charge injection amplitude)
* set `choice_cinj=0` (deactivate interne charge injection)
* set `cmd_120p=1` (activate externe charge injection)
* injected channel is selected by setting `HighRange=1`
* find a channel where ADC/TOA are in the same BX (adjust `phase_ck`)


**Procedure**

