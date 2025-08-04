# -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    For more details see InitGui.py and the LICENCE text file.               *
#*                                                                             *
#*  Module : adrFoil.py                                                        *
#*   Generate a foil skech or wing section                                     *
#*     - get foil data from dat file                                           *
#*     - optional pad to generate wing section                                 *
#*                                                                             *
#*  Dependencies :                                                             *
#*     - adrFoil.ui : GUI.                                                     *
#*     - adrLibShapes : profils coordinates generation                         *
#*     - adrLibPart : pad generation                                           *
#*                                                                             *
#*  History :                                                                  *
#*     2025-03-04 : Initial release tested on FreeCAD 1.0.0                    *
#*                                                                             *
#*******************************************************************************
''' @package adrFoil
    Produces a foil sketch + wing section.
 

'''
__title__="FreeCAD Ader Foil."
__author__ = "Claude GUTH"
__url__ = ""


import FreeCAD as App 
import FreeCADGui as Gui
import os
from math import pi, cos, sin, atan, radians
from pathlib import Path
from PySide import QtUiTools
import adrLibShapes
import adrLibPart

debugFoil= False

# resources ui, icon
import adrWBCommon as wb
ui_file=  os.path.join(wb.resources_path, 'adrFoil.ui')
icon_xpm= os.path.join(wb.icons_path,     'adrFoil.xpm')
# translation
def QT_TRANSLATE_NOOP(context, text):
    return text
	
	
def MakeSketchFromDat(datFile, length, setting=0, sk_y=0, dieth=0, skBody=None):
    filename=os.path.join(wb.dat_path, datFile)
    if Path(filename).suffix == '':
        filename += '.dat'
    name, coords= adrLibShapes.FoilCoordsFromDat(filename, length, setting)
    name.replace(" ", "_")
    # make spline
    vects = []
    for coord in coords:
        vects.append(App.Vector(coord))
    if coords[0] != coords[-1]:   # close the wire
        vects.append(App.Vector(coords[0]))
    sk=adrLibPart.MakeSpline(vects, 'sk'+name, plane='XZ', body=skBody)
    # set y position
    y=sk_y*sin(radians(dieth))
    z=sk_y*cos(radians(dieth))
    sk.AttachmentOffset = App.Placement(App.Vector(0,y,z), App.Rotation(App.Vector(1,0,0), -dieth))  
    return name, sk

class CommandFoil:
    "the Foil command definition"

    def GetResources(self):
        return {'Pixmap': icon_xpm, 
		'MenuText': QT_TRANSLATE_NOOP("Ader","Foil"),
		'ToolTip' : QT_TRANSLATE_NOOP("Ader","Create a foil")}

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        loader=QtUiTools.QUiLoader()
        self.form=loader.load(ui_file)
        if not self.form.exec_():
            quit()
        
        datFile=self.form.eDat.text()
        length = self.form.sbChord.value()
        setting = self.form.sbSetting.value()
        y=self.form.sby.value()
        name, sk= MakeSketchFromDat(datFile, length, setting, y) 

        # make pad
        if self.form.rbPad.isChecked():
            length=self.form.sbPadLength.value()
            adrLibPart.MakePad(sk, length, 'p'+name, midplane=1)
    
        # display
        App.ActiveDocument.recompute()


if App.GuiUp:
    #register the FreeCAD command
    Gui.addCommand('adrFoil', CommandFoil())
