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

basepath = "/home/mkomm/Analysis/HGCAL/cerntestbeam/toacinj"

df = pd.DataFrame(columns=["chip","half","channel","Calib_2V5","toa_fired"])

for folder in os.listdir(basepath):
    if not os.path.isdir(os.path.join(basepath,folder)):
        continue
    print (folder)
    
    for f in os.listdir(os.path.join(basepath,folder)):
        match = re.match("chip([0-9]+)_half([0-9]+)_channel([0-9]+)_toacinj.h5py",f)
        if match:
            chip = int(match.group(1))
            half = int(match.group(2))
            channel = int(match.group(3))
            
            inputFile = h5py.File(os.path.join(basepath,folder,f),"r")
            Calib_2V5 = inputFile["Calib_2V5"][:]
            toa_fired = inputFile["toa_fired"][:]
            df.loc[len(df)]={
                "chip": chip, "half": half, "channel": channel,
                "Calib_2V5": Calib_2V5, "toa_fired": toa_fired
            }

print (df)


for chip in sorted(df['chip'].unique()):
    for half in sorted(df['half'].unique()):
        plt.figure(figsize=[8,7],dpi=120)
        for channel in range(0,6):#sorted(df['channel'].unique()):
            dfSel = df[(df['chip']==chip)&(df['half']==half)&(df['channel']==channel)]
            #print (dfSel['Calib_2V5'].values[0])
            plt.plot(dfSel['Calib_2V5'].values[0],dfSel['toa_fired'].values[0],label=str(channel))
        plt.xlabel("injected charge (Calib_2V5)")
        plt.ylabel("Counts: toa>0")
        plt.xlim([0,100])
        plt.grid()
        box = plt.gca().get_position()
        plt.gca().set_position([box.x0, box.y0, box.width, 0.9*box.height])
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.28),ncols=8)
        plt.savefig(
            os.path.join(
                basepath,
                f"chip{chip}_half{half}_toaTurnon.png"
            )
        )
        plt.close()
            
            
        
        



