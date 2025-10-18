 # -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    FreeCAD workbench to design airplane and interact with CPACS files       *
#*                                                                             *
#*  Created by Claude GUTH  Copyright (c) 2023                                 *
#*  Contributors : see source files                                            *
#*  For FreeCAD Versions = 1.0.0 or >                                          *
#*                                                                             *
#*  History :                                                                  *
#*    v 0.5 : 2025-xx-xx : FreeCAD version 1.0.0 add sketch, frame...          *
#*    v 0.1 : 2023-07-11 : Initial release for developpers only                *
#*                                                                             *
#* This program is free software. You can redistribute it and/or modify        *
#* it under the terms of the MIT License.                                      *
#* For more details see the LICENCE text file                                  *
#* Note : some portions of code may be under alternate licences.               *
#*        See source files.                                                    *
#* This program is distributed in the hope that it will be useful,             *
#* but WITHOUT ANY WARRANTY; without even the implied warranty of              *
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                        *
# ******************************************************************************

import FreeCAD as App
import FreeCADGui as Gui
import os
import adrWBCommon as wb

# resources icon, translated text
global adrWB_Icon, adrWB_Tip
adrWB_Icon = os.path.join(wb.icons_path, "ader_wb.svg")
adrWB_Tip = wb.translate("Ader", "Tools to design an airplane with CPACS")

# Qt tanslation handling
Gui.addLanguagePath(os.path.join(wb.base_path, "translations"))
Gui.updateLocale()


class AderWorkbench(Workbench):
    def __init__(self):
        self.__class__.Icon = adrWB_Icon
        self.__class__.MenuText = "Ader"
        self.__class__.ToolTip = adrWB_Tip

    def Initialize(self):
        # "This function is executed when FreeCAD starts"
        # Ader WB commands
        import adrNew       # Create a new plane : infos, global parameters
        import adrBuildWings  # build wing and stab from parameters sheet
        import adrSections
        import adrFrames    
        import adrFoil
        import adrNacelle
        import adrFrame
        import adrExport    # Export to CPACS xml file
        self.comdList = [
            "adrNew",
            "adrBuildWings",

            "adrSections",
            "adrFrames",

            "adrFoil",
            "adrNacelle",
            "adrFrame",

            "adrExport",
        ]

        # creates a new toolbar with your commands
        self.appendToolbar("Ader", self.comdList)
        # creates a new menu
        self.appendMenu("Ader", self.comdList)

    def Activated(self):
        # This function is executed when the workbench is activated
        return

    def Deactivated(self):
        # This function is executed when the workbench is deactivated
        return

    def ContextMenu(self, recipient):
        # This is executed whenever the user right-clicks on screen
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu(self.comdList)  # add commands to the context menu

    def GetClassName(self):
        # this function is mandatory if this is a full python workbench
        return "Gui::PythonWorkbench"


Gui.addWorkbench(AderWorkbench())
