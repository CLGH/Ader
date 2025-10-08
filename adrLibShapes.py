# -*- coding: utf-8 -*-
# ******************************************************************************
# *  Ader workbench                                                             *
# *    For more details see InitGui.py and the LICENCE text file.               *
# *                                                                             *
# *  Module : adrLibShapes.py                                                   *
# *    Library to generate aero shapes                                          *
# *     - from *.dat files                                                      *
# *     - low drag : NACA, Lyon, Hoerner, Duhamel                               *
# *     - front / top sketches                                                  *
# *     - fuselage frames                                                       *
# *                                                                             *
# *  Dependencies :                                                             *
# *                                                                             *
# *  History :                                                                  *
# *    2025-03-03 : adapted to FreeCad 1.0, better splines                      *
# *    2023-07-15 : adapted to Ader                                             *
# *    2021-10-05 : add Heiko and Gorissen code (modifications F. Nivoix)       *
# *    2021-07-28 : Initial release Claude GUTH (nacelle shapes)                *
# *                                                                             *
# *******************************************************************************

__title__ = "Ader Workbench - profils et formes fuselées"
__author__ = "Dirk GORISSEN, Claude GUTH, Jakob HEIKO"

import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Base
import Draft
import DraftTools
import Part
import Sketcher
import math
from math import pi, cos, sin, atan, radians
from math import sqrt, pow
import re
import adrWBCommon as wb
import adrLibPart

# debug messages handling
localDebug = False
# debug msg for this unit

def MakeTopView(fuselageLength, fuselageWidth, xRelMax= 0.33, fixedFrame= True, name='skTopView', plane='XY', body=None):
  doc=App.ActiveDocument
  if doc == None:
    raise Exception("Pas de document actif") 
  if body==None:
    body=doc.getObject('Fuselage')
    if body == None:
      raise Exception("Pas de corps actif") 
	
  sk = adrLibPart.NewSketch(name, plane, body)

  #l_2=fuselageLength/2
  w_2=fuselageWidth/2
  
  # Points 
  vects=[]
  #   Points from tail (elements 0..NbPointsTail-1)
  NbPointsTail=4
  step=(1-xRelMax)*fuselageLength/(NbPointsTail-1)
  for i in range(0, NbPointsTail):
    x=fuselageLength -i*step
    y=i*fuselageWidth/6
    vects.append(App.Vector(x,y,0))
  xMax=x
  #   Points to front (elements NbPointsTai1..NbPointsTail+NbPointsFront-1)
  NbPointsFront=5
  step=xRelMax*fuselageLength/NbPointsFront
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

  adrLibPart.MakeSpline(vects, perodic=False, sk=sk)

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
  constrGeoList.append(Part.LineSegment(App.Vector(0,               w_2, 0), App.Vector(fuselageLength,  w_2, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector(fuselageLength,  w_2, 0), App.Vector(fuselageLength, -w_2, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector(fuselageLength, -w_2, 0), App.Vector(0,              -w_2, 0)))
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
    constraintList.append(Sketcher.Constraint('DistanceY', frontFrameIx,1, frontFrameIx,2, fuselageWidth))
    constraintList.append(Sketcher.Constraint('DistanceX', frontFrameIx,2, topFrameIx,2,   fuselageLength))
  
  # sketch within frame
  constraintList.append(Sketcher.Constraint('PointOnObject', pointFrontIx,1,     frontFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointTopIx,1,       topFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointBottompIx,1,   bottomFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', splineIx,1,         rearFrameIx))

  sk.addConstraint(constraintList)
  del constraintList
  
  return sk
  
def MakeFaceView(fuselageLength, fuselageHeight, xRelMax= 0.33, fixedFrame= True, name='skFaceView', plane='XZ', body=None):
  doc=App.ActiveDocument
  if doc == None:
    raise Exception("Pas de document actif") 
  if body==None:
    body=doc.getObject('Fuselage')
    if body == None:
      raise Exception("Pas de corps actif") 
	
  sk = adrLibPart.NewSketch(name, plane, body)

  #l_2=fuselageLength/2
  h_2=fuselageHeight/2
  
  # Points 
  vects=[]
  #   Points from tail (elements 0..NbPointsTail-1)
  NbPointsTail=4
  step=(1-xRelMax)*fuselageLength/(NbPointsTail-1)
  for i in range(0, NbPointsTail):
    x=fuselageLength -i*step
    y=h_2 * (1+i/3)
    vects.append(App.Vector(x,y,0))
  xMax=x
  #   Arbitrary points for front (2*NbPointsFront-1 elements)
  NbPointsFront=5
  xRel=[0.90, 0.83, 0.53, 0.12, 0.00, 0.12, 0.50, 0.70, 0.90]  # rel to xMax
  hRel=[0.97, 0.92, 0.70, 0.60, 0.50, 0.28, 0.10, 0.03, 0.01]  # rel to fuselage height
  for i in range(0, 2*NbPointsFront-1):
    x= xRel[i] * xMax
    y= hRel[i] * fuselageHeight
    vects.append(App.Vector(x,y,0))
  #   symetric points at tail
  for vect in vects[NbPointsTail-1::-1]:
    vects.append(App.Vector(vect.x,fuselageHeight-vect.y,0))

  # test
  #for vect in vects:
    #sk.addGeometry(Part.Point(vect),False)
  #return sk

  adrLibPart.MakeSpline(vects, perodic=False, sk=sk)

  # Constraints on spline
  pointTailFirstIx=0                                  # first point : start at tail
  pointTailLastIx=2*(NbPointsTail+NbPointsFront-1)    # last point : end at tail
  pointFrontIx=NbPointsTail+NbPointsFront-1           # front point element index
  splineIx=pointTailLastIx+1
  pointTopIx=NbPointsTail-1                           # top point at width/2 index
  pointBottompIx=pointTopIx + 2*NbPointsFront         # bottom point at -width/2 index

  # create limit frame (elements sk.GeometryCount ..+3, top horizontal line first, clock wise)
  topFrameIx=sk.GeometryCount 
  rearFrameIx=topFrameIx+1
  bottomFrameIx=topFrameIx+2   
  frontFrameIx=topFrameIx+3
  constrGeoList = []
  constrGeoList.append(Part.LineSegment(App.Vector(0,              fuselageHeight, 0), App.Vector(fuselageLength, fuselageHeight, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector(fuselageLength, fuselageHeight, 0), App.Vector(fuselageLength, 0,              0)))
  constrGeoList.append(Part.LineSegment(App.Vector(fuselageLength, 0,              0), App.Vector(0,              0,              0)))
  constrGeoList.append(Part.LineSegment(App.Vector(0,              0,              0), App.Vector(0,              fuselageHeight, 0)))
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
  # left bottom on origin
  constraintList.append(Sketcher.Constraint('Coincident', frontFrameIx,1, -1,1))  

  if fixedFrame:
    constraintList.append(Sketcher.Constraint('DistanceY', frontFrameIx,1, frontFrameIx,2, fuselageHeight))
    constraintList.append(Sketcher.Constraint('DistanceX', topFrameIx,1,   topFrameIx,2,   fuselageLength))
  
  # sketch within frame
  constraintList.append(Sketcher.Constraint('PointOnObject', pointFrontIx,1,     frontFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointTopIx,1,       topFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointBottompIx,1,   bottomFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', splineIx,1,         rearFrameIx))

  sk.addConstraint(constraintList)
  del constraintList
  
  return sk

def MakeFrame(frameHeight, frameWidth, offset, xPos=0, fixedFrame= True, nbPoints=8, name='skFrame', plane='YZ', body=None):
  doc=App.ActiveDocument
  if doc == None:
    raise Exception("Pas de document actif") 
  if body==None:
    body=doc.getObject('Fuselage')
    if body == None:
      raise Exception("Pas de corps actif") 
  sk = adrLibPart.NewSketch(name, plane, body)
  sk.AttachmentOffset.Base.z = xPos

  # Points 
  vects=[]
  h=frameHeight/2
  w=frameWidth/2
  # points for spline (elements 0..nbPoints-1 from top clockwise)
  for i in range(0, nbPoints):
    angle=pi/2-i*2*pi/nbPoints
    x=w*cos(angle)
    y=h*sin(angle)+h+offset
    vects.append(App.Vector(x,y,0))
    #sk.addGeometry(Part.Point(App.Vector(x,y,0)),True)   # for test

  adrLibPart.MakeSpline(vects, perodic=True, sk=sk)

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
  constrGeoList.append(Part.LineSegment(App.Vector(-frameWidth/2, frameHeight+offset, 0),App.Vector(frameWidth/2,  frameHeight+offset, 0)))
  constrGeoList.append(Part.LineSegment(App.Vector( frameWidth/2, frameHeight+offset, 0),App.Vector(frameWidth/2,  offset,             0)))
  constrGeoList.append(Part.LineSegment(App.Vector( frameWidth/2, offset,             0),App.Vector(-frameWidth/2, offset,             0)))
  constrGeoList.append(Part.LineSegment(App.Vector(-frameWidth/2, offset,             0),App.Vector(-frameWidth/2, frameHeight+offset, 0)))
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
    constraintList.append(Sketcher.Constraint('DistanceY', rightFrameIx,2, -1,1, -offset))

  # in frame constraints
  constraintList.append(Sketcher.Constraint('PointOnObject', splineIx,1,      topFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointRightIx,1,  rightFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointBottomIx,1, bottomFrameIx))
  constraintList.append(Sketcher.Constraint('PointOnObject', pointLeftIx,1,   leftFrameIx))

  sk.addConstraint(constraintList)
  del constraintList

  return sk

def MakeFramesFromPlanes(body=None):
  doc=App.ActiveDocument
  if doc == None:
    raise Exception("Pas de document actif") 
  if body==None:
    body=doc.getObject('Fuselage')
    if body == None:
      raise Exception("Pas de corps actif") 

  skFace = doc.getObject("skFaceView")
  splineFace=skFace.getSubObject("Edge1")
  skTop = doc.getObject("skTopView")
  splineTop=skTop.getSubObject("Edge1")

  # get planes
  planes = []
  planes.append(doc.getObject("extSection"))
  for i in range(1, 100):
    plane = doc.getObject("extSection"+str(i).zfill(3))
    if plane != None:
      planes.append(plane)
    else:
      break

  for plane in planes:
    sk=plane.Base
    x= sk.AttachmentOffset.Base.x
    face=plane.getSubObject("Face1")
    section= face.Surface.intersect(splineFace.Curve)
    PointTop=section[0][0]
    PointBottom=section[0][1]
    offset=min(PointTop.Z, PointBottom.Z)
    height=abs(PointTop.Z - PointBottom.Z)
    section= face.Surface.intersect(splineTop.Curve)
    PointLeft=section[0][0]
    PointRight=section[0][1]
    width=abs(PointLeft.Y - PointRight.Y)
    print(i, ": ", offset, height, width, x)  # test
    MakeFrame(height, width, offset, x, body=body) 
    # suppress intermediate object
    doc.removeObject(plane.Name)
    doc.removeObject(sk.Name)
  
def FoilCoordsFromDat(filename, chord = 1.0,  setting = 0, originalFormat=False):
    # This code adapted from Heiko Jakob <heiko.jakob@gediegos.de>  (c) 2010 LGPL
    # Returns pseudo 2D foil coords from dat file as original strings
    # The common airfoil dat format has many flavors
    # This code should work with almost every dialect

    # Regex to identify data rows and throw away unused metadata
    regex = re.compile(
        r"^\s*(?P<xval>(\-|\d*)\.\d+(E\-?\d+)?)\,?\s*(?P<yval>\-?\s*\d*\.\d+(E\-?\d+)?)\s*$"
    )
    afile = open(filename, "r")
    # read the airfoil name which is always at the first line
    airfoilname = afile.readline().strip()

    coords = []
    upside = True
    last_x = None

    # Collect the data for the upper and the lower side seperately if possible
    for lin in afile:
        curdat = regex.match(lin)
        if curdat != None:
            x = curdat.group("xval")
            y = curdat.group("yval")

            # original format is text
            if originalFormat:
                coords.append([x, y])
            else:
                s=math.radians(setting) 
                xs=chord*float(x)*cos(s)+chord*float(y)*sin(s)
                ys=-chord*float(x)*sin(s)+chord*float(y)*cos(s)
                coords.append(App.Vector(xs, ys, 0.0))
        # End of if curdat != None
    # End of for lin in file
    afile.close()

    if len(coords) < 3:
        raise ValueError("Did not find enough coordinates.")
        return

    # sometimes coords are divided in upper an lower side
    # so that x-coordinate begin new from leading or trailing edge
    # check for start coordinates in the middle of list

    if coords[0:-1].count(coords[0]) > 1:
        flippoint = coords.index(coords[0], 1)
        upper = coords[0:flippoint]
        lower = coords[flippoint + 1 :]
        lower.reverse()
        for i in lower:
            upper.append(i)
        coords = upper

    return airfoilname, coords


#***************************************************************************
#*                                                                         *
#*   These routines to generate generate 4 and 5 digit NACA profiles       *
#*   The parameters in the numerical code can be entered into equations    *
#*    to precisely generate the cross-section of the airfoil               *
#*    and calculate its properties.                                        *
#*   https://en.wikipedia.org/wiki/NACA_airfoil                            *
#*                                                                         *
#*   Author : Dirk Gorissen <dgorissen@gmail.com>  Copyright (c) 2011      *
#*                                                                         *
#*   Created :  2011                                                       *
#*   Modified : 2019  airPlaneDesign WB integration                        *
#*                                                                         *
#***************************************************************************

def linspace(start,stop,np):
    """
    Emulate Matlab linspace
    """
    return [start+(stop-start)*i/(np-1) for i in range(np)]

def interpolate(xa,ya,queryPoints):
    """
    A cubic spline interpolation on a given set of points (x,y)
    Recalculates everything on every call which is far from efficient but does the job for now
    should eventually be replaced by an external helper class
    """

    # PreCompute() from Paint Mono which in turn adapted:
    # NUMERICAL RECIPES IN C: THE ART OF SCIENTIFIC COMPUTING
    # ISBN 0-521-43108-5, page 113, section 3.3.
    # http://paint-mono.googlecode.com/svn/trunk/src/PdnLib/SplineInterpolator.cs

    #number of points
    n = len(xa)
    u, y2 = [0]*n, [0]*n

    for i in range(1,n-1):

        # This is the decomposition loop of the tridiagonal algorithm.
        # y2 and u are used for temporary storage of the decomposed factors.

        wx = xa[i + 1] - xa[i - 1]
        sig = (xa[i] - xa[i - 1]) / wx
        p = sig * y2[i - 1] + 2.0

        y2[i] = (sig - 1.0) / p

        ddydx = (ya[i + 1] - ya[i]) / (xa[i + 1] - xa[i]) - (ya[i] - ya[i - 1]) / (xa[i] - xa[i - 1])

        u[i] = (6.0 * ddydx / wx - sig * u[i - 1]) / p


    y2[n - 1] = 0

    # This is the backsubstitution loop of the tridiagonal algorithm
    #((int i = n - 2; i >= 0; --i):
    for i in range(n-2,-1,-1):
        y2[i] = y2[i] * y2[i + 1] + u[i]

    # interpolate() adapted from Paint Mono which in turn adapted:
    # NUMERICAL RECIPES IN C: THE ART OF SCIENTIFIC COMPUTING
    # ISBN 0-521-43108-5, page 113, section 3.3.
    # http://paint-mono.googlecode.com/svn/trunk/src/PdnLib/SplineInterpolator.cs

    results = [0]*n

    #loop over all query points
    for i in range(len(queryPoints)):
        # bisection. This is optimal if sequential calls to this
        # routine are at random values of x. If sequential calls
        # are in order, and closely spaced, one would do better
        # to store previous values of klo and khi and test if

        klo = 0
        khi = n - 1

        while (khi - klo > 1):
            k = (khi + klo) >> 1
            if (xa[k] > queryPoints[i]):
                khi = k
            else:
                klo = k

        h = xa[khi] - xa[klo]
        a = (xa[khi] - queryPoints[i]) / h
        b = (queryPoints[i] - xa[klo]) / h

        # Cubic spline polynomial is now evaluated.
        results[i] = a * ya[klo] + b * ya[khi] + ((a * a * a - a) * y2[klo] + (b * b * b - b) * y2[khi]) * (h * h) / 6.0

    return results

def naca4(number, n, finite_TE = False, half_cosine_spacing = False):
    """
    Returns 2*n+1 points in [0 1] for the given 4 digit NACA number string
    """

    m = float(number[0])/100.0
    p = float(number[1])/10.0
    t = float(number[2:])/100.0

    a0 = +0.2969
    a1 = -0.1260
    a2 = -0.3516
    a3 = +0.2843

    if finite_TE:
        a4 = -0.1015 # For finite thick TE
    else:
        a4 = -0.1036 # For zero thick TE

    if half_cosine_spacing:
        beta = linspace(0.0,pi,n+1)
        x = [(0.5*(1.0-cos(xx))) for xx in beta]  # Half cosine based spacing
    else:
        x = linspace(0.0,1.0,n+1)

    yt = [5*t*(a0*sqrt(xx)+a1*xx+a2*pow(xx,2)+a3*pow(xx,3)+a4*pow(xx,4)) for xx in x]

    xc1 = [xx for xx in x if xx <= p]
    xc2 = [xx for xx in x if xx > p]

    if p == 0:
        xu = x
        yu = yt

        xl = x
        yl = [-xx for xx in yt]

        #xc = xc1 + xc2
        #zc = [0]*len(xc)
    else:
        yc1 = [m/pow(p,2)*xx*(2*p-xx) for xx in xc1]
        yc2 = [m/pow(1-p,2)*(1-2*p+xx)*(1-xx) for xx in xc2]
        zc = yc1 + yc2

        dyc1_dx = [m/pow(p,2)*(2*p-2*xx) for xx in xc1]
        dyc2_dx = [m/pow(1-p,2)*(2*p-2*xx) for xx in xc2]
        dyc_dx = dyc1_dx + dyc2_dx

        theta = [atan(xx) for xx in dyc_dx]

        xu = [xx - yy * sin(zz) for xx,yy,zz in zip(x,yt,theta)]
        yu = [xx + yy * cos(zz) for xx,yy,zz in zip(zc,yt,theta)]

        xl = [xx + yy * sin(zz) for xx,yy,zz in zip(x,yt,theta)]
        yl = [xx - yy * cos(zz) for xx,yy,zz in zip(zc,yt,theta)]

    X = xu[::-1] + xl[1:]
    Z = yu[::-1] + yl[1:]
    # AiplaneDesign modification - start
    coords=[]
    for i in range(len(X)) :
        coords.append(App.Vector(X[i],0,Z[i]))
    return coords

   # AiplaneDesign modification - end

def naca5(number, n, finite_TE = False, half_cosine_spacing = False):
    """
    Returns 2*n+1 points in [0 1] for the given 5 digit NACA number string
    """


    naca1 = int(number[0])
    naca23 = int(number[1:3])
    naca45 = int(number[3:])

    cld = naca1*(3.0/2.0)/10.0
    p = 0.5*naca23/100.0
    t = naca45/100.0

    a0 = +0.2969
    a1 = -0.1260
    a2 = -0.3516
    a3 = +0.2843

    if finite_TE:
        a4 = -0.1015 # For finite thickness trailing edge
    else:
        a4 = -0.1036  # For zero thickness trailing edge

    if half_cosine_spacing:
        beta = linspace(0.0,pi,n+1)
        x = [(0.5*(1.0-cos(x))) for x in beta]  # Half cosine based spacing
    else:
        x = linspace(0.0,1.0,n+1)

    yt = [5*t*(a0*sqrt(xx)+a1*xx+a2*pow(xx,2)+a3*pow(xx,3)+a4*pow(xx,4)) for xx in x]

    P = [0.05,0.1,0.15,0.2,0.25]
    M = [0.0580,0.1260,0.2025,0.2900,0.3910]
    K = [361.4,51.64,15.957,6.643,3.230]

    m = interpolate(P,M,[p])[0]
    k1 = interpolate(M,K,[m])[0]

    xc1 = [xx for xx in x if xx <= p]
    xc2 = [xx for xx in x if xx > p]
    #xc = xc1 + xc2

    if p == 0:
        xu = x
        yu = yt

        xl = x
        yl = [-x for x in yt]

        #zc = [0]*len(xc)
    else:
        yc1 = [k1/6.0*(pow(xx,3)-3*m*pow(xx,2)+ pow(m,2)*(3-m)*xx) for xx in xc1]
        yc2 = [k1/6.0*pow(m,3)*(1-xx) for xx in xc2]
        zc  = [cld/0.3 * xx for xx in yc1 + yc2]

        dyc1_dx = [cld/0.3*(1.0/6.0)*k1*(3*pow(xx,2)-6*m*xx+pow(m,2)*(3-m)) for xx in xc1]
        dyc2_dx = [cld/0.3*(1.0/6.0)*k1*pow(m,3)]*len(xc2)

        dyc_dx = dyc1_dx + dyc2_dx
        theta = [atan(xx) for xx in dyc_dx]

        xu = [xx - yy * sin(zz) for xx,yy,zz in zip(x,yt,theta)]
        yu = [xx + yy * cos(zz) for xx,yy,zz in zip(zc,yt,theta)]

        xl = [xx + yy * sin(zz) for xx,yy,zz in zip(x,yt,theta)]
        yl = [xx - yy * cos(zz) for xx,yy,zz in zip(zc,yt,theta)]

    X = xu[::-1] + xl[1:]
    Z = yu[::-1] + yl[1:]

    # AiplaneDesign modification - start
    coords=[]
    for i in range(len(X)) :
        coords.append(App.Vector(X[i],0,Z[i]))
    return coords

   # AiplaneDesign modification - end


#***************************************************************************
#* Main NACA generate routines                                             *
#***************************************************************************
def generateNacaCoords(number, n, finite_TE, half_cosine_spacing,scale,posX,posY,posZ,rotX,rotY,rotZ,):
    coords=[]
    if len(number)==4:
        coords=naca4(number, n, finite_TE, half_cosine_spacing)
    elif len(number)==5:
        coords=naca5(number, n, finite_TE, half_cosine_spacing)
    else:
        raise ValueError("Invalid NACA number")
    return coords

def generateNaca(number, n=240, finite_TE = False, half_cosine_spacing = True,scale=1,posX=0,posY=0,posZ=0,rotX=0,rotY=0,rotZ=0,rot=0,useSpline=True,splitSpline=False):
    coords=generateNacaCoords(number, n, finite_TE , half_cosine_spacing ,scale,posX,posY,posZ,rotX,rotY,rotZ)
    if useSpline:
        if splitSpline:
            splineLower = Part.BSplineCurve()
            splineUpper = Part.BSplineCurve()
            splineUpper.interpolate(coords[:len(coords)//2+1])
            splineLower.interpolate(coords[len(coords)//2:])
            if coords[0] != coords[-1]:
                wire = Part.Wire([splineUpper.toShape(),splineLower.toShape(),Part.makeLine(coords[0],coords[-1])])
            else:
                wire = Part.Wire([splineUpper.toShape(),splineLower.toShape()])
        else:
            spline = Part.BSplineCurve()
            spline.interpolate(coords)
            if coords[0] != coords[-1]:
                wire = Part.Wire([spline.toShape(),Part.makeLine(coords[0],coords[-1])])
            else:
                wire = Part.Wire(spline.toShape())
    else:
        # alternate solution, uses common Part Faces
        lines = []
        first_v = None
        last_v = None
        for v in coords:
            if first_v is None:
                first_v = v
            # End of if first_v is None
            # Line between v and last_v if they're not equal
            if (last_v != None) and (last_v != v):
                lines.append(Part.makeLine(last_v, v))
            # End of if (last_v != None) and (last_v != v)
            # The new last_v
            last_v = v
        # End of for v in upper
        # close the wire if needed
        if last_v != first_v:
                lines.append(Part.makeLine(last_v, first_v))
        wire = Part.Wire(lines)

    face = Part.Face(wire).scale(scale) #Scale the foil
    #face.Placement.Rotation.Axis.x=rotX
    #face.Placement.Rotation.Axis.y=rotY
    #face.Placement.Rotation.Axis.z=rotZ
    #face.Placement.Rotation.Angle=rot

    return face, coords



#***************************************************************************
#*                                                                         *
#*   These routines to generate nacelles                                   *
#*   https://fr.wikipedia.org/wiki/Corps_de_moindre_tra%C3%AEn%C3%A9e.     *
#*                                                                         *
#*   Author :   Claude GUTH                                                *
#*   Created :  2021-07-28                                                 *
#*                                                                         *
#***************************************************************************

def getLyonCoords(longueur, diametre, nbPoints=100):
  """
  :param longueur:          longueur (selon axe x) de la forme
  :param diametre:          diamètre de la forme
  :param nbPoints:          nb de points calculés
  :return: les coordonnées d'ordonnées positives d'une fome Lyon modèle A
  """
  # parametres intermédiaires de calcul
  ky = diametre*1.11326

  # points de la forme
  cLyon = [App.Vector(0, 0, 0)]
  kx = 1 / float(nbPoints-1)
  for i in range(1, nbPoints):
    xRel= kx * float(i) 
    xRel2= xRel * xRel
    xRel3= xRel2 * xRel
    xRel4= xRel3 * xRel
    yPos = ky * math.sqrt(xRel - xRel2 - xRel3 + xRel4)
    cLyon.append(App.Vector(xRel * longueur, yPos, 0))
  return cLyon

def getHoernerCoords(longueur, diametre, xRelEpaisseurMax, nbPoints=100):
  """
  :param longueur:          longueur (selon axe x) de la forme
  :param diametre:          diamètre de la forme
  :param xRelEpaisseurMax:  abscisse relative (0..1) pour l'épaisseur max
  :param nbPoints:          nb de points calculés
  :return: les coordonnées d'ordonnées positives d'une FEC
  """
  # parametres intermédiaires de calcul
  xeMax = xRelEpaisseurMax*longueur
  yeMax = 0.5*diametre
  pi_2 =  math.pi/2

  # points de la forme
  cFEC = [App.Vector(0, 0, 0)]
  kl = longueur / float(nbPoints-1)
  for i in range(1, nbPoints):
    xPos = kl * float(i)
    if xPos < xeMax:
      yPos = yeMax * math.sqrt(2*xPos*xeMax - xPos*xPos) / xeMax
    else:
      yPos = yeMax * math.cos(pi_2*(xeMax-xPos)/(longueur-xeMax))
    cFEC.append(App.Vector(xPos, yPos, 0))
  return cFEC

def getDuhamelCoords(longueur, diametre, nbPoints=100):
  """
  :param longueur:          longueur (selon axe x) de la forme
  :param diametre:          diamètre de la forme
  :param nbPoints:          nb de points calculés
  :return: les coordonnées d'ordonnées positives d'une forme Duhamel simplifiée
  """
  # parametres intermédiaires de calcul
  ky = diametre*1.3

  # points de la forme
  cLyon = [App.Vector(0, 0, 0)]
  kx = 1 / float(nbPoints-1)
  for i in range(1, nbPoints):
    xRel= kx * float(i) 
    yPos = ky * (1 - xRel) * math.sqrt(xRel)
    cLyon.append(App.Vector(xRel * longueur, yPos, 0))
  return cLyon

def getNACACoords(longueur, diametre, nbPoints=100):
  """
  :param longueur:          longueur (selon axe x) de la forme
  :param diametre:          diamètre de la forme
  :param nbPoints:          nb de points calculés
  :return: les coordonnées d'ordonnées positives d'une fome NACA 4 chiffres 
  """
  # parametres intermédiaires de calcul
  a0= 0.2969
  a1= -0.126
  a2= -0.3516
  a3= 0.2843
  a4= -0.1036
  ky = 5*diametre*diametre/longueur

  # points de la forme
  cNaca = [App.Vector(0, 0, 0)]
  kx = 1 / float(nbPoints-1)
  for i in range(1, nbPoints):
    xRel= kx * float(i) 
    xRel2= xRel * xRel
    xRel3= xRel2 * xRel
    xRel4= xRel3 * xRel
    yPos = ky * (a0*math.sqrt(xRel) + a1*xRel + a2*xRel2 + a3*xRel3 + a4*xRel4)
    cNaca.append(App.Vector(xRel * longueur, yPos, 0))
  return cNaca

