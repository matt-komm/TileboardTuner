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


## TOA adjustment: 1. Toa_vref scan

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
* set `Calib_2V5` (external charge injection amplitude)
* set `IntCtest=0` (interne charge injection amplitude)
* set `choice_cinj=0` (deactivate interne charge injection)
* set `cmd_120p=1` (activate externe charge injection)
* injected channel is selected by setting `HighRange=1`
* find a channel where ADC/TOA are in the same BX, ie. high ADC/TOA at `Calib_2V5=4000` (adjust `phase_ck`)

**Procedure**
* scan `Calib_2V5` from 10 to >100 in steps of 10 (better 5); extend range/steps as needed
* NB: if `Toa_vref` is close (within 10) to the pedestal the turnon should be within `Calib_2V5<100`
* guesstimate the `trim_toa` shift; eg. `+20 Calib_2V5` per `-10 trim_toa` for ConvGain4
* guesstimate the `trim_toa` modification such that all channels has the turnon at the same `Calib_2V5`, eg. `Calib_2V5=30`
* after alignment, repeat `Toa_vref` scan; the pikes should be all at the same position
* NB: indirect alignment could also be tried as a first rough pass by doing `Toa_vref` scans for 2 `trim_toa` values to get the `Toa_vref`/`trim_toa` slope; advantages: fast scanning + easy to parse pedestal position; caveat: the threshold depend nonlinear on `Toa_vref` such that when the pedestals align the S-curves for a `Toa_vref` value above the pedestals might be dispersed

## TOT adjustment: 1. configuring max ADC threshold

**Setup**
* configure for charge injection into one channel (same as for `trim_toa` scan)
* set `Tot_vref=1000` to prevent triggering of TOT

**Procedure**
* start from max charge, ie. `Calib_2V5=4000`, for which `adc` of injected channel will be saturated, ie. `adc>1000`
* gradually lower injected charge by lowering `Calib_2V5` until `adc` level is at about `adc=900` per half (eg. `600<Calib_2V5<800` for ConvGain4)


## TOT adjustment: 2. Tot_vref scan

**Setup**
* keep injecting optimized charge from step 1. into selected channel

**Procedure**
* scan `Tot_vref` from 200 to 800 in steps of 5 (better 2)
* check `Tot_vref` vs mean `tot` in injected channels; should fall exponentially to 0 since low `Tot_vref` results in bigger `tot` due to longer pluse
* select `Tot_vref` per half where the mean `tot` falls rapidly to 0, ie. the point where the injected charge does not trigger `tot` that corresponds to the selected `adc` level from step 1.
* repeat for a few other channels and select the minimum `Tot_vref` since some channels might run out of `adc` range (ie. `>1023`) earlier
* NB: to plot mean `adc` and mean `tot` on the same scale one can multiply `tot` by 14 and substract an offset of about `7500` (for ConvGain4)

## TOT adjustment: 3. trim_tot
**Setup**
* set `trim_tot=31` for all channels

**Procedure**
* guesstimate the `trim_tot` shift; eg. `+20 Calib_2V5` per `-10 trim_tot` for ConvGain4 (oddly identical to `trim_toa`)
* scan `Calib_2V5` and find `adc`/`tot` switching point for all channels
* guesstimate the necessary `trim_tot` shift per channel to have all channels' switching points at the same `Calib_2V5`

## Trigger thresholds
**Procedure**
* take pedestal run
* set `Adc_Pedestal` parameter per channel to median `adc` level per channel
* set `Adc_TH=10` (noise level of `adc`) and `MultFactor=14` (factor between slopes  of `tot`/`adc` vs `Calib_2V5`)  in `DigitalHalf` 

