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
  if body==None:
    body=doc.getObject('Body')#temp
    if body == None:
      raise Exception("Pas de corps actif") 
  sk = NewSketch(name, plane, body)

  # Points 
  vects=[]
  h=frameHeight/2
  w=frameWidth/2
  # points for spline (elements 0..nbPoints-1 from top clockwise)
  for i in range(0, nbPoints):
    angle=i*2*pi/nbPoints
    r=sqrt((w*sin(angle))**2+(h*cos(angle))**2)
    x=r*sin(angle)
    y=r*cos(angle)+h+offset
    vects.append(App.Vector(x,y,0))
    #sk.addGeometry(Part.Point(App.Vector(x,y,0)),True)   # for test

  MakeSpline(vects, perodic=True, sk=sk)

  pointTopIx=0                           # first point : top point element index
  pointBottomIx=pointTopIx+nbPoints//2   # bottom point element index
  pointRightIx=pointTopIx+nbPoints//4    # right point element Ix
  pointLeftIx=pointRightIx+nbPoints//2   # left point element Ix
  splineIx=nbPoints                      # spline element index
  firstCircleIx=nbPoints+1               # first circle element index
  #lastCircleIx=firstCircleIx+nbPoints+1  # last circle element index
  constraintList = []
  # center points on axis
  #constraintList.append(Sketcher.Constraint('PointOnObject', splineIx,1,      -2))  # not pointTopIx, redondant with top circle symetry
  constraintList.append(Sketcher.Constraint('PointOnObject', pointBottomIx,1, -2))
 
  # Symetry
  constraintList.append(Sketcher.Constraint('Symmetric', firstCircleIx,3, firstCircleIx+1,3, -2)) # top circles symetry
  for i in range(1, nbPoints//2):
    constraintList.append(Sketcher.Constraint('Symmetric', pointTopIx+i,1,    pointTopIx+nbPoints-i,1,    -2)) # points symetry
    #constraintList.append(Sketcher.Constraint('Symmetric', firstCircleIx+i,3, firstCircleIx+nbPoints-i,3, -2)) # circles symetry
  sk.addConstraint(constraintList)
  del constraintList

  # create limit frame (elements sk.GeometryCount..+3, top horizontal line first, clock wise)
  topFrameIx=sk.GeometryCount 
  rightFrameIx=topFrameIx+1
  bottomFrameIx=topFrameIx+2   
  leftFrameIx=topFrameIx+3
  constrGeoList = []
  constrGeoList.append(Part.LineSegment(App.Vector(-frameWidth/2, frameHeight-offset, 0),App.Vector(frameWidth/2,  frameHeight-offset, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector( frameWidth/2, frameHeight-offset, 0),App.Vector(frameWidth/2,  -offset,            0)))
  constrGeoList.append(Part.LineSegment(App.Vector( frameWidth/2, -offset,            0),App.Vector(-frameWidth/2, -offset,            0)))
  constrGeoList.append(Part.LineSegment(App.Vector(-frameWidth/2, -offset,            0),App.Vector(-frameWidth/2, frameHeight-offset, 0)))
  sk.addGeometry(constrGeoList,True)
  del constrGeoList
  
  constraintList = []
  constraintList.append(Sketcher.Constraint('Coincident', topFrameIx,2,    rightFrameIx,1))
  constraintList.append(Sketcher.Constraint('Coincident', rightFrameIx,2,  bottomFrameIx,1))
  constraintList.append(Sketcher.Constraint('Coincident', bottomFrameIx,2, leftFrameIx,1))
  constraintList.append(Sketcher.Constraint('Coincident', leftFrameIx,2,   topFrameIx,1))
  constraintList.append(Sketcher.Constraint('Horizontal', topFrameIx))
  constraintList.append(Sketcher.Constraint('Vertical',   rightFrameIx))
  constraintList.append(Sketcher.Constraint('Horizontal', bottomFrameIx))
  constraintList.append(Sketcher.Constraint('Vertical',   leftFrameIx))
  
  if fixedFrame:
    constraintList.append(Sketcher.Constraint('DistanceX', topFrameIx,1, topFrameIx,2, frameWidth))
    constraintList.append(Sketcher.Constraint('DistanceY', rightFrameIx,2, rightFrameIx,1, frameHeight))
    constraintList.append(Sketcher.Constraint('DistanceY', rightFrameIx,2, -1,1, offset))

  # in frame constraints
  constraintList.append(Sketcher.Constraint('PointOnObject', splineIx,1,      topFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointRightIx,1,  rightFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointBottomIx,1, bottomFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointLeftIx,1,   leftFrameIx))

  sk.addConstraint(constraintList)
  del constraintList

  return sk


def MakeTopView(aircraftLength, aircraftWidth, xRelMax= 0.33, fixedFrame= True, name='skTopView', plane='XY', body=None):
  doc=App.ActiveDocument
  if doc == None:
    raise Exception("Pas de document actif") 
  if body==None:
    body=doc.getObject('Fuselage')
    if body == None:
      raise Exception("Pas de corps actif") 
	
  sk = NewSketch(name, plane, body)

  #l_2=aircraftLength/2
  w_2=aircraftWidth/2
  
  # Points 
  vects=[]
  #   Points from tail (elements 0..NbPointsTail-1)
  NbPointsTail=4
  step=(1-xRelMax)*aircraftLength/(NbPointsTail-1)
  for i in range(0, NbPointsTail):
    x=aircraftLength -i*step
    y=i*aircraftWidth/6
    vects.append(App.Vector(x,y,0))
  xMax=x
  #   Points to front (elements NbPointsTai1..NbPointsTail+NbPointsFront-1)
  NbPointsFront=5
  step=xRelMax*aircraftLength/NbPointsFront
  for i in range(1, NbPointsFront+1):
    x=xMax-i*step
    y= w_2 * sqrt(2*x*xMax - x*x) / xMax
    vects.append(App.Vector(x,y,0))
  #   symetric points
  for vect in vects[-2::-1]:
    vects.append(App.Vector(vect.x,-vect.y,0))

  # test
  #for vect in vects:
  #  sk.addGeometry(Part.Point(vect),False)

  MakeSpline(vects, perodic=False, sk=sk)

  # Constraints on spline
  pointTailFirstIx=0                                  # first point : start at tail
  pointTailLastIx=2*(NbPointsTail+NbPointsFront-1)    # last point : end at tail
  pointFrontIx=NbPointsTail+NbPointsFront-1           # front point element index
  splineIx=pointTailLastIx+1
  pointTopIx=NbPointsTail-1                           # top point at width/2 index
  pointBottompIx=pointTopIx + 2*NbPointsFront         # bottom point at -width/2 index
  constraintList = []
  #   front point on origin
  constraintList.append(Sketcher.Constraint('Coincident', pointFrontIx,1, -1,1))  
  #   first and last points coïncident on axis
  #constraintList.append(Sketcher.Constraint('Coincident',   pointTailFirstIx,1, pointTailLastIx,1))  # redondant ?
  constraintList.append(Sketcher.Constraint('PointOnObject', splineIx,1,      -1))  
  #   symetric points
  for i in range(1, NbPointsTail+NbPointsFront-1):
    constraintList.append(Sketcher.Constraint('Symmetric', i,1,    pointTailLastIx-i,1,    -1)) # points symetry 
  # symetric circle ()  
  constraintList.append(Sketcher.Constraint('Symmetric', splineIx+2,3, splineIx+2*(NbPointsTail+NbPointsFront),3, -1))

  sk.addConstraint(constraintList)
  del constraintList

  # create limit frame (elements sk.GeometryCount ..+3, top horizontal line first, clock wise)
  topFrameIx=sk.GeometryCount 
  rearFrameIx=topFrameIx+1
  bottomFrameIx=topFrameIx+2   
  frontFrameIx=topFrameIx+3
  constrGeoList = []
  constrGeoList.append(Part.LineSegment(App.Vector(0,               w_2, 0), App.Vector(aircraftLength,  w_2, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector(aircraftLength,  w_2, 0), App.Vector(aircraftLength, -w_2, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector(aircraftLength, -w_2, 0), App.Vector(0,              -w_2, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector(0,              -w_2, 0), App.Vector(0,               w_2, 0)))
  sk.addGeometry(constrGeoList,True)
  del constrGeoList
  
  constraintList = []
  constraintList.append(Sketcher.Constraint('Coincident', topFrameIx,2,    rearFrameIx,1))
  constraintList.append(Sketcher.Constraint('Coincident', rearFrameIx,2,   bottomFrameIx,1))
  constraintList.append(Sketcher.Constraint('Coincident', bottomFrameIx,2, frontFrameIx,1))
  constraintList.append(Sketcher.Constraint('Coincident', frontFrameIx,2,  topFrameIx,1))
  constraintList.append(Sketcher.Constraint('Horizontal', topFrameIx))
  constraintList.append(Sketcher.Constraint('Vertical',   rearFrameIx))
  constraintList.append(Sketcher.Constraint('Horizontal', bottomFrameIx))
  constraintList.append(Sketcher.Constraint('Vertical',   frontFrameIx))

  if fixedFrame:
    constraintList.append(Sketcher.Constraint('DistanceY', frontFrameIx,1, frontFrameIx,2, aircraftWidth))
    constraintList.append(Sketcher.Constraint('DistanceX', frontFrameIx,2, topFrameIx,2,   aircraftLength))
  
  # sketch within frame
  constraintList.append(Sketcher.Constraint('PointOnObject', pointFrontIx,1,     frontFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointTopIx,1,       topFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointBottompIx,1,   bottomFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', splineIx,1,         rearFrameIx))

  sk.addConstraint(constraintList)
  del constraintList
  
  return sk
  
def MakeFaceView(aircraftLength, aircraftHeight, xRelMax= 0.33, fixedFrame= True, name='skFaceView', plane='XZ', body=None):
  doc=App.ActiveDocument
  if doc == None:
    raise Exception("Pas de document actif") 
  if body==None:
    body=doc.getObject('Fuselage')
    if body == None:
      raise Exception("Pas de corps actif") 
	
  sk = NewSketch(name, plane, body)

  #l_2=aircraftLength/2
  h_2=aircraftHeight/2
  
  # Points 
  vects=[]
  #   Points from tail (elements 0..NbPointsTail-1)
  NbPointsTail=4
  step=(1-xRelMax)*aircraftLength/(NbPointsTail-1)
  for i in range(0, NbPointsTail):
    x=aircraftLength -i*step
    y=h_2 * (1+i/3)
    vects.append(App.Vector(x,y,0))
  xMax=x
  #   Points to front (elements NbPointsTai1..NbPointsTail+NbPointsFront-1)
  NbPointsFront=5
  step=xRelMax*aircraftLength/NbPointsFront
  for i in range(1, NbPointsFront+1):
    x=xMax-i*step
    y= h_2 * (1 + sqrt(2*x*xMax - x*x) / xMax)
    vects.append(App.Vector(x,y,0))
  #   symetric points
  for vect in vects[-2::-1]:
    vects.append(App.Vector(vect.x,aircraftHeight-vect.y,0))

  # test
  #for vect in vects:
  #  sk.addGeometry(Part.Point(vect),False)

  MakeSpline(vects, perodic=False, sk=sk)

  # Constraints on spline
  pointTailFirstIx=0                                  # first point : start at tail
  pointTailLastIx=2*(NbPointsTail+NbPointsFront-1)    # last point : end at tail
  pointFrontIx=NbPointsTail+NbPointsFront-1           # front point element index
  splineIx=pointTailLastIx+1
  pointTopIx=NbPointsTail-1                           # top point at width/2 index
  pointBottompIx=pointTopIx + 2*NbPointsFront         # bottom point at -width/2 index
  constraintList = []
  #   front point on origin
  constraintList.append(Sketcher.Constraint('Coincident', pointFrontIx,1, -1,1))  
  #   first and last points coïncident on axis
  #constraintList.append(Sketcher.Constraint('Coincident',   pointTailFirstIx,1, pointTailLastIx,1))  # redondant ?
  constraintList.append(Sketcher.Constraint('PointOnObject', splineIx,1,      -1))  

  #sk.addConstraint(constraintList)
  del constraintList

  # create limit frame (elements sk.GeometryCount ..+3, top horizontal line first, clock wise)
  topFrameIx=sk.GeometryCount 
  rearFrameIx=topFrameIx+1
  bottomFrameIx=topFrameIx+2   
  frontFrameIx=topFrameIx+3
  constrGeoList = []
  constrGeoList.append(Part.LineSegment(App.Vector(0,              aircraftHeight, 0), App.Vector(aircraftLength, aircraftHeight, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector(aircraftLength, aircraftHeight, 0), App.Vector(aircraftLength, 0,              0)))
  constrGeoList.append(Part.LineSegment(App.Vector(aircraftLength, 0,              0), App.Vector(0,              0,              0)))
  constrGeoList.append(Part.LineSegment(App.Vector(0,              0,              0), App.Vector(0,              aircraftHeight, 0)))
  sk.addGeometry(constrGeoList,True)
  del constrGeoList
  
  constraintList = []
  constraintList.append(Sketcher.Constraint('Coincident', topFrameIx,2,    rearFrameIx,1))
  constraintList.append(Sketcher.Constraint('Coincident', rearFrameIx,2,   bottomFrameIx,1))
  constraintList.append(Sketcher.Constraint('Coincident', bottomFrameIx,2, frontFrameIx,1))
  constraintList.append(Sketcher.Constraint('Coincident', frontFrameIx,2,  topFrameIx,1))
  constraintList.append(Sketcher.Constraint('Horizontal', topFrameIx))
  constraintList.append(Sketcher.Constraint('Vertical',   rearFrameIx))
  constraintList.append(Sketcher.Constraint('Horizontal', bottomFrameIx))
  constraintList.append(Sketcher.Constraint('Vertical',   frontFrameIx))

  if fixedFrame:
    constraintList.append(Sketcher.Constraint('DistanceY', frontFrameIx,1, frontFrameIx,2, aircraftHeight))
    constraintList.append(Sketcher.Constraint('DistanceX', frontFrameIx,2, topFrameIx,2,   aircraftLength))
  
  # sketch within frame
  constraintList.append(Sketcher.Constraint('PointOnObject', pointFrontIx,1,     frontFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointTopIx,1,       topFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointBottompIx,1,   bottomFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', splineIx,1,         rearFrameIx))

  #sk.addConstraint(constraintList)
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

