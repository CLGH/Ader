# -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    For more details see InitGui.py and the LICENCE text file.               *
#*                                                                             *
#*  Module : adrWBCommon.py                                                    *
#*   Common resources for the Ader workbench                                   *
#*     - path to resources...                                                  *
#*     - translation for python modules                                        *
#*     - messages : debug, console                                             *
#*                                                                             *
#*   History :                                                                 *
#*     2023-07-12 : Initial release Claude GUTH                                *
#*                                                                             *
#*******************************************************************************

__title__="App Ader Common"
__author__ = "Claude GUTH "
__url__ = "https://.fr"

import os
import FreeCAD as App
from PySide import QtCore

# debug messages handling
localDebug= False;        # debug msg for this unit     

# Qt translation handling
# translate = App.Qt.translate
def translate(context, text, disambig=None):
    return QtCore.QCoreApplication.translate(context, text, disambig)

# resources path, files
base_path= os.path.dirname(__file__)
resources_path= os.path.join(base_path, 'resources')
icons_path= os.path.join(resources_path, 'icons')
dat_path= os.path.join(base_path, 'dat_profiles')

# debug messages handling
debug= False;        # global debug         
def debugMsg(msg, localDebug= True):
    if debug or localDebug:
        App.Console.PrintMessage(msg)     

def consoleMsg(msg, type=None):
    if type:
        if type=='W':
            App.Console.PrintWarning(msg)
            exit()
        if type=='E':
            App.Console.PrintError(msg)
            exit()
        App.Console.PrintMessage(msg)
    else:
        App.Console.PrintMessage(msg)

def ListDatProfiles():
    "list profiles in dat_profiles folder (first line)"
    files=[]
    for f in os.listdir(dat_path): 
        if f.endswith(".dat"):
            files.append(f)
    profiles=[]
    for f in files:
        profiles.append(open(os.path.join(dat_path, f), 'r', errors='ignore').readline().strip())
        
    return files, profiles