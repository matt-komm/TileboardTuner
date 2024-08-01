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
