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
#*     - adrLibPart : sketch generation                                        *
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
import adrLibPart

debugFrame= False

# resources ui, icon
import adrWBCommon as wb
ui_file=  os.path.join(wb.resources_path, 'adrFrame.ui')
icon_xpm= os.path.join(wb.icons_path,     'adrFrame.xpm')
# translation
def QT_TRANSLATE_NOOP(context, text):
    return text
	
	
class CommandFrame:
    "the Frame command definition"

    def GetResources(self):
        return {'Pixmap': icon_xpm, 
                'MenuText': QT_TRANSLATE_NOOP("Ader","Frame"),
                'ToolTip' : QT_TRANSLATE_NOOP("Ader","Create a frame")}

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        loader=QtUiTools.QUiLoader()
        self.form=loader.load(ui_file)
        if not self.form.exec_():
            quit()
        
        height = self.form.sbHeight.value()
        width = self.form.sbWidth.value()
        offset = self.form.sbOffset.value()
        x=self.form.sbx.value()
        sk= adrLibPart.MakeFrame(height, width, offset, x) 

        # display
        App.ActiveDocument.recompute()


if App.GuiUp:
    #register the FreeCAD command
    Gui.addCommand('adrFrame', CommandFrame())
