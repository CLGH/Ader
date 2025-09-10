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
''' @package adrBuildNew
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
icon_xpm= os.path.join(wb.icons_path,     'adrBuildNew.xpm')
# translation
def QT_TRANSLATE_NOOP(context, text):
    return text
	
class CommandBuildNew:
    "the BuildNew command definition"

    def GetResources(self):
        return {'Pixmap': icon_xpm, 
		'MenuText': QT_TRANSLATE_NOOP("Ader","Build"),
		'ToolTip' : QT_TRANSLATE_NOOP("Ader","Build from sheet")}

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        doc=App.activeDocument()
        spec = doc.getObject("specifications")
        if not spec:
            raise Exception("Pas de feuille de spécifications.") 

        # create bodies
        #   fuselage
        bf=doc.getObject("Fuselage")
        if bf == None:
          bf=doc.addObject('PartDesign::Body','Fuselage')
          bf.Label = 'Cellule'
       #   wing
        
        bw=doc.getObject("Wing") 
        if bw == None:
          bw=doc.addObject('PartDesign::Body','Wing')
          bw.Label = 'Aile'
        w_x=spec.w_x*1000
        w_z=spec.w_z*1000
        bw.Placement = App.Placement(App.Vector(w_x,0,w_z),App.Rotation(App.Vector(0,0,1),0))
       #   stabs
        bs=doc.getObject("Stabilizer") 
        if bs == None:
          bs=doc.addObject('PartDesign::Body','Stabilizer')
          bs.Label = 'Empennage'
        s_x=spec.s_x*1000
        s_z=spec.s_z*1000
        bs.Placement = App.Placement(App.Vector(s_x,0,s_z),App.Rotation(App.Vector(0,0,1),0))

        # create wing
        profile=spec.ci_profile
        chord=spec.ci*1000
        setting=spec.ci_cal
        name, sk_in=adrFoil.MakeSketchFromDat(profile, chord, setting, skBody=bw)
        profile=spec.ce_profile
        chord=spec.ce*1000
        setting=spec.ce_cal
        y = spec.b * 500    # b/2 in mm
        name, sk_ext_right=adrFoil.MakeSketchFromDat(profile, chord, setting, sk_y=y, skBody=bw)
        name, sk_ext_left=adrFoil.MakeSketchFromDat(profile, chord, setting, sk_y=-y, skBody=bw)
        # loft the wing
        loft=bw.newObject('PartDesign::AdditiveLoft','lWing_r')
        loft.Profile = sk_in
        loft.Sections += [(sk_ext_right, ['Edge1',])]        
        loft=bw.newObject('PartDesign::AdditiveLoft','lWing_l')
        loft.Profile = sk_in
        loft.Sections += [(sk_ext_left, ['Edge1',])]        

        # create stabilizers
        #    vertical
        try:
            profile=spec.vs_profile
        except Exception: 
            profile = None
            pass
        if profile and profile != '': 
            chord=spec.vs_ci*1000
            name, sk_in=adrFoil.MakeSketchFromDat(profile, chord, skBody=bs)
            chord=spec.vs_ce*1000
            y = spec.vs_length * 1000
            name, sk_ext=adrFoil.MakeSketchFromDat(profile, chord, sk_y=y, skBody=bs)
            # loft the vertical stabilizer
            loft=bs.newObject('PartDesign::AdditiveLoft','lStab_v')
            loft.Profile = sk_in
            loft.Sections += [(sk_ext, ['Edge1',])]  
        #    horizontal
        profile=spec.hs_profile
        if profile and profile != '': 
            chord=spec.hs_ci*1000
            dh = spec.hs_dh
            name, sk_in_right=adrFoil.MakeSketchFromDat(profile, chord, dieth=dh, skBody=bs)
            if dh == 0:
                sk_in_left= sk_in_right
            else:
                name, sk_in_left= adrFoil.MakeSketchFromDat(profile, chord, dieth=-dh, skBody=bs)
            chord=spec.hs_ce*1000
            y = spec.hs_length * 1000
            name, sk_ext_right=adrFoil.MakeSketchFromDat(profile, chord, sk_y=y, dieth=dh, skBody=bs)
            name, sk_ext_left=adrFoil.MakeSketchFromDat(profile, chord, sk_y=-y, dieth=-dh, skBody=bs)
            # loft the horizontal stabilizer
            loft=bs.newObject('PartDesign::AdditiveLoft','lStab_h_r')
            loft.Profile = sk_in_right
            loft.Sections += [(sk_ext_right, ['Edge1',])]        
            loft=bs.newObject('PartDesign::AdditiveLoft','lStab_h_l')
            loft.Profile = sk_in_left
            loft.Sections += [(sk_ext_left, ['Edge1',])]        
       
        # display
        App.ActiveDocument.recompute()
        Gui.SendMsgToActiveView("ViewFit")

if App.GuiUp:
    #register the FreeCAD command
    Gui.addCommand('adrBuildNew', CommandBuildNew())
