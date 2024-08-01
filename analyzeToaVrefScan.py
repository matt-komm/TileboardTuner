import uproot
import pandas as pd
import numpy as np
import yaml
import re
import sys
import os
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

matplotlib.use('agg')

def autodetectFiles(filePath, fileParamPattern):
    fileParamList = []
    for f in os.listdir(filePath):
        params = {}
        for k,pattern in fileParamPattern.items():
            match = re.match(pattern,f)
            if match:
                params[k] = int(match.group(1))
                #print (match.group(1))
        if len(params)==len(fileParamPattern):
            fileParamList.append((
                os.path.join(filePath,f),
                params
            ))
    return fileParamList
    

    
#sys.exit(1)
    

def parsePedestalFile(filePath,addParams={}):
    f = uproot.open(filePath)
    tree = f['unpacker_data']['hgcroc']
    df = tree.arrays(['channel','adc','chip','half','corruption','toa'],library='pd')
    #print(df.head())
    for k,v in addParams.items():
        df[k] = v
    return df
   
dfs = []




for filePath,addParams in autodetectFiles(
    "/home/mkomm/Analysis/HGCAL/cerntestbeam/2024-08-01_15-43-48_ConvGain4_scan_toa_vref_noinj",
    {"toa_vref": "[0-9]+_[0-9]+_toa_vref_([0-9]+)_DAQ.root"}
):
    df = parsePedestalFile(
        filePath,
        addParams = addParams
    )
    dfs.append(df)
    
dfTot = pd.concat(dfs)


dfTot = dfTot[(dfTot['channel']>=0)&(dfTot['corruption']==0)]
    
dfTot['real_channel'] = dfTot['channel'] + dfTot['half']*50 + dfTot['chip']*100
#print (sorted(dfTot['channel'].unique()))

toa_vref_binning = np.sort(dfTot['toa_vref'].unique())
toa_vref_binning = 0.5*(toa_vref_binning[1:]+toa_vref_binning[:-1])
toa_vref_binning = np.concatenate([
    [2*dfTot['toa_vref'].min()-toa_vref_binning[0]],
    toa_vref_binning,
    [toa_vref_binning[-1]+2*dfTot['toa_vref'].max()-2*toa_vref_binning[-1]]
])
dfTot['toa_fired']=1*(dfTot['toa']>0)
dfToaFired = dfTot[dfTot['toa']>0].groupby(['real_channel','toa_vref','channel','half','chip'],as_index=False ).agg({'toa_fired': 'sum'})
#print (dfToaFired)



for chip in dfTot['chip'].unique():
    for half in dfTot['half'].unique():
        plt.figure(figsize=[8,7],dpi=120)
        for channel in range(0,36):
            #dfToaFiredSel = dfToaFired[(dfToaFired['chip']==chip)&(dfToaFired['half']==half)&(dfToaFired['channel']==channel)]
            
            dfTotSel = dfTot[(dfTot['chip']==chip)&(dfTot['half']==half)&(dfTot['channel']==channel)&(dfTot['toa']>0)]
            
            plt.hist(dfTotSel['toa_vref'],bins=toa_vref_binning, alpha=0.3, label=f"{channel}")
            
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),ncols=12)
        #plt.tight_layout()
        plt.xlabel("toa_vref")
        plt.ylabel("Counts: toa>0")
        plt.savefig(f"chip{chip}_half{half}_channel{channel}_toavref.png")
        plt.close()
            






