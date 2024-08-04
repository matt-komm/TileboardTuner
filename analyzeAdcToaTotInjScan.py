import uproot
import pandas as pd
import numpy as np
import yaml
import re
import sys
import os
import matplotlib
import argparse
import h5py
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

matplotlib.use('agg')

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--channel', dest='channel', type=int, required=True)
args = parser.parse_args()

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
    print (filePath)
    stripVer = lambda l: map(lambda x: x.split(';')[0],l)
    if not ('unpacker_data' in stripVer(f.keys()) and 'hgcroc' in stripVer(f['unpacker_data'].keys())):
        return None
    tree = f['unpacker_data']['hgcroc']
    df = tree.arrays(['channel','adc','chip','half','corruption','toa','tot'],library='pd')
    #print(df.head())
    for k,v in addParams.items():
        df[k] = v
    return df
   
dfs = []


scanningFolder = "/home/mkomm/Analysis/HGCAL/cerntestbeam/toatot_aligned_totcinj"

inputFolder = None
for basePath in os.listdir(scanningFolder):
    match = re.search("ConvGain4_toatot_aligned_scan_ch([0-9]+)_Calib_2V5",basePath)
    if match:
        channel = int(match.group(1))
        if channel==args.channel:
            inputFolder = os.path.join(scanningFolder,basePath)

if inputFolder is None:
    print ("No input folder found")
    sys.exit(1)


#inputFolder = "/home/mkomm/Analysis/HGCAL/cerntestbeam/2024-08-04_10-05-33_ConvGain4_toatot_aligned_scan_ch0_Calib_2V5"
    
print ("Analyzing folder: ",inputFolder)

for filePath,addParams in autodetectFiles(
    inputFolder,
    #"/home/mkomm/Analysis/HGCAL/cerntestbeam/totcinj/2024-08-02_19-38-19_ConvGain4_scan_ch4_Calib_2V5",
    {"Calib_2V5": "[0-9]+_[0-9]+_ReferenceVoltage.all.Calib_2V5_([0-9]+)_DAQ.root"}
):
    df = parsePedestalFile(
        filePath,
        addParams = addParams
    )
    if df is None:
        print ("skipping file: ",filePath)
        continue
    dfs.append(df)
    
dfTot = pd.concat(dfs)


dfTot = dfTot[(dfTot['channel']>=0)&(dfTot['corruption']==0)]

#select injected channel
#dfTot = dfTot[(dfTot['channel']==4)]
    
dfTot['real_channel'] = dfTot['channel'] + dfTot['half']*50 + dfTot['chip']*100
#print (sorted(dfTot['channel'].unique()))


#dfTot = dfTot[dfTot['toa_vref']>230]

dfMean = dfTot.groupby(['real_channel','Calib_2V5','channel','half','chip'],as_index=False ).agg({
    'tot': ['mean', 'median', 'std'], 
    'adc': ['mean', 'median', 'std'], 
    'toa': ['mean', 'median', 'std'], 
})

print (dfMean)


def totToAdcRange(tot):
    scale = 14 #from Arnaud
    offset = 7100 #found this by eye
    return scale*tot-offset

for chip in dfTot['chip'].unique():
    for half in dfTot['half'].unique():
        plt.figure(figsize=[8,7],dpi=120)
        plt.title(f"chip{chip}/half{half}")
        for channel in [args.channel]:
            dfMeanSel = dfMean[(dfMean['chip']==chip)&(dfMean['half']==half)&(dfMean['channel']==channel)]
            dfMeanSel = dfMeanSel.sort_values(by=['Calib_2V5'])
            
            plt.plot(dfMeanSel['Calib_2V5'],dfMeanSel['adc']['mean'],label="adc"+str(channel))
            plt.plot(dfMeanSel['Calib_2V5'],totToAdcRange(dfMeanSel['tot']['mean']),label="tot"+str(channel))
            plt.plot(dfMeanSel['Calib_2V5'],dfMeanSel['toa']['mean'],label="toa"+str(channel))
            
            adcTurnoff = dfMeanSel[dfMeanSel['adc']['mean']<10]['Calib_2V5'].min()
            totTurnon = dfMeanSel[dfMeanSel['tot']['mean']<10]['Calib_2V5'].max()
            
            midPoint = 0.5*(adcTurnoff+totTurnon)
            plt.plot([midPoint],[0], marker='v', c='black')
            
            outputFile = h5py.File(
                os.path.join(
                    inputFolder,
                    f"chip{chip}_half{half}_channel{channel}_totcinj.h5"
                ),
                'w'
            )
            outputFile.create_dataset("Calib_2V5", data=dfMeanSel['Calib_2V5'].to_numpy(), compression="gzip", compression_opts=4)
            for quantity in ['adc','tot','toa']:
                for fieldName in dfMeanSel[quantity].columns:
                    outputFile.create_dataset(quantity+"_"+fieldName, data=dfMeanSel['adc'].to_numpy(), compression="gzip", compression_opts=4)
            outputFile.close()
            
        plt.legend(loc='upper center',ncols=3,bbox_to_anchor=(0.5, 1.13))
        plt.ylim([0,totToAdcRange(dfMeanSel['tot']['mean']).max()*1.1])
        #plt.xlim([400,600])
        plt.grid()
        plt.xlabel("Injected charge: Calib_2V5")
        plt.ylabel("Mean adc/tot")
        plt.savefig(
            os.path.join(
                inputFolder,
                f"chip{chip}_half{half}_channel{channel}_totcinj.png"
            )
        )
        plt.close()
            






