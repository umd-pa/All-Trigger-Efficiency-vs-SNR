# Updated-In-Situ-Trigger-Efficiency-vs-SNR
Updated in-situ trigger efficiency vs SNR curves with scaling factor (0.54) for the 2/4 hit multiplicity trigger

1) Run python3 make_dag.py to generate att_new.dag.
2) Run condor_submit_dag att_new.dag to generate SNR files for each attenuation 0-32 dB in 0.5 dB intervals for channels 0,1,2,3. The 2nd highest SNR across the 4 channels is saved.
 - The attenuation range and channels can be modified in make_dag.py
 - att.sub and att_new.sh defines the environment and paths to log files.
 - voltage calibration constants for station 23 run 3400 and station 11 are provided, can be used in make_snr_bin_ch_clean.py (cal_path)
3) Run python3 plot_snr_att.py to obtain the plot of SNR vs attenuation
 - define the directory where the saved SNR files are located ("indir")
 - can modify initial fitting parameters in the scipy.optimize.curve_fit function which defines the exponential fit
4) Run python3 plot_trig_snr_clean.py --file /path/to/combined.root for station 23 to obtain plots of the trigger efficiency vs SNR and trigger efficiency vs attenuation.
  - define calibration constants path (cal_path) and directory with saved SNRs ("indir")
  - put initial fitting parameters for SNR vs attenuation in the scipy.optimize.curve_fit function
  - modify fit parameters for the logistic function fit under log_fit.SetParameter()
  - modify range of the logistic function fit in log_fit (also explains each parameter as fit for in log_fit.SetParameter)
   
