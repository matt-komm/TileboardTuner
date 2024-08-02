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

matplotlib.use('agg')

basepath = "/home/mkomm/Analysis/HGCAL/cerntestbeam/totcinj"

df = pd.DataFrame(columns=["chip","half","channel","Calib_2V5","adc_mean","toa_mean","tot_mean"])

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
            df.loc[len(df)]={
                "chip": chip, "half": half, "channel": channel,
                "Calib_2V5": Calib_2V5, 
                "adc_mean": adc_mean,
                "toa_mean": toa_mean,
                "tot_mean": tot_mean,
            }

print (df)


for chip in sorted(df['chip'].unique()):
    for half in sorted(df['half'].unique()):
        plt.figure(figsize=[8,7],dpi=120)
        for channel in range(0,10):#sorted(df['channel'].unique()):
            dfSel = df[(df['chip']==chip)&(df['half']==half)&(df['channel']==channel)]
            #print (dfSel['tot_mean'].values[0])
            plt.plot(dfSel['Calib_2V5'].values[0],dfSel['adc_mean'].values[0],label="adc"+str(channel))
            plt.plot(dfSel['Calib_2V5'].values[0],dfSel['tot_mean'].values[0],label="tot"+str(channel))
            
            adcTurnoff = dfSel['Calib_2V5'].values[0][dfSel['adc_mean'].values[0]<10].min()
            totTurnon = dfSel['Calib_2V5'].values[0][dfSel['tot_mean'].values[0]<10].max()
            #print (adcTurnoff,totTurnon)
            midPoint = 0.5*(adcTurnoff+totTurnon)
            #print (midPoint)
            plt.plot([midPoint],[0], marker='v')
            
        plt.xlabel("injected charge (Calib_2V5)")
        plt.ylabel("Mean adc/tot")
        plt.grid()
        box = plt.gca().get_position()
        plt.gca().set_position([box.x0, box.y0, box.width, 0.9*box.height])
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.28),ncols=8)
        plt.savefig(
            os.path.join(
                basepath,
                f"chip{chip}_half{half}_totTurnon.png"
            )
        )
        plt.close()
        '''
        plt.figure(figsize=[8,7],dpi=120)
        for channel in range(30,36):#sorted(df['channel'].unique()):
            dfSel = df[(df['chip']==chip)&(df['half']==half)&(df['channel']==channel)]
            #print (dfSel['Calib_2V5'].values[0])
            
            trim_toa = 31+0.5*(dfSel['Calib_2V5'].values[0]-30)
            
            plt.plot(trim_toa,dfSel['toa_fired'].values[0],label=str(channel))
        plt.xlabel("trim_toa")
        plt.ylabel("Counts: toa>0")
        #plt.xlim([0,100])
        plt.grid()
        box = plt.gca().get_position()
        plt.gca().set_position([box.x0, box.y0, box.width, 0.9*box.height])
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.28),ncols=8)
        plt.savefig(
            os.path.join(
                basepath,
                f"chip{chip}_half{half}_trim_toa.png"
            )
        )
        plt.close()
            
        '''
        
        



