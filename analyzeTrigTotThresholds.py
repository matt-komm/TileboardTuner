import uproot
import pandas as pd
import numpy as np
import yaml
import re
import sys
import os
import matplotlib
import h5py
import math
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

matplotlib.use('agg')


def fitAdc(calib_2V5, adc, unc=2.):
    #select fit range
    adcSel = (adc>200)&(adc<1000)&(calib_2V5>0)
    
    adc = adc[adcSel]
    calib_2V5 = calib_2V5[adcSel]
    if unc is not None:
        if hasattr(unc, '__len__'):
            unc = unc[adcSel]
        else:
            unc = np.ones_like(adc)*unc
        
        posUncSel = unc>0.01
        adc = adc[posUncSel]
        calib_2V5 = calib_2V5[posUncSel]
        unc = unc[posUncSel]
    
    params,cov = curve_fit(
        lambda x,a,b: a*x+b, 
        calib_2V5, adc, p0=[1,0], 
        sigma=unc, absolute_sigma=True, 
        check_finite=True, 
        bounds=[(0,0),(np.inf,np.inf)] #force positive slope & offset
    )
    
    return {
        "slope": params[0],
        "offset": params[1],
        "slope_unc": math.sqrt(cov[0,0]),
        "offset_unc": math.sqrt(cov[1,1])
    }
    
def fitTot(calib_2V5, tot, unc=5.):
    #select fit range
    totSel = (calib_2V5>2700)
    
    tot = tot[totSel]
    calib_2V5 = calib_2V5[totSel]
    
    if unc is not None:
        if hasattr(unc, '__len__'):
            unc = unc[totSel]
        else:
            unc = np.ones_like(tot)*unc
        posUncSel = unc>0.01
        tot = tot[posUncSel]
        calib_2V5 = calib_2V5[posUncSel]
        unc = unc[posUncSel]
        
    params,cov = curve_fit(
        lambda x,a,b: a*x+b, 
        calib_2V5, tot, p0=[0.1,0], 
        sigma=unc, absolute_sigma=True, 
        check_finite=True, 
        bounds=[(0,0),(np.inf,np.inf)] #force positive slope & offset
    )

    return {
        "slope": params[0],
        "offset": params[1],
        "slope_unc": math.sqrt(cov[0,0]),
        "offset_unc": math.sqrt(cov[1,1])
    }

basepath = "/home/mkomm/Analysis/HGCAL/cerntestbeam/toatot_aligned_totcinj"

dfMean = None 

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

            fieldNames = list(inputFile.keys())
            if dfMean is None:
                dfMean = pd.DataFrame(columns=['chip','half','channel']+fieldNames)
           
            data = {'chip': chip, 'half': half, 'channel': channel}
            for fieldName in fieldNames:
                data[fieldName] = inputFile[fieldName][:]

            dfMean.loc[len(dfMean)]=data

            
#print (dfMean.columns)
            
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
            adc_std = dfMeanSel['adc_std'].values[0]
            tot_mean = dfMeanSel['tot_mean'].values[0]
            tot_std = dfMeanSel['tot_std'].values[0]
            
            '''
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
            '''
            #plt.plot([midPoint],[0], marker='v', c='black')
           
            #print (calib_2V5)
            #print (adc_mean)
            #print (adc_std)
            
            adcFitResult = fitAdc(calib_2V5, adc_mean, adc_std)
            totFitResult = fitTot(calib_2V5, tot_mean, tot_std)

            multiFactor = adcFitResult['slope']/totFitResult['slope']
            tot_Pn = totFitResult['offset']
            
            
            #TODO: finite difference between fitted curves originates from 
            #neglecting the adc offset
            plt.plot(calib_2V5,adc_mean,c='royalblue',linewidth=2,label='Mean ADC')
            #plt.plot(calib_2V5,calib_2V5*adcFitResult['slope']+adcFitResult['offset'],linestyle='--',c='blue')
            plt.plot(calib_2V5,multiFactor*(tot_mean-tot_Pn)+adcFitResult['offset'],c='orange',linewidth=2,label='Mean TOT (calibrated)')
            plt.plot(calib_2V5,dfMeanSel['toa_mean'].values[0]*5,c='green',linewidth=2,label="Mean TOA (x5)")
            
            plt.plot(calib_2V5,multiFactor*(calib_2V5*totFitResult['slope'])+adcFitResult['offset'],linestyle=':',linewidth=3,c='black', label="Linear fit")
            
            plt.grid()
            plt.legend()
            plt.ylim([0,1.05*multiFactor*(calib_2V5.max()*totFitResult['slope'])])
            plt.xlabel("Injected charge: Calib_2V5")
            plt.ylabel("Mean ADC/TOT/TOA")
            plt.savefig(
                f"chip{chip}_half{half}_channel{channel}_trigTotThres.png"
            )
            plt.close()
            #sys.exit(1)
            #dfTot
            #calib_2V5 = 
            



      
            



