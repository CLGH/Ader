# -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    For more details see InitGui.py and the LICENCE text file.               *
#*                                                                             *
#*  Module : adrNacelle.py                                                     *
#*   Generate a nacelle volume.                                                *
#*     - optinal shapes : Hoerner, Lyon, Duhamel, NACA.                        *
#*     - 0° to 360° volume.                                                    *
#*                                                                             *
#*  Dependencies :                                                             *
#*     - adrNacelle.ui : GUI.                                                  *
#*     - adrLibShapes : profils coordinates generation                         *
#*                                                                             *
#*  History :                                                                  *
#*     2021-10-11 : correction Naca                                            *
#*     2021-07-11 : Initial release for v 0.1 tested on FreeCAD 0.19           *
#*                                                                             *
#*******************************************************************************
''' @package adrNacelle
    Produces a nacelle volume.
 
    Optional shapes : Hoerner, Lyon, Duhamel, NACA.
'''
__title__="FreeCAD Ader Nacelle"
__author__ = "Claude GUTH"
__url__ = ""


import FreeCAD as App 
import FreeCADGui as Gui
import Part
import Sketcher
import os
from PySide import QtUiTools
import adrLibShapes
import adrLibPart

debugNacelle= False

# resources ui, icon
import adrWBCommon as wb
ui_file=  os.path.join(wb.resources_path, 'adrNacelle.ui')
icon_cmd= os.path.join(wb.icons_path,     'adrNacelle.svg')
	
	
class CommandNacelle:
    "the Nacelle command definition"

    def GetResources(self):
        return {'Pixmap': icon_cmd, 
		'MenuText': wb.translate("Ader","Nacelle"),
		'ToolTip' : wb.translate("Ader","Create a nacelle")}

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        wb.InTaskPanel(self, ui_file)

    def accept(self):      
        XMaxRel= 0
        length=self.form.sbLength.value()
        diameter=self.form.sbDiameter.value()
        nbPoints = self.form.sbNbPoints.value()
        if self.form.rbLyon.isChecked():
            nacelleType="Lyon"
            coords= adrLibShapes.getLyonCoords(length, diameter, nbPoints)
        elif self.form.rbHoerner.isChecked():
            nacelleType="Hoerner"
            coords= adrLibShapes.getHoernerCoords(length, diameter, nbPoints)
            XMaxRel= self.form.sbXMaxRel.value()
        elif self.form.rbDuhamel.isChecked():
            nacelleType="Duhamel"
            coords= adrLibShapes.getDuhamelCoords(length, diameter, nbPoints)
        else:
            nacelleType="NACA"
            coords= adrLibShapes.getNACACoords(length, diameter, nbPoints)

        vects = []
        for coord in reversed(coords):
            vects.append(coord)
        # complete 
        if not self.form.rbRevolve.isChecked():
            for coord in coords[1:]:
                vects.append(App.Vector(coord.x, -coord.y, 0))
        sk=adrLibPart.MakeSpline(vects, 'sk'+nacelleType)

        # make pad
        if self.form.rbPad.isChecked():
            length=self.form.sbPadLength.value()
            adrLibPart.MakePad(sk, length, 'p'+nacelleType, midplane=1)
            sk.Visibility = False

        # make revolution
        if self.form.rbRevolve.isChecked():
            # close sketch with line
            sk.addGeometry([Part.LineSegment(vects[0],vects[-1])],False)
            constraintList = []
            nbPoints=self.form.sbNbPoints.value()   # ????
            iC=2*nbPoints+4     # should be +2 : 1 point + cercle overhead ?
            # constraintList.append(Sketcher.Constraint('Coincident', iC, 1, nbPoints, 2))
            # constraintList.append(Sketcher.Constraint('Coincident', iC, 2, nbPoints, 1))
            # constraintList.append(Sketcher.Constraint('Coincident', 204, 1, 100, 2))
            # constraintList.append(Sketcher.Constraint('Coincident', 204, 2, 100, 1))
            sk.addConstraint(constraintList)
            del constraintList
            # make revolution
            adrLibPart.MakeRevolution(sk, self.form.sbRevolveAngle.value(), 'r'+nacelleType)
            sk.Visibility = False
          
        wb.TaskTerminated(self)
        App.ActiveDocument.recompute()


if App.GuiUp:
    #register the FreeCAD command
    Gui.addCommand('adrNacelle', CommandNacelle())
