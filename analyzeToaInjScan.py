import uproot
import pandas as pd
import numpy as np
import yaml
import re
import sys
import os
import matplotlib
import h5py
import argparse
import matplotlib.pyplot as plt

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
    tree = f['unpacker_data']['hgcroc']
    df = tree.arrays(['channel','adc','chip','half','corruption','toa'],library='pd')
    #print(df.head())
    for k,v in addParams.items():
        df[k] = v
    return df
   
dfs = []

scanningFolder = "/home/mkomm/Analysis/HGCAL/cerntestbeam/toacinj"

inputFolder = None
for basePath in os.listdir(scanningFolder):
    match = re.search("ConvGain4_scan_Calib_2V5_ch([0-9]+)",basePath)
    if match:
        channel = int(match.group(1))
        if channel==args.channel:
            inputFolder = os.path.join(scanningFolder,basePath)

if inputFolder is None:
    print ("No input folder found")
    sys.exit(1)


#inputFolder = "/home/mkomm/Analysis/HGCAL/cerntestbeam/2024-08-01_20-31-18_ConvGain4_scan_Calib_2V5_ch17_newphase"
    
print ("Analyzing folder: ",inputFolder)

for filePath,addParams in autodetectFiles(
    #"/home/mkomm/Analysis/HGCAL/cerntestbeam/2024-08-01_18-39-58_ConvGain4_scan_Calib_2V5_ch4_newphase_trim_toa_21",
    inputFolder,
    {"Calib_2V5": "[0-9]+_[0-9]+_Calib_2V5_([0-9]+)_DAQ.root"}
    #{"Calib_2V5": "[0-9]+_[0-9]+_ReferenceVoltage.all.Calib_2V5_([0-9]+)_DAQ.root"}
    
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

dfTot['toa_fired']=1*(dfTot['toa']>0)
dfTotSel = dfTot[(dfTot['chip']==0)&(dfTot['half']==0)&(dfTot['channel']==5)&(dfTot["Calib_2V5"]==10)]
print (dfTotSel)

dfToaFired = dfTot.groupby(['real_channel','Calib_2V5','channel','half','chip'],as_index=False ).agg({'toa_fired': 'sum'})
#print (dfToaFired[(dfToaFired['chip']==0)&(dfToaFired['half']==0)&(dfToaFired['channel']==5)])


for chip in dfTot['chip'].unique():
    for half in dfTot['half'].unique():
        plt.figure(figsize=[8,7],dpi=120)
        for channel in [args.channel]:
            #print (chip,half,'='*10)
            dfToaFiredSel = dfToaFired[(dfToaFired['chip']==chip)&(dfToaFired['half']==half)&(dfToaFired['channel']==channel)]
            dfToaFiredSel = dfToaFiredSel.sort_values(by=['Calib_2V5'])

            dfTotSel = dfTot[(dfTot['chip']==chip)&(dfTot['half']==half)&(dfTot['channel']==channel)]
            dfTotSel = dfTotSel.sort_values(by=['Calib_2V5'])
            #plt.hist(dfTotSel['toa_vref'],bins=toa_vref_binning, alpha=0.3, label=f"{channel}")
            '''
            idxSorted =  np.argsort(dfToaFiredSel['Calib_2V5'].to_numpy())
            cinj = dfToaFiredSel['Calib_2V5'].to_numpy()[idxSorted]
            toa_fired = dfToaFiredSel['toa_fired'].to_numpy()[idxSorted]
            '''
            
            
            outputFile = h5py.File(
                os.path.join(
                    inputFolder,
                    f"chip{chip}_half{half}_channel{channel}_toacinj.h5py"
                ),
                'w'
            )
            outputFile.create_dataset("Calib_2V5", data=dfToaFiredSel['Calib_2V5'].to_numpy(), compression="gzip", compression_opts=4)
            outputFile.create_dataset("toa_fired", data=dfToaFiredSel['toa_fired'].to_numpy(), compression="gzip", compression_opts=4)
            outputFile.close()
            
            plt.plot(dfToaFiredSel['Calib_2V5'],dfToaFiredSel['toa_fired'])
            
            
        #plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),ncols=12)
        #plt.tight_layout()
        plt.xlabel("injected charge (Calib_2V5)")
        plt.ylabel("Counts: toa>0")
        plt.xlim([0,100])
        plt.grid()
        plt.savefig(
            os.path.join(
                inputFolder,
                f"chip{chip}_half{half}_channel{channel}_toacinj.png"
            )
        )
        plt.close()
            






