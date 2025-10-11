# -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    For more details see InitGui.py and the LICENCE text file.               *
#*                                                                             *
#*  Module : adrNew.py                                                         *
#*   Generate a new FreeCAD document with infos and empty data spec           *
#*                                                                             *
#*  Dependencies :                                                             *
#*                                                                             *
#*  History :                                                                  *
#*    2023-07-13 : Initial release, tested on FreeCAD 0.20                     *
#*                                                                             *
# ******************************************************************************
""" @package adrspecMain
    Initiates a spec to specify main caracteristics of the airplane.
 
"""
__title__ = "FreeCAD Ader main spec"
__author__ = "Claude GUTH"
__url__ = "https://github.com/   /FreeCAD_Ader"

import FreeCAD as App
import FreeCADGui as Gui
import os
import Spreadsheet
import adrWBCommon as wb
import adrInfos
import adrSheetMain as adrspec
import adrLibShapes

# debug messages handling
localDebug= False;        # debug msg for this unit       

# resources ui, icon
# ui_file= os.path.join(wb.resources_path, 'adrNew.ui')
icon_cmd = os.path.join(wb.icons_path, "adrNew.svg")


class CommandNew:
    """Initiate a new airplane"""

    def GetResources(self):
        return {
            "Pixmap": icon_cmd,
            "MenuText": wb.translate("Ader", "Create a new airplane"),
        }

    def IsActive(self):
        return True

    def Activated(self):
        # get infos : CPACS source...
        infos, l, w, h = adrInfos.EditInfos()
        if infos == None:
            return 
        
        # check values
        if l <= 0 or w <= 0 or h <= 0:
            raise Exception( "Dimensions invalides")
        
        # if success we have new doc : set main spec
        doc = App.ActiveDocument
        adrspec.CommandSheetMain.Activated(Gui)
        spec = doc.getObject("specifications")
        spec.fus_l = float(l) / 1000  # mm to m temp ?
        spec.fus_w = float(w) / 1000
        spec.fus_h = float(h) / 1000   
        
        # set bodies
        bf=doc.addObject('PartDesign::Body','Fuselage')
        bf.Label = wb.translate("Ader", "Fuselage")
        bw=doc.addObject('PartDesign::Body','Wing')
        bw.Label = wb.translate("Ader", "Wing")
        bs=doc.addObject('PartDesign::Body','Stabilizer')
        bs.Label = wb.translate("Ader", "Stabilizer")

        # set top/face views
        adrLibShapes.MakeTopView(l, w, body=bf)
        adrLibShapes.MakeFaceView(l, h, body=bf)
        
        doc.recompute()
        Gui.SendMsgToActiveView("ViewFit")


if App.GuiUp:
    # register the FreeCAD command
    Gui.addCommand("adrNew", CommandNew())
