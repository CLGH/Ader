# -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    For more details see InitGui.py and the LICENCE text file.               *
#*                                                                             *
#*  Module : adrFrame.py                                                       *
#*   Generate a frame skech                                                    *
#*                                                                             *
#*  Dependencies :                                                             *
#*     - adrFrame.ui : GUI.                                                    *
#*     - adrLibShapes : frame generation                                        *
#*                                                                             *
#*  History :                                                                  *
#*     2025-03-12 : Initial release tested on FreeCAD 1.0.0                    *
#*                                                                             *
#*******************************************************************************
''' @package adrFrame
    Produces a frame sketch.
 

'''
__title__="FreeCAD Ader Frame."
__author__ = "Claude GUTH"
__url__ = ""


import FreeCAD as App 
import FreeCADGui as Gui
import os
from pathlib import Path
from PySide import QtUiTools
import adrLibShapes

debugFrame= False

# resources ui, icon
import adrWBCommon as wb
ui_file=  os.path.join(wb.resources_path, 'adrFrame.ui')
icon_cmd= os.path.join(wb.icons_path,     'adrFrame.svg')

	
	
class CommandFrame:
    "the Frame command definition"

    def GetResources(self):
        return {'Pixmap': icon_cmd, 
                'MenuText': wb.translate("Ader","Frame"),
                'ToolTip' : wb.translate("Ader","Create a frame")}

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        wb.InTaskPanel(self, ui_file)

    def accept(self):
        height = self.form.sbHeight.value()
        width = self.form.sbWidth.value()
        offset = self.form.sbOffset.value()
        x=self.form.sbx.value()
        if self.form.rb8.isChecked(): 
            nb=8
        elif self.form.rb12.isChecked(): 
            nb=12
        elif self.form.rb16.isChecked(): 
            nb=16
        constrained=self.form.ckConstrained.isChecked()
        sk= adrLibShapes.MakeFrame(height, width, offset, x, fixedFrame=constrained, nbPoints=nb) 

        wb.TaskTerminated(self)
        App.ActiveDocument.recompute()


if App.GuiUp:
    #register the FreeCAD command
    Gui.addCommand('adrFrame', CommandFrame())
