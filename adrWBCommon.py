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

import configparser
import os
import FreeCAD as App
import FreeCADGui as Gui
import PySide
from PySide import QtCore
from PySide import QtGui

# debug messages handling
localDebug= False;        # debug msg for this unit     

# Qt translation handling
translate = App.Qt.translate
#def translate(context, text, disambig=None):
#    return QtCore.QCoreApplication.translate(context, text, disambig)

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

def InTaskPanel(CommandClass, ui_file):
    """
    ui_file in FreeCAD TaskPanel.
     """
    CommandClass.form = Gui.PySideUic.loadUi(ui_file)

    if hasattr(CommandClass, 'LocalInitTaskValues'):
        InitComplete = CommandClass.LocalInitTaskValues()
    else:
        InitComplete = False
        
    if not InitComplete:
        InitFormValues(CommandClass.form)

    Gui.Control.showDialog(CommandClass)

def TaskTerminated(CommandClass):
    """
    Save values and close TaskPanel.
     """
    if hasattr(CommandClass, 'LocalSaveTaskValues'):
        SaveComplete = CommandClass.LocalSaveTaskValues()
    else:
        SaveComplete = False
        
    if not SaveComplete:
        SaveFormValues(CommandClass.form)

    Gui.Control.closeDialog()

# persistance handling

iniFilename=os.path.join(base_path, "Ader.ini")
def GetValue(section, key, defaultValue):
    """
    Get persistant value (str, int, float ou bool) from Ader.ini file.
     """
    config = configparser.ConfigParser()
    config.optionxform = str  # case sensitive
    
    if os.path.exists(iniFilename):
        config.read(iniFilename, encoding='utf-8')
    else:
        return defaultValue

    if section not in config:
        return defaultValue
    elif key not in config[section]:
        return defaultValue  
    else:
        raw_value = config[section][key]
        # Cast ?
        for caster in (str_to_bool, int, float):
            try:
                return caster(raw_value)
            except ValueError:
                pass
        
        return raw_value  # default

def SaveValue(section, key, value):
    """
    Save persistant value (str, int, float ou bool) in Ader.ini file.
    """
    config = configparser.ConfigParser()
    config.optionxform = str  # case sensitive
    
    if os.path.exists(iniFilename):
        config.read(iniFilename, encoding='utf-8')
    
    if section not in config:
        config[section] = {}
    
    config[section][key] = str(value)
    
    with open(iniFilename, 'w', encoding='utf-8') as f:
        config.write(f)
    
    return True

def str_to_bool(s):
    """ Cast 'true', 'false', '1', '0' as bool."""
    s_lower = s.strip().lower()
    if s_lower in ('true', '1', 'yes', 'on'):
        return True
    elif s_lower in ('false', '0', 'no', 'off'):
        return False
    else:
        raise ValueError(f"Not a boolean : {s}")

def InitFormValues(form):
    """
    Set widgets persistent values.
    """
    section = form.objectName() if hasattr(form, 'objectName') else None
    if not section:
        return

    for w in form.findChildren(QtCore.QObject):
        key = w.objectName() if hasattr(w, 'objectName') else None

        # set value, default with current object
        if key:
            if hasattr(w, "setValue"):
                w.setValue(GetValue(section, key, w.value()) )          
            elif hasattr(w, "setChecked"):
                w.setChecked(GetValue(section, key, w.isChecked()) )
            elif isinstance(w, QtGui.QLineEdit):
                w.setText(GetValue(section, key, w.text()) )
            elif isinstance(w, QtGui.QPlainTextEdit) or isinstance(w, QtGui.QTextEdit):
                default_value = w.toPlainText() # todo
            elif isinstance(w, QtGui.QComboBox):
                # try current text
                #default_value = w.currentText() if w.currentText() else w.currentIndex()
                w.setCurrentIndex(GetValue(section, key, w.currentIndex()) )
            elif hasattr(w, "date") and hasattr(w, "setDate"):
                # QDateEdit / QDateTimeEdit -> use ISO string
                try:
                    default_value = w.date().toString(QtCore.Qt.ISODate)
                except Exception:
                    default_value = None
 			
def SaveFormValues(form):
    """
	Save widgets persistent values.
    """

    section = form.objectName() if hasattr(form, 'objectName') else None
    if not section:
        return

    for w in form.findChildren(QtCore.QObject):
        key = w.objectName() if hasattr(w, 'objectName') else None
        debugMsg(key, localDebug)

        # valeur par défaut prise depuis l'état courant du widget
        if key:
            if hasattr(w, "setValue"):
                SaveValue(section, key, w.value())           
            elif hasattr(w, "setChecked"):
                SaveValue(section, key, w.isChecked()) 
            elif isinstance(w, QtGui.QLineEdit):
                SaveValue(section, key, w.text()) 
            elif isinstance(w, QtGui.QPlainTextEdit) or isinstance(w, QtGui.QTextEdit):
                SaveValue(section, key, w.toPlainText())
            elif isinstance(w, QtGui.QComboBox):
                SaveValue(section, key, w.currentIndex())
            elif hasattr(w, "date") and hasattr(w, "setDate"):
                # QDateEdit / QDateTimeEdit -> use ISO string
                try:
                    default_value = w.date().toString(QtCore.Qt.ISODate)
                    SaveValue(section, key, default_value)
                except Exception:
                    default_value = None
