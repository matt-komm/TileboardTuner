import uproot
import pandas as pd
import numpy as np
import yaml
import re
import sys
import os
import matplotlib
import h5py
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

matplotlib.use('agg')


def fitAdc(calib_2V5, adc, unc=2.):
    #select fit range
    adcSel = (adc>200)&(adc<1000)
    
    adc = adc[adcSel]
    calib_2V5 = calib_2V5[adcSel]
    if unc is not None:
        if hasattr(unc, '__len__'):
            unc = unc[adcSel]
        else:
            unc = np.ones_like(adc)*unc
        
    
    params,cov = curve_fit(
        lambda x,a,b: a*x+b, 
        calib_2V5, adc, p0=[1,0], 
        sigma=unc, absolute_sigma=True, 
        check_finite=True, 
    )

    print (params,cov)
    
def fitTot(calib_2V5, tot, unc=5.):
    #select fit range
    totSel = (calib_2V5>2900)
    
    tot = tot[totSel]
    calib_2V5 = calib_2V5[totSel]
    if unc is not None:
        if hasattr(unc, '__len__'):
            unc = unc[totSel]
        else:
            unc = np.ones_like(tot)*unc
        
    
    params,cov = curve_fit(
        lambda x,a,b: a*x+b, 
        calib_2V5, tot, p0=[0.1,0], 
        sigma=unc, absolute_sigma=True, 
        check_finite=True, 
    )

    print (params,cov)


basepath = "/home/mkomm/Analysis/HGCAL/cerntestbeam/toatot_aligned_totcinj"

dfMean = pd.DataFrame(columns=["chip","half","channel","Calib_2V5","adc_mean","toa_mean","tot_mean"])    

for folder in os.listdir(basepath):
    if not os.path.isdir(os.path.join(basepath,folder)):
        continue
    print (folder)
    
    for f in os.listdir(os.path.join(basepath,folder)):
       
        match = re.match("chip([0-9]+)_half([0-9]+)_channel([0-9]+)_totcinj.h5",f)
        if match:
            chip = int(match.group(1))
            half = int(match.group(2))
            channel = int(match.group(3))
            
            inputFile = h5py.File(os.path.join(basepath,folder,f),"r")
            Calib_2V5 = inputFile["Calib_2V5"][:]
            adc_mean = inputFile["adc_mean"][:]
            toa_mean = inputFile["toa_mean"][:]
            tot_mean = inputFile["tot_mean"][:]
            dfMean.loc[len(dfMean)]={
                "chip": chip, "half": half, "channel": channel,
                "Calib_2V5": Calib_2V5, 
                "adc_mean": adc_mean,
                "toa_mean": toa_mean,
                "tot_mean": tot_mean,
            }
#print (
#(df['tot_mean'].values>700).any()
#print (df['channel'].unique())

#df = df[df['tot_mean'].map(lambda x: (x>0).any())]
#dfTot['real_channel'] = dfTot['channel'] + dfTot['half']*50 + dfTot['chip']*100
#dfTot = dfTot.sort_values(by=

for chip in sorted(dfMean['chip'].unique()):
    for half in sorted(dfMean['half'].unique()):
        for channel in sorted(dfMean['channel'].unique()):
            plt.figure(figsize=[8,7],dpi=120)
            plt.title(f"chip{chip}/half{half}/channel{channel}")
            print (chip,half,channel)
            
            dfMeanSel = dfMean[(dfMean['chip']==chip)&(dfMean['half']==half)&(dfMean['channel']==channel)]
            dfMeanSel = dfMeanSel.sort_values(by=['Calib_2V5'])
            
            calib_2V5 = dfMeanSel['Calib_2V5'].values[0]
            adc_mean = dfMeanSel['adc_mean'].values[0]
            tot_mean = dfMeanSel['tot_mean'].values[0]
            
            adcTurnoff = dfMeanSel['Calib_2V5'].values[0][dfMeanSel['adc_mean'].values[0]<10]
            totTurnon = dfMeanSel['Calib_2V5'].values[0][dfMeanSel['tot_mean'].values[0]<10]
            if len(adcTurnoff)>0 and len(totTurnon)>0:
                midPoint = 0.5*(adcTurnoff.min()+totTurnon.max())
            elif len(adcTurnoff)>0:
                midPoint = adcTurnoff.min()
                print (f"WARNING: no TOT crossing for {chip}/{half}/{channel}")
            elif len(totTurnon)>0:
                midPoint = totTurnon.max()
                print (f"WARNING: no ADC crossing for {chip}/{half}/{channel}")
            else:
                midPoint = dfSel['Calib_2V5'].values[0].min()
                print (f"WARNING: no crossing for {chip}/{half}/{channel}")
            
            #plt.plot([midPoint],[0], marker='v', c='black')
            
            fitAdc(calib_2V5,adc_mean)
            fitTot(calib_2V5,tot_mean)
            
            plt.plot(calib_2V5,adc_mean)   
            #plt.plot(calib_2V5,tot_mean)
            
            plt.grid()
            plt.xlabel("Injected charge: Calib_2V5")
            plt.ylabel("Mean adc/tot")
            plt.savefig(
                f"chip{chip}_half{half}_channel{channel}_trigTotThres.png"
            )
            plt.close()
            sys.exit(1)
            #dfTot
            #calib_2V5 = 
            



      
            



