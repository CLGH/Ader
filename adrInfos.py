# -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    For more details see InitGui.py and the LICENCE text file.               *
#*                                                                             *
#*  Module : adrInfos.py                                                       *
#*    Link to CPACS file and handles basic infos from CPACS header             *
#*                                                                             *
#*  Dependencies :                                                             *
#*                                                                             *
#*  History :                                                                  *
#*    2023-07-13 : Initial release, tested on FreeCAD 0.20                     *
#*                                                                             *
# ******************************************************************************
""" @package adrInfos
    Link to CPACS file and handles basic infos from CPACS header.
 
"""
__title__ = "FreeCAD Ader infos"
__author__ = "Claude GUTH"
__url__ = "https://github.com/   /FreeCAD_Ader"

import FreeCAD as App
import FreeCADGui as Gui
import os
import adrWBCommon as wb

from PySide import QtCore
from PySide import QtGui
from PySide import QtUiTools

# debug messages handling
localDebug= False;        # debug msg for this unit        

# resources ui, icon
ui_file = os.path.join(wb.resources_path, "adrInfos.ui")
icon_cmd = os.path.join(wb.icons_path, "adrInfos.xpm")


def EditInfos(infos= None):
    # fill and show the form
    loader = QtUiTools.QUiLoader()
    Gui.form = loader.load(ui_file)
    if infos:
        Gui.form.CPACS_FileName.setText(infos.cpacs_filename)
        Gui.form.name.setText(infos.name)
        Gui.form.author.setText(infos.author)
    else:
        from datetime import datetime
        Gui.form.dateCreated.setDateTime(QtCore.QDateTime.currentDateTime())  
    valid = Gui.form.exec_()
    if not valid:
        return None

    # create doc and infos if required
    if not infos:
        doc = App.newDocument(Gui.form.name.text())
        doc.FileName = doc.Name + ".FCStd"
        App.setActiveDocument(doc.Name)
        infos = doc.addObject("Part::FeaturePython", "infos")
        infos.Label= "Infos"
        Infos(infos)
        ViewProviderInfos(infos.ViewObject)   
    
    # save values
    infos.name = Gui.form.name.text()
    infos.author = Gui.form.author.text()
    infos.cpacs_filename = Gui.form.CPACS_FileName.text()
    fuselageLength = Gui.form.sbLength.value()
    fuselageWidth = Gui.form.sbWidth.value()
    fuselageHeight = Gui.form.sbHeight.value()
 
     
    return infos, fuselageLength, fuselageWidth, fuselageHeight


class Infos:
    """Infos class"""
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty(
            "App::PropertyString",
            "cpacs_filename",
            "Infos",
            wb.translate("Ader", "CPACS File"),
        )
        obj.addProperty(
            "App::PropertyString",
            "author",
            "Infos",
            wb.translate("Ader", "Author"),
        )
        obj.addProperty(
            "App::PropertyString",
            "name",
            "Infos",
            wb.translate("Ader", "Project name"),
        )

    def onChanged(self, fp, prop):
        """Do something when a property has changed"""
        wb.debugMsg("Infos: Change property  " + str(prop) + "\n", localDebug)

    def execute(self, fp):
        #   Do something when doing a recomputation, this method is mandatory
        wb.debugMsg("Infos : execute process l= " + str(fp.cpacs_filename) + "\n", localDebug)


class InfosTaskPanel:
    """Infos TaskPanel mahagement """
    def __init__(self, vobj):
        wb.debugMsg("init )", localDebug)
        self.obj = vobj
        self.update(vobj)

    def isAllowedAlterSelection(self):
        return True

    def isAllowedAlterView(self):
        return True

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok)

    def update(self, vobj):
        "fills the dialog with infos properties"
        wb.debugMsg('update', localDebug)
        return

    def accept(self):
        """Update Infos"""
        wb.debugMsg("accept", localDebug)
        App.ActiveDocument.recompute()
        Gui.ActiveDocument.resetEdit()
        return True

    def retranslateUi(self, TaskPanel):
        TaskPanel.lCPACS.setText(wb.translate("Ader", "CPACS file :"))
        wb.debugMsg("retranslate", localDebug)


class ViewProviderInfos:
    def __init__(self, obj):
        """Set this object to the proxy object of the actual view provider"""
        obj.Proxy = self

    def getDefaultDisplayMode(self):
        """Return the name of the default display mode. It must be defined in getDisplayModes."""
        return "Flat Lines"

    def getIcon(self):
        """Return the icon in XPM format which will appear in the tree view. This method is\
            optional and if not defined a default icon is shown."""
        return icon_cmd

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
        EditInfos(App.ActiveDocument.getObject('Infos'))
        return True

    def doubleClicked(self, vobj):
        EditInfos(App.ActiveDocument.getObject('Infos'))
        return True


class CommandInfos:
    """CPACS infos"""

    def GetResources(self):
        return {"Pixmap": icon_cmd, "MenuText": wb.translate("Ader", "Infos")}

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        EditInfos(App.ActiveDocument.getObject('infos'))
        # save to CPACS ?
        doc = App.ActiveDocument
        doc.recompute()


if App.GuiUp:
    # register the FreeCAD command
    Gui.addCommand("adrInfos", CommandInfos())
