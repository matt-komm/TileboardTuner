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
    "/home/mkomm/Analysis/HGCAL/cerntestbeam/2024-08-01_15-03-16_ConvGain4_scan_triminv_swapped_configs",
    {"trim_inv": "[0-9]+_[0-9]+_trim_inv_([0-9]+)_DAQ"}
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


dfMean = dfTot.groupby(['real_channel','trim_inv','channel','half','chip'],as_index=False ).agg({'adc': 'mean'})




for chip in dfMean['chip'].unique():
    channel_dict = {}
    yaml_dict = {}
    for half in dfMean['half'].unique():
        dfSummary = pd.DataFrame({'channel':[], 'chip': [], 'half': [], 'alpha': [],'beta': []})
        
        
        
        
        for channel in range(0,36):
            if (channel%6) == 0:
                plt.figure(figsize=[8,7],dpi=120)
            plt.subplot(2,3,(channel%6)+1,title=f"ch{channel}")
            
                
                
            #print (chip,half,channel,"="*50)
            dfSel = dfMean[(dfMean['chip']==chip) & (dfMean['half']==half)&(dfMean['channel']==channel)]
            x0 = dfSel['trim_inv']
            y0 = dfSel['adc']
            popt, pcov = curve_fit(lambda x,a,b:a*x+b, x0, y0, p0=[6,x0.min()])
            #print (popt, pcov)
            alpha=popt[0]
            beta=popt[1]

            plt.scatter(x0,y0,s=15,c='royalblue')
            plt.plot([0,63],[beta,beta+alpha*63],c='red',alpha=0.6,linewidth=2,linestyle='--')
            

            insert_row = {"channel": channel, 'chip': chip, 'half': half, "alpha": alpha, "beta": beta}
            dfSummary= pd.concat([dfSummary, pd.DataFrame([insert_row])], ignore_index=True)
            
            if channel>0 and ((channel+1)%6) == 0:
                plt.tight_layout()
                plt.savefig(f"chip{chip}_half{half}_channel{channel}_fits.png")
                plt.close()
            
        iqr = dfSummary['beta'].quantile(0.75) - dfSummary['beta'].quantile(0.25)
        sel = dfSummary.beta - dfSummary.beta.mean() < 2*iqr

        target = dfSummary[sel]['beta'].max()    

        print(target, dfSummary.beta.mean(), iqr )
        #if not target:
        #    continue
        dfSummary['trimmed_ref_dac'] = dfSummary.apply( lambda x: int(round( (target-x.beta)/x.alpha )) if x.alpha>0 else 99, axis=1 )
        dfSummary['trimmed_ref_dac'] = dfSummary['trimmed_ref_dac'].clip(0,63)
        print(dfSummary)
        
        
        
        for index, row in dfSummary.iterrows():
            adict = { 
                'trim_inv' : int(row.trimmed_ref_dac),
                'Gain_conv' : 4,
                'Inputdac' : 31,
                'sign_dac' : 0,
                'dacb' : 0,
            }

            
            channel_dict[int(row.channel+row.half*36)] = adict

    
    
    with open('trimmed_pedestal_chip%i.yaml'%chip,'w') as fout:
        yaml.dump(
            {
                'roc0': 
                {
                    'sc': {'ch' : channel_dict}
                }
            },
            fout
        )
'''
for i, ch in enumerate([tb*36:(tb+1)*36]):
        
        x0 = trim_inv
        y0 = df_pedestal[ch]
        popt, pcov = curve_fit(lambda x,a,b:a*x+b, x0, y0, p0=[6,x0.min()])
        alpha=popt[0]
        beta=popt[1]

        insert_row = {"channel": i, "Name": ch,"alpha": alpha,"beta": beta}
        summary= pd.concat([summary, pd.DataFrame([insert_row])], ignore_index=True)
        
    iqr = summary['beta'].quantile(0.75) - summary['beta'].quantile(0.25)
    sel = summary.beta - summary.beta.mean() < 2*iqr

    target = summary[sel]['beta'].max()    

    print(target, summary.beta.mean(), iqr )
    #if not target:
    #    continue
    summary['trimmed_ref_dac'] = summary.apply( lambda x: int(round( (target-x.beta)/x.alpha )) if x.alpha>0 else 99, axis=1 )
    summary['trimmed_ref_dac'] = summary['trimmed_ref_dac'].clip(0,63)
    print(summary)


for trim_inv in dfTot['trim_inv'].unique():
    for chip in dfTot['chip'].unique():
        for half in dfTot['half'].unique():
            for channel in dfTot['channel'].unique():
                dfSel = dfTot[dfTot['trim_inv']==trim_inv and dfTot['chip']==chip and dfTot['half']==half and dfTot['channel']==channel]
            
                print (dfSel)
'''
    
    
#print (dfTot['real_channel'].unique())


#dfTot['adcmean'] = dfTot['adc'].mean()
