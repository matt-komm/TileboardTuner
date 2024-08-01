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
    df = tree.arrays(['channel','adc','chip','half','corruption'],library='pd')
    #print(df.head())
    for k,v in addParams.items():
        df[k] = v
    return df
   
dfs = []




for filePath,addParams in autodetectFiles(
    "/home/mkomm/Analysis/HGCAL/cerntestbeam/2024-08-01_12-03-01_ConvGain4_scan_Inv_vref_noHZ",
    {"vref_inv": "[0-9]+_[0-9]+_Inv_vref_([0-9]+)_DAQ.root"}
):
    df = parsePedestalFile(
        filePath,
        addParams = addParams
    )
    dfs.append(df)
    
dfTot = pd.concat(dfs)
dfTot = dfTot[(dfTot['channel']>=0)&(dfTot['corruption']==0)]

#might only make sense in this range
dfTot = dfTot[(dfTot['vref_inv']>249) & (dfTot['vref_inv']<751)]
    
dfTot['real_channel'] = dfTot['channel'] + dfTot['half']*50 + dfTot['chip']*100
#print (sorted(dfTot['channel'].unique()))


dfMean = dfTot.groupby(['real_channel','vref_inv','channel','half','chip'],as_index=False ).agg({'adc': 'mean'})




for chip in dfMean['chip'].unique():
    channel_dict = {}
    yaml_dict = {}
    for half in dfMean['half'].unique():
        dfSummary = pd.DataFrame({'channel':[], 'chip': [], 'half': [], 'alpha': [],'beta': []})
        for channel in [17]: #TODO: atm only using one channel as reference
            plt.figure(figsize=[8,7],dpi=120)
        
            #print (chip,half,channel,"="*50)
            dfSel = dfMean[(dfMean['chip']==chip) & (dfMean['half']==half)&(dfMean['channel']==channel)]
            x0 = dfSel['vref_inv']
            y0 = dfSel['adc']
            popt, pcov = curve_fit(lambda x,a,b:a*x+b, x0, y0, p0=[6,x0.min()])
            #print (popt, pcov)
            alpha=popt[0]
            beta=popt[1]
            
            plt.scatter(x0,y0,s=15,c='royalblue')
            plt.plot([0,1000],[beta,beta+alpha*1000],c='red',alpha=0.6,linewidth=2,linestyle='--')
           
            plt.tight_layout()
            plt.savefig(f"chip{chip}_half{half}_channel{channel}_vreffit.png")
            plt.close()
            
            insert_row = {"channel": channel, 'chip': chip, 'half': half, "alpha": alpha, "beta": beta}
            dfSummary= pd.concat([dfSummary, pd.DataFrame([insert_row])], ignore_index=True)
            
        #iqr = dfSummary['beta'].quantile(0.75) - dfSummary['beta'].quantile(0.25)
        #sel = dfSummary.beta - dfSummary.beta.mean() < 2*iqr

        

        target = 125

        #target = dfSummary[sel]['beta'].max()   
        
        print(target, dfSummary.beta) 

        #print(target, dfSummary.beta.mean(), iqr )
        #if not target:
        #    continue
        dfSummary['vref_inv'] = dfSummary.apply(lambda x: int(round( (target-x.beta)/x.alpha )), axis=1)
        #dfSummary['vref_inv'] = dfSummary['vref_inv'].clip(0,1000)
        print(dfSummary)
        
        #sys.exit(1)
        
