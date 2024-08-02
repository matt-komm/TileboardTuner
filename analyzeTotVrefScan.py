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
    df = tree.arrays(['channel','adc','chip','half','corruption','toa','tot'],library='pd')
    #print(df.head())
    for k,v in addParams.items():
        df[k] = v
    return df
   
dfs = []




for filePath,addParams in autodetectFiles(
    "/home/mkomm/Analysis/HGCAL/cerntestbeam/2024-08-02_12-09-04_ConvGain4_scan_ch4_Tot_vref",
    {"tot_vref": "[0-9]+_[0-9]+_ReferenceVoltage.all.Tot_vref_([0-9]+)_DAQ.root"}
):
    df = parsePedestalFile(
        filePath,
        addParams = addParams
    )
    dfs.append(df)
    
dfTot = pd.concat(dfs)


dfTot = dfTot[(dfTot['channel']>=0)&(dfTot['corruption']==0)]

#select injected channel
dfTot = dfTot[(dfTot['channel']==4)]
    
dfTot['real_channel'] = dfTot['channel'] + dfTot['half']*50 + dfTot['chip']*100
#print (sorted(dfTot['channel'].unique()))


dfTot['tot_fired']=1*(dfTot['tot']>0)

#dfTot = dfTot[dfTot['toa_vref']>230]

dfTotMean = dfTot.groupby(['real_channel','tot_vref','channel','half','chip'],as_index=False ).agg({'tot': 'mean'})
print (dfTotMean)
#sys.exit(1)


for chip in dfTot['chip'].unique():
    for half in dfTot['half'].unique():
        plt.figure(figsize=[8,7],dpi=120)
        plt.title(f"chip{chip}/half{half}")
        for channel in [4]:
            dfTotMeanSel = dfTotMean[(dfTotMean['chip']==chip)&(dfTotMean['half']==half)&(dfTotMean['channel']==channel)]
            dfTotMeanSel = dfTotMeanSel.sort_values(by=["tot_vref")
            #dfTotSel = dfTot[(dfTot['chip']==chip)&(dfTot['half']==half)&(dfTot['channel']==channel)&(dfTot['toa']>0)]
            
            #plt.hist(dfTotSel['toa_vref'],bins=toa_vref_binning, alpha=0.3, label=f"{channel}")
            plt.plot(dfTotMeanSel['tot_vref'],dfTotMeanSel['tot'],label=str(channel))
            
        box = plt.gca().get_position()
        plt.gca().set_position([box.x0, box.y0, box.width, 0.87*box.height])
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.32),ncols=8)
        #plt.tight_layout()
        plt.xlabel("tot_vref")
        plt.ylabel("Counts: tot>0")
        plt.savefig(f"chip{chip}_half{half}_totvref.png")
        plt.close()
            






