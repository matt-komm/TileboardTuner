import uproot
import pandas as pd
import yaml
import re
import sys
import os
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

matplotlib.use('agg')

   
def parsePedestalFile(filePath,addParams={}):
    f = uproot.open(filePath)
    tree = f['unpacker_data']['hgcroc']
    df = tree.arrays(['adc','channel','half','chip','corruption'],library='pd')
    #print(df.head())
    for k,v in addParams.items():
        df[k] = v
    return df
   
    
dfTot = parsePedestalFile(
    "/home/mkomm/Analysis/HGCAL/cerntestbeam/2024-08-03_14-51-02_ConvGain4_trim_tot_120GeV_muons/20240803_152912_phase_ck_6_DAQ.root",
    addParams = {}
)
    
dfTot = dfTot[(dfTot['channel']>=0)&(dfTot['corruption']==0)]
    
dfTot['real_channel'] = dfTot['channel'] + dfTot['half']*50 + dfTot['chip']*100


dfMedian = dfTot.groupby(['real_channel','channel','half','chip'],as_index=False ).agg({'adc': 'median'})
dfMedian = dfMedian[dfMedian['adc']>0]


print (dfMedian)



with open("roc_TB3_A5_1_ConvGain4_toatot_aligned.yaml","r") as f:
    cfg = yaml.load(f)


for chip in [1]:#sorted(dfTot['chip'].unique()):
    for half in sorted(dfTot['half'].unique()):
        for channel in range(0,36):
            dfMedianSel = dfMedian[(dfMedian['chip']==chip)&(dfMedian['half']==half)&(dfMedian['channel']==channel)]
            adcMedian = dfMedianSel['adc'].values[0]
            print (chip,half,channel,adcMedian)
            cfg['ch'][36*half+channel]["Adc_pedestal"]=int(adcMedian)

with open("roc_TB3_A5_1_ConvGain4_toatot_aligned_trigThres.yaml","w") as f:
    yaml.dump(cfg,f)

            
            
