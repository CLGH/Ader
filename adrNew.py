# -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    For more details see InitGui.py and the LICENCE text file.               *
#*                                                                             *
#*  Module : adrNew.py                                                         *
#*   Generate a new FreeCAD document with infos and empty data sheet           *
#*                                                                             *
#*  Dependencies :                                                             *
#*                                                                             *
#*  History :                                                                  *
#*    2023-07-13 : Initial release, tested on FreeCAD 0.20                     *
#*                                                                             *
# ******************************************************************************
""" @package adrSheetMain
    Initiates a sheet to specify main caracteristics of the airplane.
 
"""
__title__ = "FreeCAD Ader main sheet"
__author__ = "Claude GUTH"
__url__ = "https://github.com/   /FreeCAD_Ader"

import FreeCAD as App
import FreeCADGui as Gui
import os
import Spreadsheet
import adrWBCommon as wb
import adrInfos
import adrSheetMain as adrSheet

# debug messages handling
localDebug= False;        # debug msg for this unit       

# resources ui, icon
# ui_file= os.path.join(wb.resources_path, 'adrNew.ui')
icon_xpm = os.path.join(wb.icons_path, "adrNew.xpm")


class CommandNew:
    """Initiate a new airplane"""

    def GetResources(self):
        return {
            "Pixmap": icon_xpm,
            "MenuText": wb.translate("Ader", "Créé un nouvel avion"),
        }

    def IsActive(self):
        return True

    def Activated(self):
        # get infos : CPACS source...
        infos = adrInfos.EditInfos()
        if infos == None:
            return 
        # if success we have new doc : set main sheet
        doc = App.ActiveDocument
        adrSheet.CommandSheetMain.Activated(Gui)
        doc.recompute()


if App.GuiUp:
    # register the FreeCAD command
    Gui.addCommand("adrNew", CommandNew())
