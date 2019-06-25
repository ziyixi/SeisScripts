#!/usr/bin/env python
import os
import sys
import subprocess
import numpy as np
from obspy.core import UTCDateTime
import argparse

# for the obs data you must consider everything: three components not the same length, not the same starttime, the trace is too short than ecpected, some trace unable to open .........
# suppose these data is pre-processed to remove the instrument response to displacement, added event information, added station information 


def get_args(args=None):
    parser = argparse.ArgumentParser(
        description='pre-proc obs and syn data (depth pert and/or cmt3d pert)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--pert_type',
                        help='the flag to define the type of perturbation. 0 is depth, 6 is cmt, 9 is all',
                        required=True)
    parser.add_argument('--pert_code',
                        help='the name of perturbation, obs is observations, others like 00,u1,d1 use comma to separate different perts... if pert_type!=0, this parameter is null',
                        required=True)

    parser.add_argument('--cmtfile',
                        help='original (non-perturbed) cmt file name',
                        required=True)

    parser.add_argument('--stafile',
                        help='station list file name',
                        required=True)

    parser.add_argument('--evtnm',
                        help='event name (in cmtsolution style)',
                        required=True)
    
    parser.add_argument('--basedir',
                        help='basement directory name',
                        required=True)
    
    parser.add_argument('--period_max',
                        help='max period in seconds',
                        required=True)
    
    parser.add_argument('--period_min',
                        help='min period in seconds',
                        required=True)

    results = parser.parse_args(args)
    # return results["base"], results["cmtfiles"], results["ref"], results["output"]
    return results.pert_type, results.pert_code, results.cmtfile, results.stafile, results.evtnm, results.basedir, results.period_max, results.period_min

if __name__ == "__main__":
    pert_type, pert_code, cmtsolution, stafile, evtnm, basedir, period_max, period_min = get_args(sys.argv[1:])
    pert_type = int(pert_type)
    if(pert_type==0):
        if(pert_code=='obs'):
            npar = 0
            parlist = []
        else:
            parlist = pert_code.strip().split(",")
            npar = len(parlist)
    else:
        npar = pert_type
        if(npar==6):
            parlist = ["Mrr","Mtt","Mpp","Mrp","Mrp","Mtp"]
        else:
            parlist = ["Mrr","Mtt","Mpp","Mrp","Mrp","Mtp",'lat','lon','dep']
    ###print info####
    print("pert_type="+str(pert_type))
    print("pert_code="+str(pert_code))
    print("par_list="+str(parlist))
    synoutdir = basedir+"/syn_processed"
    obsoutdir = basedir+"/obs_processed"
    freq1 = 1./float(period_min)
    freq2 = 1./float(period_max)
    resample_delta = float(1./10)   # resample to 10Hz sampling rate
    print("filter tp %f %f Hz" %(freq2,freq1))
    # read cmtsolution file
    fcmt = open(cmtsolution,'r')
    cmtm = fcmt.readline().strip().split()
    cmttime = UTCDateTime(cmtm[1]+"-"+cmtm[2]+"-"+cmtm[3]+"T"+cmtm[4]+":"+cmtm[5]+":"+cmtm[6]+"Z") 
    print(cmttime)
    fsta = open(stafile,'r')
    if(not os.path.exists(synoutdir)):
         os.mkdir(synoutdir)
    if(not os.path.exists(obsoutdir)):
         os.mkdir(obsoutdir)
    if(pert_code=='obs' or pert_type!=0):
        stalist_used = open(basedir+"/stations_used.txt",'w')   # output used station file for next step
    # loop on stations
    for sta in fsta.readlines():
        staline = sta.strip().split()
        stnm = staline[0]
        netwk = staline[1]
        obsdir = basedir+"/"+evtnm
        # add obs data
        if(pert_type!=0 or pert_code=='obs'):    # no need to add obs data if pert_code is specified
            obsz = obsdir+"/"+netwk+"."+stnm+"..BHZ"
            if(os.path.isfile(obsz)):
                obsn = obsdir+"/"+netwk+"."+stnm+"..BHN"
                obse = obsdir+"/"+netwk+"."+stnm+"..BHE"
                if(not os.path.isfile(obsn)):
                    obsn = obsdir+"/"+netwk+"."+stnm+"..BH2"
                    if(os.path.isfile(obsn)):
                        obse = obsdir+"/"+netwk+"."+stnm+"..BH1"
                    else:
                        print("horiz comp missing %s" %(obsn))
                        continue
            else:
                obsz = obsdir+"/"+netwk+"."+stnm+".00.BHZ"
                if(os.path.isfile(obsz)):
                    obsn = obsdir+"/"+netwk+"."+stnm+".00.BHN"
                    obse = obsdir+"/"+netwk+"."+stnm+".00.BHE"
                    if(not os.path.isfile(obsn)):
                        obsn = obsdir+"/"+netwk+"."+stnm+".00.BH2"
                        if(os.path.isfile(obsn)):
                            obse = obsdir+"/"+netwk+"."+stnm+".00.BH1"
                        else:
                            print("horiz comp missing %s" %(obsn))
                            continue
                else:
                    obsz = obsdir+"/"+netwk+"."+stnm+".01.BHZ"
                    if(os.path.isfile(obsz)):
                        obsn = obsdir+"/"+netwk+"."+stnm+".01.BHN"
                        obse = obsdir+"/"+netwk+"."+stnm+".01.BHE"
                        if(not os.path.isfile(obsn)):
                            obsn = obsdir+"/"+netwk+"."+stnm+".01.BH2"
                            if(os.path.isfile(obsn)):
                                obse = obsdir+"/"+netwk+"."+stnm+".01.BH1"
                            else:
                                print("horiz comp missing %s" %(obsn))
                                continue
                    else:
                        print("no such file %s" %(obsz))
                        continue
  
            # rotate and filter using sac
            # use the filtered stations (snr checked), check delta and npts, remove bad files
            # saclst is not a typical 'Error', you can't even use try/except to catch it, only to check dim of output
            cmd = 'saclst b e delta f {}'.format(obsz).split()
            try:
                output = subprocess.check_output(cmd)
            except subprocess.CalledProcessError as e:
                print("skip ".format(e).split())
                continue
            if(not output):
                print("file is broken {}, skip".format(obsz).split())
                continue
            Zb, Ze, Zdelta = output.decode().split()[1:]
            cmd = 'saclst b e delta f {}'.format(obsn).split()
            try:
                output = subprocess.check_output(cmd)
            except subprocess.CalledProcessError as e:
                print("skip ".format(e).split())
                continue
            if(not output):
                print("file is broken {}, skip".format(obsz).split())
                continue
            Nb, Ne, Ndelta = output.decode().split()[1:]
            cmd = 'saclst b e delta f {}'.format(obse).split()
            try:
                output = subprocess.check_output(cmd)
            except subprocess.CalledProcessError as e:
                print("skip ".format(e).split())
                continue
            if(not output):
                print("file is broken {}, skip".format(obsz).split())
                continue
            Eb, Ee, Edelta = output.decode().split()[1:]
            
            if not (float(Zdelta) == float(Edelta) and float(Zdelta) == float(Ndelta)):
                print("%s: delta not equal!" % netwk+"."+stnm)   # remove the three traces has unequal sampling rate
                continue
                
            # change cmpinc (somethhing wrong with OBSPY downloads)
            s = "r %s \n" % (obsz)
            s += "ch cmpinc 0 \n"
            s += "w over \n"
            s += "r %s \n" % (obsn)
            s += "ch cmpinc 90 \n"
            s += "w over \n"
            s += "r %s \n" % (obse)
            s += "ch cmpinc 90 \n"
            s += "w over \n"
            s += "q \n"
            p = subprocess.Popen(['sac'],stdin=subprocess.PIPE).communicate(s.encode())

            # select max b and min e to avoid unequal npts
            
            # cut all the traces to be the same 
            begin = max(float(Zb), float(Eb), float(Nb))
            end = min(float(Ze), float(Ee), float(Ne))
            obsr = obsoutdir+"/"+netwk+"."+stnm+"..R"
            obst = obsoutdir+"/"+netwk+"."+stnm+"..T"
            obsz0 = obsoutdir+"/"+netwk+"."+stnm+"..Z"
            print(obsz0)
            saccmd = "cut b %f b %f \n" % (begin,end)
            saccmd += "r %s %s \n" % (obse,obsn)
            saccmd += "rotate to gcp \n"
            saccmd += "bp co %f %f \n" % (freq2,freq1)
            saccmd += "w %s %s \n" % (obsr,obst)
            saccmd += "r %s \n" % (obsz)
            saccmd += "bp co %f %f \n" % (freq2,freq1)
            saccmd += "w %s \n" % (obsz0)
            saccmd += "q \n"
            p = subprocess.Popen(['sac'],stdin=subprocess.PIPE).communicate(saccmd.encode())
            # cut traces: starting time is the event origin time, ending time is 20 mins
            # each component may have different b. Treat separately
            # get starting time for the current observation
            # if the trace time is less than 20 minutes, there must be a bug (downloaded 25 minutes total!, remove them)
            # get R
            cmd = 'saclst kzdate kztime b f {}'.format(obsr).split()
            kzdate, kztime, b = subprocess.check_output(cmd).decode().split()[1:]
            obstime = UTCDateTime(kzdate+" "+kztime) #+ float(b)## here use interp, the time is relative to kztime, do not need to consider b
            print(obstime)
            begin = cmttime - obstime
            if(begin < 0):            # check if the obs start time is after the centroid time, drop this station
                print("station begin time after centroid time for {}, drop".format(obsr))
                continue
                
            # cut R
            saccmd = "r %s \n" % (obsr)
            saccmd += "interp delta %f begin %f \n" %(resample_delta,begin)
            saccmd += "ch o %f \n" %(begin)      # correct the event time
            saccmd += "w over \n"
            saccmd += "cut b 0 b 1200 \n"        # here the time is relative to b 
            saccmd += "r %s \n" % (obsr)
            saccmd += "ch allt (0-&1,o&) \n"
            saccmd += "ch kcmpnm BHR \n"
            saccmd += "w over \n"
            saccmd += "q \n"
            p = subprocess.Popen(['sac'],stdin=subprocess.PIPE).communicate(saccmd.encode())
            # get T
            cmd = 'saclst kzdate kztime b f {}'.format(obst).split()
            kzdate, kztime, b = subprocess.check_output(cmd).decode().split()[1:]
            obstime = UTCDateTime(kzdate+" "+kztime) 
            begin = cmttime - obstime
            # cut T
            saccmd = "r %s \n" % (obst)
            saccmd += "interp delta %f begin %f \n" %(resample_delta,begin)
            saccmd += "ch o %f \n" %(begin)      # correct the event time
            saccmd += "w over \n"
            saccmd += "cut b 0 b 1200 \n"
            saccmd += "r %s \n" % (obst)
            saccmd += "ch allt (0-&1,o&) \n"
            saccmd += "ch kcmpnm BHT \n"
            saccmd += "w over \n"
            saccmd += "q \n"
            p = subprocess.Popen(['sac'],stdin=subprocess.PIPE).communicate(saccmd.encode())
            # get Z
            cmd = 'saclst kzdate kztime b f {}'.format(obsz0).split()
            kzdate, kztime, b = subprocess.check_output(cmd).decode().split()[1:]
            obstime = UTCDateTime(kzdate+" "+kztime) 
            begin = cmttime - obstime
            # cut Z
            saccmd = "r %s \n" % (obsz0)
            saccmd += "interp delta %f begin %f \n" %(resample_delta,begin)
            saccmd += "ch o %f \n" %(begin)      # correct the event time
            saccmd += "w over \n"
            saccmd += "cut b 0 b 1200 \n"
            saccmd += "r %s \n" % (obsz0)
            saccmd += "ch allt (0-&1,o&) \n"
            saccmd += "ch kcmpnm BHZ \n"
            saccmd += "w over \n"
            saccmd += "q \n"
            p = subprocess.Popen(['sac'],stdin=subprocess.PIPE).communicate(saccmd.encode())
            # check begin time and npts
            # R
            cmd = 'saclst kztime npts f {}'.format(obsr).split()
            kztime, Rnpts = subprocess.check_output(cmd).decode().split()[1:]
            cmd = 'saclst b kzdate f {}'.format(obsr).split()
            b, kzdate = subprocess.check_output(cmd).decode().split()[1:]
            #print(b[0:],type(b[0:]))
            Robst = UTCDateTime(kzdate+" "+kztime) + float(b)
            # T
            cmd = 'saclst kztime npts f {}'.format(obst).split()
            kztime, Tnpts = subprocess.check_output(cmd).decode().split()[1:]
            cmd = 'saclst b kzdate f {}'.format(obst).split() # if only b it is a list, sep for neg values not merged
            b, kzdate = subprocess.check_output(cmd).decode().split()[1:]
            Tobst = UTCDateTime(kzdate+" "+kztime) + float(b)
            # Z
            cmd = 'saclst kztime npts f {}'.format(obsz0).split()
            kztime, Znpts = subprocess.check_output(cmd).decode().split()[1:]
            cmd = 'saclst b kzdate f {}'.format(obsz0).split()
            b, kzdate = subprocess.check_output(cmd).decode().split()[1:]
            Zobst = UTCDateTime(kzdate+" "+kztime) + float(b)
            npts_should = int(20*60/resample_delta) + 1  # there should be such data points, if not, throw them away
            if not (int(Rnpts)==npts_should and int(Tnpts)==npts_should and int(Znpts)==npts_should 
                    and np.isclose(Robst-Zobst,0) and np.isclose(Robst-Tobst,0)):
                print("obs station %s incoherent, removed" %(netwk+"."+stnm))
                cmd = "rm %s %s %s" %(obsr,obst,obsz0)
                print(cmd)
                try:
                    subprocess.Popen(cmd)
                except:
                    print("file not found")
                continue
  
            print("processed obs station "+netwk+"."+stnm)
            stalist_used.writelines(sta)
        
        # add syn data
        # CMT3D pert, add 'ori' first
        if(pert_type==6 or pert_type==9):
            syndir = basedir+"/syn_data/syn_ori_"+evtnm
            synz = syndir+"/"+netwk+"."+stnm+".BXZ.sem.sac"
            synn = syndir+"/"+netwk+"."+stnm+".BXN.sem.sac"
            syne = syndir+"/"+netwk+"."+stnm+".BXE.sem.sac"
            synr = synoutdir+"/"+netwk+"."+stnm+"..R"
            synt = synoutdir+"/"+netwk+"."+stnm+"..T"
            synz0 = synoutdir+"/"+netwk+"."+stnm+"..Z"
            # get begin time for current synthetics
            # synthetics 3 components have the same info, no need treat separately
            cmd = 'saclst kzdate kztime b f {}'.format(syne).split()
            kzdate, kztime, b = subprocess.check_output(cmd).decode().split()[1:]
            syntime = UTCDateTime(kzdate+" "+kztime) #+ float(b)
            print(syntime)
            begin = cmttime - syntime
            saccmd = "r %s %s \n" % (syne,synn)
            saccmd += "rotate to gcp \n"
            saccmd += "bp co %f %f \n" % (freq2,freq1)
            saccmd += "w %s %s \n" % (synr,synt)
            saccmd += "r %s \n" % (synz)
            saccmd += "bp co %f %f \n" % (freq2,freq1)
            saccmd += "w %s \n" % (synz0)
            saccmd += "q \n"
            p = subprocess.Popen(['sac'],stdin=subprocess.PIPE).communicate(saccmd.encode())
            # cut the same windows
            saccmd = "r %s %s %s \n" % (synr,synt,synz0)
            saccmd += "interp delta %f begin %f \n" %(resample_delta,begin)
            saccmd += "w over \n"
            saccmd += "cut b 0 b 1200 \n"
            saccmd += "r %s %s %s \n" % (synr,synt,synz0)
            saccmd += "ch allt (0-&1,o&) \n"
            saccmd += "w over \n"
            saccmd += "q \n"
            p = subprocess.Popen(['sac'],stdin=subprocess.PIPE).communicate(saccmd.encode())
            saccmd = "r %s \n" % (synr)
            saccmd += "ch kcmpnm BHR \n"
            saccmd += "wh \n"
            saccmd += "r %s \n" % (synt)
            saccmd += "ch kcmpnm BHT \n"
            saccmd += "wh \n"
            saccmd += "r %s \n" % (synz0)
            saccmd += "ch kcmpnm BHZ \n"
            saccmd += "wh \n"
            saccmd += "q \n"
            p = subprocess.Popen(['sac'],stdin=subprocess.PIPE).communicate(saccmd.encode())
            # check the synthetics
            # R (example) ##########################
            cmd = 'saclst kzdate kztime b npts f {}'.format(synr).split()
            kzdate, kztime, b, Snpts = subprocess.check_output(cmd).decode().split()[1:]
            Rsynt = UTCDateTime(kzdate+" "+kztime) + float(b)
            obsr = obsoutdir+"/"+netwk+"."+stnm+"..R"
            cmd = 'saclst kztime npts f {}'.format(obsr).split()
            kztime, Rnpts = subprocess.check_output(cmd).decode().split()[1:]
            cmd = 'saclst b kzdate f {}'.format(obsr).split()
            b, kzdate = subprocess.check_output(cmd).decode().split()[1:]
            Robst = UTCDateTime(kzdate+" "+kztime) + float(b)
            if not (abs(Rsynt-Robst)<resample_delta):
                raise ValueError("obs and syn not have the same start time %s" %(synr))
            if not (Snpts==Rnpts):
                raise ValueError("npts not good for station %s" %(synr))
    
        # for pert_type == 0, 6, 9, add all the synthetics
        # add derivative synthetics
        for ipar in range(1,npar+1):
            if(pert_type==6 or pert_type==9):
                syndir = basedir+"/syn_data/syn_"+parlist[ipar-1]+"_"+evtnm
            elif(npar==0):
                print("No synthetics to be added, continue ...")
                continue
            else:
                syndir = basedir + "/syn_data/CMTSOLUTION_"+parlist[ipar-1]+"_"+evtnm
                synz = syndir+"/"+netwk+"."+stnm+".BXZ.sem.sac"
                synn = syndir+"/"+netwk+"."+stnm+".BXN.sem.sac"
                syne = syndir+"/"+netwk+"."+stnm+".BXE.sem.sac"
            print(synz)
            # synthetics 3 components have the same info, no need treat separately
            cmd = 'saclst kzdate kztime b f {}'.format(syne).split()
            kzdate, kztime, b = subprocess.check_output(cmd).decode().split()[1:]
            syntime = UTCDateTime(kzdate+" "+kztime) #+ float(b)
            print(syntime)
            begin = cmttime - syntime
            # rotate and filter using sac
            # SEM synthetics has the same b and e, no need to check
            # add extensions
            synr = synoutdir+"/"+netwk+"."+stnm+"..R."+parlist[ipar-1]
            synt = synoutdir+"/"+netwk+"."+stnm+"..T."+parlist[ipar-1]
            synz0 = synoutdir+"/"+netwk+"."+stnm+"..Z."+parlist[ipar-1]
            saccmd = "r %s %s \n" % (syne,synn)
            saccmd += "rotate to gcp \n"
            saccmd += "bp co %f %f \n" % (freq2,freq1)
            #saccmd += "interp delta %f \n" %(resample_delta)
            saccmd += "w %s %s \n" % (synr,synt)
            saccmd += "r %s \n" % (synz)
            saccmd += "bp co %f %f \n" % (freq2,freq1)
            #saccmd += "interp delta %f \n" %(resample_delta)
            saccmd += "w %s \n" % (synz0)
            saccmd += "q \n"
            p = subprocess.Popen(['sac'],stdin=subprocess.PIPE).communicate(saccmd.encode())
            # cut the same windows
            #saccmd = "cut b %f b %f \n" % (begin,end)
            saccmd = "r %s %s %s \n" % (synr,synt,synz0)
            saccmd += "interp delta %f begin %f \n" %(resample_delta,begin)
            saccmd += "w over \n"
            saccmd += "cut b 0 b 1200 \n"
            saccmd += "r %s %s %s \n" % (synr,synt,synz0)
            saccmd += "ch allt (0-&1,o&) \n"
            saccmd += "w over \n"
            saccmd += "q \n"
            p = subprocess.Popen(['sac'],stdin=subprocess.PIPE).communicate(saccmd.encode())
            saccmd = "r %s \n" % (synr)
            saccmd += "ch kcmpnm BHR \n"
            saccmd += "wh \n"
            saccmd += "r %s \n" % (synt)
            saccmd += "ch kcmpnm BHT \n"
            saccmd += "wh \n"
            saccmd += "r %s \n" % (synz0)
            saccmd += "ch kcmpnm BHZ \n"
            saccmd += "wh \n"
            saccmd += "q \n"
            p = subprocess.Popen(['sac'],stdin=subprocess.PIPE).communicate(saccmd.encode())
            # check the synthetics
            # R (example) ##########################
            cmd = 'saclst kzdate kztime b npts f {}'.format(synr).split()
            kzdate, kztime, b, Snpts = subprocess.check_output(cmd).decode().split()[1:]
            Rsynt = UTCDateTime(kzdate+" "+kztime) + float(b)
            obsr = obsoutdir+"/"+netwk+"."+stnm+"..R"
            cmd = 'saclst kztime npts f {}'.format(obsr).split()
            kztime, Rnpts = subprocess.check_output(cmd).decode().split()[1:]
            cmd = 'saclst b kzdate f {}'.format(obsr).split()
            b, kzdate = subprocess.check_output(cmd).decode().split()[1:]
            Robst = UTCDateTime(kzdate+" "+kztime) + float(b)
            if not (abs(Rsynt-Robst)<resample_delta):
                raise ValueError("obs and syn not have the same start time %s" %(synr))
            if not (Snpts==Rnpts):
                raise ValueError("npts not good for station %s" %(synr))
        print("processed syn station "+netwk+"."+stnm)
    # end loop over stations
    if(pert_code=='obs' or pert_type!=0):
        stalist_used.close()


