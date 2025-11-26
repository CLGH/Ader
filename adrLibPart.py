# -*- coding: utf-8 -*-
# *******************************************************************************
# *  Ader workbench                                                             *
# *    For more details see InitGui.py and the LICENCE text file.               *
# *                                                                             *
# *  Module : adrLibPart.py                                                     *
# *    Library to generate splines, part, revolution...                         *
# *                                                                             *
# *  Dependencies :                                                             *
# *                                                                             *
# *  History :                                                                  *
# *    2025-03-05 : initial release                                             *
# *                                                                             *
# *******************************************************************************

__title__ = "Ader Workbench - Part library"
__author__ = "Claude GUTH"

import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher
from math import sin, cos, sqrt, pi, radians
import adrWBCommon as wb
import adrLibPart

# debug messages handling
localDebug = False
# debug msg for this unit

def NewSketch(name='Sketch', plane='XY', body=None):
  if body == None:
    body=Gui.ActiveDocument.ActiveView.getActiveObject('pdbody')
  if body == None:
    raise Exception(wb.translate("No active body")) 
  sk=body.newObject('Sketcher::SketchObject', name)

  if plane ==  'XY':
    attach = body.Origin.OutList[3]
  elif plane ==  'XZ':
    attach = body.Origin.OutList[4]
  elif plane ==  'YZ':
    attach = body.Origin.OutList[5]
  else:
    attach = None
  if attach == None:
    raise Exception(wb.translate("Ader","No plane specified"))
  sk.AttachmentSupport = (attach, [''])
  sk.MapMode = 'FlatFace'

  return sk

def MakeSpline(vects, name='skSpline', plane='XY', perodic=False, body=None, sk=None):
  doc=App.ActiveDocument
  if doc == None:
    raise Exception(wb.translate("No active document")) 
  if sk == None:
    sk=NewSketch(name, plane, body)
  originIx=sk.GeometryCount                # get nb elements
  nb=len(vects)
 
  for vect in vects:
    sk.addGeometry(Part.Point(vect),True)  # add nb elements

  poles = []
  knots = []
  mults = []
  bsps = []
  bsps.append(Part.BSplineCurve())
  bsps[-1].interpolate(vects, PeriodicFlag=perodic)
  bsps[-1].increaseDegree(3)
  poles.extend(bsps[-1].getPoles())
  knots.extend(bsps[-1].getKnots())
  mults.extend(bsps[-1].getMultiplicities())
  sk.addGeometry(Part.BSplineCurve(poles,mults,knots,perodic,3,None,False),False)
  splineIx= originIx + nb
  del(bsps)
  del(poles)
  del(knots)
  del(mults)

  conList = []
  for i in range(0, nb):
    constraint = Sketcher.Constraint('InternalAlignment:Sketcher::BSplineKnotPoint', i+originIx, 1, splineIx, i)
    conList.append(constraint) 
  if vects[0] == vects[-1]:
    conList.append(Sketcher.Constraint('Coincident', originIx+nb-1, 1, 0, 1))
  sk.addConstraint(conList)
  del conList
  sk.exposeInternalGeometry(splineIx)

  return sk

def MakePad(sketch, length, name= 'Pad', reversed=0, midplane=0, offset=0):
  body=Gui.ActiveDocument.ActiveView.getActiveObject('pdbody')
  if body == None:
    raise Exception(wb.translate("No active body")) 
  pad=body.newObject('PartDesign::Pad', name)
  pad.Profile = (sketch, ['',])
  pad.ReferenceAxis = (sketch,['N_Axis'])
  pad.Length = length
  pad.AlongSketchNormal = 1
  pad.Type = 0
  pad.Reversed = reversed
  pad.Midplane = midplane
  pad.Offset = offset
  #pad.TaperAngle = 0.000000
  #pad.UseCustomVector = 0
  #pad.Direction = (0, 0, 1)
  #pad.UpToFace = None

def MakeRevolution(sketch, angle, name= 'Revolution', reversed=0, midplane=0):
  doc=App.ActiveDocument
  body=Gui.ActiveDocument.ActiveView.getActiveObject('pdbody')
  if body == None:
    raise Exception(wb.translate("No active body")) 
  rev=body.newObject('PartDesign::Revolution', name)
  rev.Profile = (sketch, ['',])
  rev.ReferenceAxis = (doc.getObject('X_Axis'), [''])
  rev.Angle = angle            
  rev.Midplane = midplane
  rev.Reversed = reversed
  rev.Type = 0

def MakeIntersectionPlanes(nbPlanes=8, body=None):
  doc=App.ActiveDocument
  if doc == None:
    raise Exception(wb.translate("No active document")) 
  if body==None:
    body=doc.getObject('Fuselage')
    if body == None:
      raise Exception(wb.translate("No active body")) 
  spec = doc.getObject("specifications")
  if not spec:
    raise Exception(wb.translate("No specification sheet"))
  fLength=spec.fus_l*1000 
  fWidth = spec.fus_w*1000 
  fHeight = spec.fus_h*1000 
  
  space = 1        # space from front and back 
  step = (fLength-2*space)/(nbPlanes-1)
  for i in range(int(nbPlanes)):
    skSection=adrLibPart.NewSketch('skSection', 'XY', body)
    geoList = []
    geoList.append(Part.LineSegment(App.Vector(0, 0.51*fWidth, 0),App.Vector(0, -0.51*fWidth, 0)))
    skSection.addGeometry(geoList,False)
    del geoList

    skSection.addConstraint(Sketcher.Constraint('Vertical', 0))

    skSection.AttachmentOffset.Base.x=space+i*step
    skSection.AttachmentOffset.Base.z=-5

    # Extrude
    f = doc.addObject('Part::Extrusion','extSection')
    f.Base = skSection
    f.DirMode = "Normal"
    f.LengthFwd = fHeight+10
    f.Solid = False
    f.Reversed = False
    f.Symmetric = False
  