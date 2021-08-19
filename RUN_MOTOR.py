#!bin/python

import os
from subprocess import Popen
import threading
import robotguiV4
#import ROOT
import time

top_dir = os.getcwd()

# start robot
print('')
print('Opening robot gui...')
print('')
robot_thread = threading.Thread(target=robotguiV4.run)
robot_thread.start()

# start event display
#eventDisplayCode = """
#include "EventDisplay.C"
#"""
#ROOT.gInterpreter.ProcessLine(eventDisplayCode)
#evd_thread = threading.Thread(target=EventDisplay, args=(top_dir,))
#ROOT.EventDisplay(top_dir)
#evd.Open()
#time.sleep(10)
#print 'heyy'
#command = 'python '+str(guipath)
#proc = Popen([command], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

#print('')
#print('Running event display...')
#print('')

#command = 'root -l \'./evd/EventDisplay.C(\"'+evd_dir+'\")\''
#os.system(command)
