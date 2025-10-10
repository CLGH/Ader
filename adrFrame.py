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
icon_xpm= os.path.join(wb.icons_path,     'adrFrame.svg')
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

        # default values
        self.form.sbHeight.setValue   (wb.GetValue('Frame', 'height', 100))
        self.form.sbWidth.setValue    (wb.GetValue('Frame', 'width', 75))
        self.form.sbOffset.setValue   (wb.GetValue('Frame', 'offset', 0))
        self.form.sbx.setValue        (wb.GetValue('Frame', 'x', 0))
        self.form.rb8.setChecked      (wb.GetValue('Frame', 'Nb8', True))
        self.form.rb12.setChecked     (wb.GetValue('Frame', 'Nb12', False))
        self.form.rb16.setChecked     (wb.GetValue('Frame', 'Nb16', False))
        self.form.ckConstrained.setChecked(wb.GetValue('Frame', 'Constrained', False))

        if not self.form.exec_():
            quit()
        
        # save values
        wb.SaveValue('Frame', 'height', self.form.sbHeight.value())
        wb.SaveValue('Frame', 'width',  self.form.sbWidth.value())
        wb.SaveValue('Frame', 'offset', self.form.sbOffset.value())
        wb.SaveValue('Frame', 'x',      self.form.sbx.value())
        wb.SaveValue('Frame', 'Nb8',    self.form.rb8.isChecked())
        wb.SaveValue('Frame', 'Nb12',   self.form.rb12.isChecked())
        wb.SaveValue('Frame', 'Nb16',   self.form.rb16 .isChecked())
        wb.SaveValue('Frame', 'Constrained', self.form.ckConstrained.isChecked())
        
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

        # display
        App.ActiveDocument.recompute()


if App.GuiUp:
    #register the FreeCAD command
    Gui.addCommand('adrFrame', CommandFrame())
