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

results = {}

target_trim_tots = {}

with open("trim_tot_default.yaml","r") as f:
    trim_tot_default = yaml.load(f)

for chip in sorted(df['chip'].unique()):
    results[int(chip)] = {}
    target_trim_tots[int(chip)] = {}
    for half in sorted(df['half'].unique()):
        results[int(chip)][int(half)] = {}
        target_trim_tots[int(chip)][int(half)] = {}
        plt.figure(figsize=[8,7],dpi=120)
        print("="*50)
        for channel in range(0,36):#sorted(df['channel'].unique()):
            dfSel = df[(df['chip']==chip)&(df['half']==half)&(df['channel']==channel)]
           
            trim_tot = trim_tot_default[int(chip)][int(half)][int(channel)]
            #adjust for default trim_tot; if trim_tot>31 move point higher
            
           
            Calib_2V5 = dfSel['Calib_2V5'].values[0]
            Calib_2V5_corr = Calib_2V5+2*(trim_tot-31)
           
            plt.plot(Calib_2V5_corr,dfSel['adc_mean'].values[0],label=str(channel))
            plt.plot(Calib_2V5_corr,dfSel['tot_mean'].values[0])
            
            adcTurnoff = dfSel['Calib_2V5'].values[0][dfSel['adc_mean'].values[0]<10]
            totTurnon = dfSel['Calib_2V5'].values[0][dfSel['tot_mean'].values[0]<10]
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
                
            
            #print (adcTurnoff,totTurnon)
            
            #print (f"{chip}/{half}/{channel:2d}: {midPoint:4.1f}")
            plt.plot([midPoint],[0], marker='v')
            
            results[int(chip)][int(half)][int(channel)] = int(midPoint)
            
        plt.xlabel("injected charge (Calib_2V5)")
        plt.ylabel("Mean adc/tot")
        plt.grid()
        plt.ylim([0,1000])
        plt.xlim([400,1000])
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
        
        calib_2V5_values = np.array(list(results[int(chip)][int(half)].values()))
        #median = np.median(calib_2V5_values)
        #print (median,calib_2V5_values)
        
        corrected_calib_2V5 = []
        for ch in sorted(results[int(chip)][int(half)].keys()):
            current_calib_2V5 = results[int(chip)][int(half)][ch]
            trim_tot = trim_tot_default[int(chip)][int(half)][ch]
            #adjust for default trim_tot; if trim_tot>31 move point higher
            corrected_current_calib_2V5 = current_calib_2V5+2*(trim_tot-31)
            corrected_calib_2V5.append(corrected_current_calib_2V5)
        target_calib_2V5 = np.median(corrected_calib_2V5)
        print ("target:",target_calib_2V5)
        
        for ch in sorted(results[int(chip)][int(half)].keys()):
            current_calib_2V5 = int(results[int(chip)][int(half)][int(ch)])
            trim_tot_start = int(trim_tot_default[int(chip)][int(half)][int(ch)])
            target_trim_tot = int(0.5*(current_calib_2V5-target_calib_2V5)+trim_tot_start)
            print (f"{chip}/{half}/{ch:2d}: current={current_calib_2V5:3d} default={trim_tot_start:3d} target={target_trim_tot:3d}")
        
            if target_trim_tot<0 or target_trim_tot>63:
                print ("WARNING: trimming outside valid range")
            target_trim_tots[int(chip)][int(half)][int(ch)]=int(np.clip(0,target_trim_tot,63))
        
        #print (current_calib_2V5,trim_tot)
        #diff = current_calib_2V5-target_calib_2V5
            
        
with open("roc_TB3_A5_1_ConvGain4_toa_aligned.yaml") as f:
    defaultCfg = yaml.load(f)

newCfg = {}
for ch in sorted(defaultCfg['ch'].keys()):
    newCfg[ch] = defaultCfg['ch'][ch]
    newCfg[ch]['trim_tot'] = target_trim_tots[1][ch//36][ch%36]
    
with open("roc_TB3_A5_1_ConvGain4_toatot_aligned.yaml","w") as f:
    yaml.dump({"ch":newCfg},f)
      
            



