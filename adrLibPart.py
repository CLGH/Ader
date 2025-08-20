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

def MakeFrame(frameHeight, frameWidth, offset, x=0, fixedFrame= True, nbPoints=8, name='skFrame', plane='YZ', body=None):
  doc=App.ActiveDocument
  if doc == None:
    raise Exception("Pas de document actif") 
  sk = NewSketch(name, plane, body)

  # create limit frame (elements 0..3, top horizontal line first, clock wise)
  constrGeoList = []
  constrGeoList.append(Part.LineSegment(App.Vector(-frameWidth/2, frameHeight-offset, 0),App.Vector(frameWidth/2, frameHeight-offset, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector(frameWidth/2, frameHeight-offset, 0),App.Vector(frameWidth/2, -offset, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector(frameWidth/2, -offset, 0),App.Vector(-frameWidth/2, -offset, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector(-frameWidth/2, -offset, 0),App.Vector(-frameWidth/2, frameHeight-offset, 0)))
  sk.addGeometry(constrGeoList,True)
  del constrGeoList
  topFrameIx=0
  rightFrameIx=1
  bottomFrameIx=2
  leftFrameIx=3   
  
  constraintList = []
  constraintList.append(Sketcher.Constraint('Coincident', 0, 2, 1, 1))
  constraintList.append(Sketcher.Constraint('Coincident', 1, 2, 2, 1))
  constraintList.append(Sketcher.Constraint('Coincident', 2, 2, 3, 1))
  constraintList.append(Sketcher.Constraint('Coincident', 3, 2, 0, 1))
  constraintList.append(Sketcher.Constraint('Horizontal', 0))
  constraintList.append(Sketcher.Constraint('Vertical', 1))
  constraintList.append(Sketcher.Constraint('Vertical', 3))
  
  #constraintList.append(Sketcher.Constraint('Symmetric',0,1,2,2,-2))
  if fixedFrame:
    constraintList.append(Sketcher.Constraint('DistanceX', topFrameIx,1, topFrameIx,2, frameWidth))
    constraintList.append(Sketcher.Constraint('DistanceY', rightFrameIx,2, rightFrameIx,1, frameHeight))
    constraintList.append(Sketcher.Constraint('DistanceY', rightFrameIx,2, -1,1, offset))
  sk.addConstraint(constraintList)
  del constraintList

  # Points 
  vects=[]
  h=frameHeight/2
  w=frameWidth/2
  # points for spline (elements 4..nbPoints+3 from top clockwise)
  for i in range(0, nbPoints):
    angle=i*2*pi/nbPoints
    r=sqrt((w*sin(angle))**2+(h*cos(angle))**2)
    x=r*sin(angle)
    y=r*cos(angle)+h+offset
    vects.append(App.Vector(x,y,0))
    #sk.addGeometry(Part.Point(App.Vector(x,y,0)),True)

  MakeSpline(vects, perodic=True, sk=sk)

  pointTopIx=4                           # first point : top point element index
  pointBottomIx=pointTopIx+nbPoints//2   # bottom point element index
  pointRightIx=pointTopIx+nbPoints//4    # right point element Ix
  pointLeftIx=pointRightIx+nbPoints//2   # left point element Ix
  splineIx=4+nbPoints                    # spline element index
  firstCircleIx=4+nbPoints+1             # first circle element index
  #lastCircleIx=firstCircleIx+nbPoints+1  # last circle element index
  constraintList = []
  # center points on axis
  #constraintList.append(Sketcher.Constraint('PointOnObject', splineIx,1,      -2))  # not pointTopIx ? redondant with top circle symetry
  constraintList.append(Sketcher.Constraint('PointOnObject', pointBottomIx,1, -2))
  # in frame constraints
  constraintList.append(Sketcher.Constraint('PointOnObject', splineIx,1,      topFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointRightIx,1,  rightFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointBottomIx,1, bottomFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointLeftIx,1,   leftFrameIx))

  # Symetry
  constraintList.append(Sketcher.Constraint('Symmetric', firstCircleIx,3, firstCircleIx+1,3, -2)) # top circles symetry
  for i in range(1, nbPoints//2):
    constraintList.append(Sketcher.Constraint('Symmetric', pointTopIx+i,1,    pointTopIx+nbPoints-i,1,    -2)) # points symetry
    #constraintList.append(Sketcher.Constraint('Symmetric', firstCircleIx+i,3, firstCircleIx+nbPoints-i,3, -2)) # circles symetry
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

