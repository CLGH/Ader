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

# debug messages handling
localDebug = False
# debug msg for this unit

def NewSketch(name='Sketch', plane='XY', body=None):
  if body == None:
    body=Gui.ActiveDocument.ActiveView.getActiveObject('pdbody')
  if body == None:
    raise Exception("Pas de corps actif") 
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
    raise Exception("Pas de plan spécifié")
  sk.AttachmentSupport = (attach, [''])
  sk.MapMode = 'FlatFace'

  return sk

def MakeSpline(vects, name='skSpline', plane='XY', perodic=False, body=None, sk=None):
  doc=App.ActiveDocument
  if doc == None:
    raise Exception("Pas de document actif") 
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

def MakeFrame(frameHeight, frameWidth, offset, x=0, name='skFrame', plane='YZ', body=None):
  doc=App.ActiveDocument
  if doc == None:
    raise Exception("Pas de document actif") 
  sk = NewSketch(name, plane, body)

  # create limit frame (elements 0..3, left line first)
  constrGeoList = []
  constrGeoList.append(Part.LineSegment(App.Vector(-frameWidth/2, frameHeight-offset, 0),App.Vector(-frameWidth/2, -offset, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector(-frameWidth/2, -offset, 0),App.Vector(frameWidth/2, -offset, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector(frameWidth/2, -offset, 0),App.Vector(frameWidth/2, frameHeight-offset, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector(frameWidth/2, frameHeight-offset, 0),App.Vector(-frameWidth/2, frameHeight-offset, 0)))
  sk.addGeometry(constrGeoList,True)
  del constrGeoList

  constraintList = []
  constraintList.append(Sketcher.Constraint('Coincident', 0, 2, 1, 1))
  constraintList.append(Sketcher.Constraint('Coincident', 1, 2, 2, 1))
  constraintList.append(Sketcher.Constraint('Coincident', 2, 2, 3, 1))
  constraintList.append(Sketcher.Constraint('Coincident', 3, 2, 0, 1))
  constraintList.append(Sketcher.Constraint('Vertical', 0))
  constraintList.append(Sketcher.Constraint('Vertical', 2))
  constraintList.append(Sketcher.Constraint('Horizontal', 1))
  constraintList.append(Sketcher.Constraint('Symmetric',0,1,2,2,-2))
  constraintList.append(Sketcher.Constraint('DistanceX',1,2,1,1,frameWidth))
  constraintList.append(Sketcher.Constraint('DistanceY',0,2,0,1,frameHeight))
  constraintList.append(Sketcher.Constraint('DistanceY',0,2,-1,1,offset))
  sk.addConstraint(constraintList)
  del constraintList

  # Points 
  nbPoints=8   #12
  vects=[]
  h=frameHeight/2
  w=frameWidth/2
  # points for spline (elements 4..nbPoints+3)
  for i in range(0, nbPoints):
    angle=i*2*pi/nbPoints
    r=sqrt((w*sin(angle))**2+(h*cos(angle))**2)
    x=r*sin(angle)
    y=r*cos(angle)+h+offset
    vects.append(App.Vector(x,y,0))
    #sk.addGeometry(Part.Point(App.Vector(x,y,0)),True)

  MakeSpline(vects, perodic=True, sk=sk)

  pointTopIx=4                          # top point element index
  pointBottomIx=pointTopIx+nbPoints/2   # bottom point element index
  pointRightIx=pointTopIx+nbPoints/4    # right point element Ix
  pointLeftIx=pointRightIx+nbPoints/2   # left point element Ix
  constraintList = []
  # center points on axis
  constraintList.append(Sketcher.Constraint('PointOnObject', int(pointTopIx), 1, -2))
  constraintList.append(Sketcher.Constraint('PointOnObject', int(pointBottomIx), 1, -2))
  # in frame constraints
  constraintList.append(Sketcher.Constraint('Tangent',int(pointTopIx),1,3))
  constraintList.append(Sketcher.Constraint('Tangent',int(pointBottomIx),1,1))
  constraintList.append(Sketcher.Constraint('Tangent',int(pointLeftIx),1,2))
  constraintList.append(Sketcher.Constraint('Tangent',int(pointRightIx),1,0))
  # points symetry
  #for i in range(pointTopIx+1, pointBottomIx):
    #constraintList.append(Sketcher.Constraint('Symmetric', i,1, 16-i,1, -2)) # points symetry
  constraintList.append(Sketcher.Constraint('Symmetric', 5,1, 11,1, -2)) # points symetry
  constraintList.append(Sketcher.Constraint('Symmetric', 6,1, 10,1,-2))
  constraintList.append(Sketcher.Constraint('Symmetric', 7,1, 9,1,-2))
  constraintList.append(Sketcher.Constraint('Symmetric', 21,3, 15,3, -2)) # circles symetry
  constraintList.append(Sketcher.Constraint('Symmetric', 20,3, 16,3, -2))
  constraintList.append(Sketcher.Constraint('Symmetric', 19,3, 17,3,-2))  
  sk.addConstraint(constraintList)
  del constraintList

  return sk

def MakePad(sketch, length, name= 'Pad', reversed=0, midplane=0, offset=0):
  body=Gui.ActiveDocument.ActiveView.getActiveObject('pdbody')
  if body == None:
    raise Exception("Pas de corps actif") 
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
    raise Exception("Pas de corps actif") 
  rev=body.newObject('PartDesign::Revolution', name)
  rev.Profile = (sketch, ['',])
  rev.ReferenceAxis = (doc.getObject('X_Axis'), [''])
  rev.Angle = angle            
  rev.Midplane = midplane
  rev.Reversed = reversed
  rev.Type = 0

