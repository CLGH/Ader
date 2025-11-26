# -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    For more details see InitGui.py and the LICENCE text file.               *
#*                                                                             *
#*  Module : adrBuidNew.py                                                     *
#*    Build structure and components (wing, fuselage, stabilizers) from sheet  *
#*                                                                             *
#*  Dependencies :                                                             *
#*     - adrLibShapes : profils coordinates generation                         *
#*     - adrLibPart : pad generation                                           *
#*                                                                             *
#*  History :                                                                  *
#*     2025-03-06 : Initial release tested on FreeCAD 1.0.0                    *
#*                                                                             *
#*******************************************************************************
''' @package adrBuildWings
    Produces an airplace structure and elements.
 

'''
__title__="FreeCAD Ader build new airplane."
__author__ = "Claude GUTH"
__url__ = ""


import FreeCAD as App 
import FreeCADGui as Gui
import os
import adrFoil

debugAdrNew= False

# resources ui, icon
import adrWBCommon as wb
icon_cmd= os.path.join(wb.icons_path, 'adrBuildFuselage.svg')

	
class CommandBuildFuselage:
    "Build fuselage from frames"

    def GetResources(self):
        return {'Pixmap': icon_cmd, 
		'MenuText': wb.translate("Ader","Build"),
		'ToolTip' : wb.translate("Ader","Build fuselage from frames")}

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        doc=App.activeDocument()

        # get fuselage frames
        frames = wb.GetObjectsByPrefix("skFrame")
        if frames == []:
            raise Exception(wb.translate("Ader","No frames for fuselage")) 
        # sort frames
        frames = sorted(frames, key=lambda s: s.AttachmentOffset.Base.x)

        # get/create fuselage body
        bf=doc.getObject("Fuselage")
        if bf == None:
          bf=doc.addObject('PartDesign::Body','Fuselage')
          bf.Label = wb.translate("Ader", "Fuselage")

        # create loft
        loft = bf.newObject('PartDesign::AdditiveLoft','FuselageLoft')
        loft.Profile = frames[0]
        for frame in frames[1:]:
          loft.Sections += [(frame, [''])]

        # display
        App.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")

if App.GuiUp:
    #register the FreeCAD command
    Gui.addCommand('adrBuildFuselage', CommandBuildFuselage())
