# TileboardTuner

## Pedestal adjustment per half

**Setup**
* set `Inv_vref` and `Noinv_vref` to same values
* set `dacb` to same values (NB: this could be modified in case the adjustment is outside the `trim_inv` range)

**Procedure**
* scan `trim_inv` parameter for all channels simultaneously, eg. `0,15,30,45,60`
* fit linear function to `trim_inv` vs mean `adc` per channel
* find maximum of `adc`-intercept per chip half only = target `adc` level (NB: both halfs will be corrected to each other later through `Inv_vref` instead) 
* optional: remove outliers (eg. 68% `adc` quantile) and unresponsive channels before fitting 
* adjust `trim_inv` to match the target `adc` level

## 
