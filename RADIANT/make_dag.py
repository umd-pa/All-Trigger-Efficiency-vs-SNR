#!/usr/env python 
import numpy as np

#run make_snr_bin.py for specified attenuations (att_unique) and channels (chs)

att_unique  = np.arange(0, 32, 0.5)
#att_unique = [10, 15, 20, 5, 31.5]
#runs = [4809, 4811, 4813, 4815, 4820]
chs = [0,1,2,3]

dag = ""
for i in range(len(att_unique)):
    att = att_unique[i]
    run = 3400 
    job_name = f"{att}_sim"
    cmd = f"JOB {job_name} att.sub\n"
    cmd += f"VARS {job_name} job_name=\"{job_name}\""
    cmd += f" cmd=\"'python3 /data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/make_snr_bin_ch_clean.py "
    cmd += f"--file /data/i3store/users/avijai/rnog_tutorials/station23/run{run}/combined.root "
    cmd += f"--att {att} "
    cmd += "'"
    cmd += f"\"\n"
    dag += cmd

open("att_new.dag", 'w').write(dag)





