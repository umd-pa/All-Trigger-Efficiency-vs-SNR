import os, sys, shutil, glob
import argparse
import math
import numpy as np
import ROOT
import pickle
import scipy
import matplotlib.pyplot as plt
from ROOT import gStyle, gPad, kRed
import pandas as pd 
import csv 

# load the RNO-G library
ROOT.gSystem.Load(os.environ.get('RNO_G_INSTALL_DIR')+"/lib/libmattak.so")


#path to files with snr arrays for each attenuation 

indir = "/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/snr_npy_23_0.54"
#indir = "/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/flower_traces/snr_flower_st11"

files = sorted(glob.glob(os.path.join(indir, "*")))


#calculating mean snr value in each attenuation bin 

snr_means = []
snr_std = []
atts = []
atts_12 = []
snr_means_12 = []
for f in files:
    att_one = f.split("/")[-1].split("_")[-1].split(".")[0]
    att_two = f.split("/")[-1].split("_")[-1].split(".")[1]
    att = int(att_one) + 0.1*int(att_two)
    
    snr_arr = np.load(f)

    if (len(snr_arr) != 0):
        atts.append(att)
        snr_means.append(np.average(snr_arr))
        snr_std.append(np.std(snr_arr))
        if (att >= 6 and att <= 13):
            atts_12.append(att)
            snr_means_12.append(np.average(snr_arr))
        

#exponential fit for attenuation between 6-15 dB

#error_upscaling = 0.034/(np.sqrt(len(snr_means_12)))

fit = scipy.optimize.curve_fit(lambda t,a,b: a*np.exp(b*t),  atts_12, snr_means_12,  p0=(17.5, -0.2))
#fit = scipy.optimize.curve_fit(lambda t,a,b: a*np.exp(b*t),  atts_12, snr_means_12,  p0=(30, -0.2))

x_vals = np.arange(0,32, 0.5)
y_vals = []

for x in x_vals:
    y_vals.append(fit[0][0]*np.exp(fit[0][1]*x))


#save values if needed
"""
df_atts = pd.DataFrame(atts)
df_atts.to_csv("/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/snr_att_23_0.54/atts_57.csv", index = False, header = False)

df_snr = pd.DataFrame(snr_means)
df_snr.to_csv("/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/snr_att_23_0.54/snr_57.csv", index = False, header = False)

df_x = pd.DataFrame(x_vals)
df_x.to_csv("/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/snr_att_23_0.54/x_57.csv", index = False, header = False)

df_y = pd.DataFrame(y_vals)
df_y.to_csv("/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/snr_att_23_0.54/y_57.csv", index = False, header = False)

df_yerr = pd.DataFrame(snr_std)
df_yerr.to_csv("/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/snr_att_23_0.54/snr_std_57.csv", index = False, header = False)

"""
#plot snr vs attenuation 


plt.scatter(atts,snr_means, s = 15)
plt.plot(x_vals, y_vals)
plt.errorbar(atts,snr_means, yerr = snr_std, ls = "None")
#plt.errorbar(atts,snr_means, yerr = error_upscaling, ls = "None")
#plt.xlim(0,10)
plt.title("Event SNR vs Attenuation")
plt.xlabel("Attenuation (dB)")
plt.ylabel("Event SNR")
plt.legend()
plt.savefig("/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/snr_vs_att_23_0.54.png")


