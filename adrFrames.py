# -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    For more details see InitGui.py and the LICENCE text file.               *
#*                                                                             *
#*  Module : adrFrames.py                                                      *
#*   Generate fuselage frames from section planes                              *
#*                                                                             *
#*  Dependencies :                                                             *
#*     - adrLibShapesrt : frames generation                                    *
#*                                                                             *
#*  History :                                                                  *
#*     2025-09-19 : Initial release tested on FreeCAD 1.0.2                    *
#*                                                                             *
#*******************************************************************************
''' @package adrFrames
    Produces frames to build the fuselage.
 

'''
__title__="FreeCAD Ader Frames."
__author__ = "Claude GUTH"
__url__ = ""


import FreeCAD as App 
import FreeCADGui as Gui
import os
from math import pi, cos, sin, atan, radians
from pathlib import Path
from PySide import QtUiTools
import adrLibShapes

debugFrames= False

# resources ui, icon
import adrWBCommon as wb
#ui_file=  os.path.join(wb.resources_path, 'adrFrames.ui')
icon_cmd= os.path.join(wb.icons_path,     'adrFrames.svg')

	
	
class CommandFrames:
    "the Frames command definition"

    def GetResources(self):
        return {'Pixmap': icon_cmd, 
		'MenuText': wb.translate("Ader","Frames"),
		'ToolTip' : wb.translate("Ader","Sections to frames")}

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):

        # make Frames
        adrLibShapes.MakeFramesFromPlanes()
    
        # display
        App.ActiveDocument.recompute()


if App.GuiUp:
    #register the FreeCAD command
    Gui.addCommand('adrFrames', CommandFrames())
