from dataManager import *
from utils import *

import sys
import re
import numpy as np
import itertools
import os
import time
from threading import Thread, Semaphore, RLock

lockZ = RLock()
zipper_exec_time=dict()

class Zipperposition(Thread):

    def __init__(self, zf_dir,chapter,lemme,timeout=30,mem_limit=4000):
        Thread.__init__(self)
        self.zf_dir=zf_dir
        self.chapter=chapter
        self.lemme=lemme
        self.timeout=timeout
        self.mem_limit=mem_limit

    def run(self):
        global zipper_exec_time
        t=time.time()
        lemme_file=self.zf_dir+self.chapter+"/"+self.lemme
        if os.path.isfile(lemme_file+".zf") :
            res=os.popen("zipperposition -o none --mem-limit "+str(self.mem_limit)+" --timeout "+str(self.timeout)+" "+lemme_file+".zf").read()
            with lockZ :
                if res.endswith("output end Refutation\n") :
                    print(self.lemme+" : Valid")
                    zipper_exec_time[self.chapter][self.lemme]=(time.time()-t)
                else:
                    print(self.lemme+" : Error")
                    zipper_exec_time[self.chapter][self.lemme]=res
        else :
            with lockZ :
                print("FileNotFoundError : "+lemme_file+".zf")

def get_zipper_stat(zipper_exec_time):
	"""
	Retourne l'ensemble des théorèmes prouvés (done), non prouvés (notdone), abandonnées par manque d'information (gaveup), dont la preuve n'est pas trouvé dans le temps imparti (timeout), dont la preuve demande trop de memoire ou temps (ressourceout). timeout et ressourceout sont disjoints.
	"""
	done=[]
	notdone=[]
	gaveup=[]
	ressourceout=[]
	timeout=[]
	for chapter in zipper_exec_time :
		for lemme in zipper_exec_time[chapter] :
		    if isinstance(zipper_exec_time[chapter][lemme],float) :
		        done.append(lemme)
		    else :
		        if "GaveUp" in zipper_exec_time[chapter][lemme] :
		            gaveup.append(lemme)
		        else :
		            if "for" in zipper_exec_time[chapter][lemme] :
		                timeout.append(lemme)
		            else :
		                ressourceout.append(lemme)
		        notdone.append(lemme)
	return (done,notdone,gaveup,ressourceout,timeout)

def zipper_stat(done,notdone,gaveup,ressourceout,timeout):
	"""
	Affiche les informations de get_zipper_stat sous forme de stats
	"""
	res = str(len(done)/(len(done)+len(notdone))*100)+"% done = "+str(len(done))+" notdone = "+str(len(notdone))
	if len(notdone) > 0 :
		res+=", as notdone : GaveUp = "+str(len(gaveup)/len(notdone)*100)+"% TimeOut = "+str(len(timeout)/len(notdone)*100)+"% RessourceOut = "+str(len(ressourceout)/len(notdone)*100)+"% size = "+str(len(done)+len(notdone))
	return res
