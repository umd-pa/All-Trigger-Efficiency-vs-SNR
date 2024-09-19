import os
import argparse
import math
import numpy as np
import ROOT
import pickle
import matplotlib.pyplot as plt
from ROOT import gStyle, gPad, kRed
import scipy
import scipy.optimize as opt
from scipy import signal
from scipy.fft import fft, fftfreq, rfft, irfft
from array import array
from ROOT import gStyle, gPad, kRed, TMath
from NuRadioReco.utilities import bandpass_filter
from NuRadioReco.utilities import fft as fft_reco
from NuRadioReco.detector.RNO_G import analog_components

# load the RNO-G library
ROOT.gSystem.Load(os.environ.get('RNO_G_INSTALL_DIR')+"/lib/libmattak.so")

# make sure we have enough arguments to proceed
parser = argparse.ArgumentParser(description='daqstatus example')
parser.add_argument('--file', dest='file', required=True)
parser.add_argument('--att', type=float, required=True)

args = parser.parse_args()
filename = args.file
att_lim = args.att

#voltage calibration coeffs

cal_path = "/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/volCalConsts_pol9_s23_1697181551-1697183024.root"
#cal_path = "/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/volCalConsts_pol9_s11_1719015822-1719017482.root"
fIn = ROOT.TFile.Open(filename)
combinedTree = fIn.Get("combined")


volCalib = ROOT.mattak.VoltageCalibration()
volCalib.readFitCoeffsFromFile(cal_path)

d = ROOT.mattak.DAQStatus()
wf = ROOT.mattak.Waveforms()
hdr = ROOT.mattak.Header()

combinedTree.SetBranchAddress("daqstatus", ROOT.AddressOf(d))
combinedTree.SetBranchAddress("waveforms", ROOT.AddressOf(wf))
combinedTree.SetBranchAddress("header", ROOT.AddressOf(hdr))

num_events = combinedTree.GetEntries()

rms_all = []


#high pass filter (butterworth) to eliminate noise

def apply_butterworth(spectrum, frequencies, passband, order=8):
    f = np.zeros_like(frequencies, dtype=complex)
    mask = frequencies > 0
    b, a = scipy.signal.butter(order, passband, 'highpass', analog=True)
    w, h = scipy.signal.freqs(b, a, frequencies[mask])
    f[mask] = h
    filtered_spectrum = f * spectrum

    return filtered_spectrum

chs = [0,1,2,3]
rms_all = dict()

for ch in chs:
    rms_all[ch] = []

for event in range(num_events):
    combinedTree.GetEntry(event)

    sysclk = hdr.sysclk
    sysclk_last_pps = hdr.sysclk_last_pps
    sys_diff = (sysclk - sysclk_last_pps)%2**(32)

    #calculating the noise rms

    if (hdr.trigger_info.force_trigger == True):
        for ch in chs:
            c = ROOT.mattak.CalibratedWaveforms(wf, hdr, volCalib, False)
            g = c.makeGraph(ch)

            voltage = g.GetY()
            time = g.GetX()


            voltage_0 = []

            for v in voltage:
                voltage_0.append(v - voltage[0])

            n_samples = len(time)
            sampling_frequency = 1/(time[1] - time[0])
            pb2 = 0.05  #for the high pass filter

            spectrum = fft_reco.time2freq(voltage_0, sampling_frequency)
            frequencies = np.fft.rfftfreq(n_samples, 1 / sampling_frequency)

            filtered_hi = apply_butterworth(spectrum, frequencies, pb2, 8)
            filtered_trace = fft_reco.freq2time(filtered_hi, sampling_frequency)


            rms = np.sqrt(np.mean(filtered_trace**(2)))
            rms_all[ch].append(rms)

            del g
            del c

rms_avg = dict()
for ch in chs:
    rms = rms_all[ch]
    rms_avg[ch] = np.average(rms)

snr_arr = []

chs = [0,1,2,3]

ch_arr = []

for event in range(num_events):
    combinedTree.GetEntry(event)

    sysclk = hdr.sysclk
    sysclk_last_pps = hdr.sysclk_last_pps
    sys_diff = (sysclk - sysclk_last_pps)%(2**(32))

    att = d.calinfo.attenuation

    #calculating snr at a particular attenuation (att_lim)

    if att == att_lim:
        if (sys_diff <= 200*10**(3)):
            snr_event = []
            for ch in chs:
                c = ROOT.mattak.CalibratedWaveforms(wf, hdr, volCalib, False)
                g = c.makeGraph(ch)

                voltage = g.GetY()
                time = g.GetX()

                voltage_0 = []

                for v in voltage:
                    voltage_0.append(v - voltage[0])

                n_samples = len(time)

                sampling_frequency = 1/(time[1] - time[0])
                pb2 = 0.05

                spectrum = fft_reco.time2freq(voltage_0, sampling_frequency)
                frequencies = np.fft.rfftfreq(n_samples, 1 / sampling_frequency)

                #applying high pass filter followed by real low pass filter

                filtered_hi = apply_butterworth(spectrum, frequencies, pb2, 8)
                filtered_trace = fft_reco.freq2time(filtered_hi, sampling_frequency)
                
                #snr calculation
                rms = rms_avg[ch]
                high = np.max(filtered_trace)
                low = np.min(filtered_trace)
                snr = (high-low)/2./rms

                snr_event.append(snr)

                del g

            #picking second highest SNR amongst channels and applying scaling factor (0.54)

            sorted_snr = sorted(snr_event)

            snr_arr.append(sorted_snr[-2] * 0.54)

            ch_arr.append(snr_event.index(sorted_snr[-2]))

np.save(f'/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/snr_npy_23_0.54/snr_{att_lim}.npy', snr_arr)
np.save(f'/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/ch_npy_23_0.54/ch_{att_lim}.npy', ch_arr)
