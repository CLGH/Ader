# -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    For more details see InitGui.py and the LICENCE text file.               *
#*                                                                             *
#*  Module : adrSections.py                                                    *
#*   Generate section planes                                     *
#*                                                                             *
#*  Dependencies :                                                             *
#*     - adrSections.ui : GUI.                                                 *
#*     - adrLibPart : section plane generation                                 *
#*                                                                             *
#*  History :                                                                  *
#*     2025-09-19 : Initial release tested on FreeCAD 1.0.2                    *
#*                                                                             *
#*******************************************************************************
''' @package adrSections
    Produces planes for intersection with top / side views.
 

'''
__title__="FreeCAD Ader Sections."
__author__ = "Claude GUTH"
__url__ = ""


import FreeCAD as App 
import FreeCADGui as Gui
import os
from math import pi, cos, sin, atan, radians
from pathlib import Path
from PySide import QtUiTools
import adrLibPart

debugSections= False

# resources ui, icon
import adrWBCommon as wb
ui_file=  os.path.join(wb.resources_path, 'adrSections.ui')
icon_cmd= os.path.join(wb.icons_path,     'adrSections.svg')
	
	
class CommandSections:
    "Sections command : create section planes to build fuselage."

    def GetResources(self):
        return {'Pixmap': icon_cmd, 
		'MenuText': wb.translate("Ader","Sections"),
		'ToolTip' : wb.translate("Ader","Create fuselage section planes")}

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        wb.InTaskPanel(self, ui_file)
 
    def accept(self):
        # make sections
        nb= self.form.sbNbSections.value()
        adrLibPart.MakeIntersectionPlanes(nb)
        wb.TaskTerminated(self)
    
        # display
        App.ActiveDocument.recompute()


if App.GuiUp:
    #register the FreeCAD command
    Gui.addCommand('adrSections', CommandSections())
