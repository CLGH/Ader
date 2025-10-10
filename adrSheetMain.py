# -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    For more details see InitGui.py and the LICENCE text file.               *
#*                                                                             *
#*  Module : adrSheetMain.py                                                   *
#*   Generate a spreadsheet to enter global airplane datas.                    *
#*                                                                             *
#*  Dependencies :                                                             *
#*                                                                             *
#*  History :                                                                  *
#*    2023-07-12 : Initial release, tested on FreeCAD 0.20                     *
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

# debug messages handling
localDebug= False;        # debug msg for this unit     

# resources ui, icon
# ui_file= os.path.join(wb.resources_path, 'adrSheetMain.ui')
icon_xpm = os.path.join(wb.icons_path, "adrSheetMain.svg")

# Main sheet parameters
fuselageParams = [
    {"alias": "fus_l",      "unite": "m", "value": "0.001", "description": "Longueur totale du fuselage"},
    {"alias": "fus_w",      "unite": "m", "value": "0.001", "description": "Largeur totale du fuselage"},
    {"alias": "fus_h",      "unite": "m", "value": "0.001", "description": "Hauteur totale du fuselage"},
]

wingParams = [
    {"alias": "w_x",        "unite": "m", "value": "0.001", "description": "Position x"},
    {"alias": "w_z",        "unite": "m", "value": "0.001", "description": "Position z"},
    {"alias": "b",          "unite": "m", "value": "0.001",  "description": "Envergure"},
    {"alias": "dieth",      "unite": "m", "value": "0.001",  "description": "Dièdre"},
    {"alias": "fleche",     "unite": "°", "value": "0.001",  "description": "Flèche"},
    {"alias": "ci",         "unite": "m", "value": "",  "description": "Corde interne"},
    {"alias": "ci_profile", "unite": "",  "value": "",  "description": "Profil interne (fichier *.dat)"},
    {"alias": "ci_cal",     "unite": "°", "value": "",  "description": "Calage interne"},
    {"alias": "ce",         "unite": "m", "value": "",  "description": "Corde à l'extrémité"},
    {"alias": "ce_profile", "unite": "",  "value": "",  "description": "Profil à l'extrémité (fichier *.dat)"},
    {"alias": "ce_cal",     "unite": "°", "value": "",  "description": "Calage à l'extrémité"},
]
stabParams = [
    {"alias": "s_x",        "unite": "m", "value": "0", "description": "Position x"},
    {"alias": "s_z",        "unite": "m", "value": "0", "description": "Position z"},
    {"alias": "vs_profile", "unite": "",  "value": "",  "description": "Profil dérive (fichier *.dat)"},
    {"alias": "vs_length",  "unite": "m", "value": "",  "description": "Envergure dérive"},
    {"alias": "vs_ci",      "unite": "m", "value": "",  "description": "Corde interne"},
    {"alias": "vs_ce",      "unite": "m", "value": "",  "description": "Corde à l'extrémité"},
    {"alias": "hs_profile", "unite": "",  "value": "",  "description": "Profil profondeur (fichier *.dat)"},
    {"alias": "hs_length",  "unite": "m", "value": "",  "description": "Envergure profondeur"},
    {"alias": "hs_ci",      "unite": "m", "value": "",  "description": "Corde interne"},
    {"alias": "hs_ce",      "unite": "m", "value": "",  "description": "Corde à l'extrémité"},
    {"alias": "hs_dh",      "unite": "°", "value": "",  "description": "Dièdre profondeur"},
]


class SheetMain:
    def __init__(self, ms):
        def ParamInSheet(p):
            textAlias = p["alias"]
            if p["unite"] != "":
                textAlias+= " [" + p["unite"] + "]"         
            ms.set("A" + str(cellNo), textAlias)
            ms.set("B" + str(cellNo), p["value"])
            ms.setAlias("B" + str(cellNo), p["alias"])
            ms.set("C" + str(cellNo), p["description"])
            
        cellNo = 1
        # fuselage params start here ++++++++++++++++++++++++++++++++++++++++++++
        ms.set("A" + str(cellNo), "Fuselage")
        cellNo += 1
        for p in fuselageParams:
            ParamInSheet(p)
            cellNo += 1

        # wing params start here ++++++++++++++++++++++++++++++++++++++++++++++++
        ms.set("A" + str(cellNo), "Wing")
        cellNo += 1
        for p in wingParams:
            ParamInSheet(p)
            cellNo += 1

        # stab params start here ++++++++++++++++++++++++++++++++++++++++++++++++
        ms.set("A" + str(cellNo), "Stabilizers")
        cellNo += 1
        for p in stabParams:
            ParamInSheet(p)
            cellNo += 1

    def onChanged(self):
        """Do something when a property has changed"""
        wb.debugMsg("Feuille modifiée " + "\n", localDebug)

    def execute(self):
        #   Do something when doing a recomputation, this method is mandatory
        wb.debugMsg("Feuille principale créée \n", localDebug)


class ViewProviderSheetMain:
    def __init__(self, obj):
        # obj.addProperty("App::PropertyColor","Color","Wing","Color of the wing").Color=(1.0,0.0,0.0)
        return None

    def getDefaultDisplayMode(self):
        """Return the name of the default display mode. It must be defined in getDisplayModes."""
        return "Flat Lines"

    def getIcon(self):
        """Return the icon in XPM format which will appear in the tree view. This method is\
            optional and if not defined a default icon is shown."""
        return icon_xpm

    def __getstate__(self):
        """When saving the document this object gets stored using Python's json module.\
            Since we have some un-serializable parts here -- the Coin stuff -- we must define this method\
            to return a tuple of all serializable objects or None."""
        return None

    def __setstate__(self, state):
        """When restoring the serialized object from document we have the chance to set some internals here.\
            Since no data were serialized nothing needs to be done here."""
        return None

    def setEdit(self, vobj, mode):
        return True

    def doubleClicked(self, vobj):
        return True


class CommandSheetMain:
    "the SheetMain command definition"

    def GetResources(self):
        return {
            "Pixmap": icon_xpm,
            "MenuText": wb.translate("Ader", "Feuille de spécifications"),
        }

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        doc = App.activeDocument()
        sheet = doc.getObject("specifications")
        if not sheet:
            sheet = doc.addObject("Spreadsheet::Sheet", "specifications")
            sheet.Label = wb.translate("Ader", "Spécifications")
            SheetMain(sheet)
            ViewProviderSheetMain(sheet.ViewObject)
            doc.recompute()
        else:
            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(doc.Name,"specifications")
        


if App.GuiUp:
    # register the FreeCAD command
    Gui.addCommand("adrSheetMain", CommandSheetMain())
