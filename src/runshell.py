#13 Lines
import os,subprocess

def runccppprocess(filename,olddir):

    #f = "gnome-terminal -e " + "\"/bin/bash -c '" + str(filename) + "; exec /bin/bash -i'\""
    #p = subprocess.Popen(f,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    
    if olddir.find(" ")!=-1:
        olddir = olddir[:olddir.find(" ")]+'\\'+olddir[olddir.find(" "):]
    f = "python " + olddir + "/shell.py "+ str(filename)
    p = subprocess.Popen(f,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

def run_independently(filename,olddir):

    if olddir.find(" ")!=-1:
        olddir = olddir[:olddir.find(" ")]+'\\'+olddir[olddir.find(" "):]
    f = str(filename)
    p = subprocess.Popen(f,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
