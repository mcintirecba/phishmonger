#################
# VERSION 1.0.0 #
#################

###########
# IMPORTS #
###########

import bz2
import sys
import os
import json
from datetime import datetime
from subprocess import call
import time
import requests
import shutil

from pullPhish import *

from twisted.internet import reactor, task
from twisted.internet.defer import Deferred

#################
# CONFIGURATION #
#################

timeout = (60 * 60) # set up loop for 1 hour (3600 seconds); adjust as desired

#############
# MAIN LOOP #
#############

def doTwistedPull509 (err):
    print(err)
    print("Stopping due to error...\n\n---\n")

l = task.LoopingCall( doTwistedPull )

t = l.start(timeout)

t.addErrback(doTwistedPull509)

reactor.run()
