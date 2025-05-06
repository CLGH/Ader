
# -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    For more details see InitGui.py and the LICENCE text file.               *
#*                                                                             *
#*  Module : adrExport.py                                                      *
#*    Export xml data to CPACS                                                 *
#*                                                                             *
#*  Dependencies :                                                             *
#*                                                                             *
#*  History :                                                                  *
#*    2023-07-15 : Initial release, tested on FreeCAD 0.20                     *
#*                                                                             *
#*******************************************************************************

__title__  = "Ader Workbench - CPACS export"
__author__ = "Claude GUTH"

import FreeCAD as App
import FreeCADGui as Gui
import os
from pathlib import Path
import adrCPACSxChg as toCPACS
import adrWBCommon as wb

localDebug= False

# resources ui, icon
#ui_file= os.path.join(wb.resources_path, 'adrExport.ui')
icon_xpm= os.path.join(wb.icons_path, 'adrExport.xpm')
# translation
def QT_TRANSLATE_NOOP(context, text):
    return text

def ExportWing(wing_name):
    '''Export wing profiles from specifications'''
    doc = App.activeDocument()
    cpacs_file_path = doc.infos.cpacs_filename 
    wing_id = doc.Name + '_wing'
    wing_span = doc.specifications.b
    if hasattr(doc.specifications, 'fleche'):
        wing_sweep = doc.specifications.fleche
    else:
        wing_sweep = 0
    foil_in = Path(doc.specifications.ci_profile).stem
    if hasattr(doc.specifications, 'ce_profile'):
        foil_out = Path(doc.specifications.ce_profile).stem
    else:
        foil_out = foil_in
    wing_ci = doc.specifications.ci
    wedge_in= doc.specifications.ci_cal
    wing_ce = doc.specifications.ce
    wedge_out= doc.specifications.ce_cal
    toCPACS.WingInCPACS(cpacs_file_path, wing_id, wing_span, wing_sweep, foil_in, wing_ci, wedge_in, foil_out, wing_ce, wedge_out)

def ExportProfiles():
    '''Export wing profiles from specifications'''
    doc = App.activeDocument()
    cpacs_file_path = doc.infos.cpacs_filename 
    dat_base_path = os.path.join(wb.base_path, "dat_profiles") + "/"
    dat_int = dat_base_path + doc.specifications.ci_profile  
    toCPACS.DatInCPACS(cpacs_file_path, dat_int)
    if hasattr(doc.specifications, 'ce_profile'):
        dat_ex = dat_base_path + doc.specifications.ce_profile
        # dat_ex = 'C:/Users/MINI PC/AppData/Roaming/FreeCAD/Mod/Ader/dat_profiles/n652-415.dat'
        if (dat_ex != dat_int):
            toCPACS.DatInCPACS(cpacs_file_path, dat_ex)

class CommandExport:
    '''Export profiles >> wing  >> aircraft'''

    def GetResources(self):
        return {'Pixmap': icon_xpm, 
		'MenuText': QT_TRANSLATE_NOOP("Ader","Export"),
		'ToolTip' : QT_TRANSLATE_NOOP("Ader","Export to CPACS file")}

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        #wb.debugMsg(doc.Name + "\n", localDebug)
        # save wing profiles
        # ExportWing("Test")
        ExportProfiles()

if App.GuiUp:
    #register the FreeCAD command
    Gui.addCommand('adrExport', CommandExport())
