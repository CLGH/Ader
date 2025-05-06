# -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    For more details see InitGui.py and the LICENCE text file.               *
#*                                                                             *
#*  Module : adrCPACSTemplates.py                                              *
#*    CPACS xml templates                                                      *
#*                                                                             *
#*  Dependencies :                                                             *
#*                                                                             *
#*  History :                                                                  *
#*    2023-07-13 : Initial release, tested on FreeCAD 0.20                     *
#*                                                                             *
# ******************************************************************************
""" @package adrCPACSTemplates
    CPACS xml templates.
 
"""
__title__ = "FreeCAD Ader CPACS templates"
__author__ = "Claude GUTH"
__url__ = "https://github.com/   /FreeCAD_Ader"

import os
import adrWBCommon as wb


# debug messages handling
localDebug= False;        # debug msg for this unit

# template for header
header = \
'''<?xml version='1.0' encoding='utf-8'?>
<cpacs xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="https://github.com/DLR-SL/CPACS/tree/develop/schema/cpacs_schema.xsd">
  <header>
    <name>{project_name}</name>
    <description>{project_desc}</description>
    <creator>{project_author}</creator>
    <timestamp>{project_timestamp}</timestamp>
    <version>{project_version}</version>
    <cpacsVersion>3.3</cpacsVersion>
    <updates>
    </updates>
  </header>
</cpacs>
'''

# template for transformation
transformation = \
  '''<transformation uID="{transformation_id}">
    <scaling uID="{trans_scale_name}">
        <x>{trans_scale_x}</x>
        <y>{trans_scale_y}</y>
        <z>{trans_scale_z}</z>
      </scaling>
      <rotation uID="{trans_rot_name}">
        <x>{trans_rot_x}</x>
        <y>{trans_rot_y}</y>
        <z>{trans_rot_z}</z>
      </rotation>
      <translation uID="{trans_trans_name}">
        <x>{trans_trans_x}</x>
        <y>{trans_trans_y}</y>
        <z>{trans_trans_z}</z>
      </translation>
    </transformation>
  '''
def TransformationXML(name, scale_x=1, scale_y=1, scale_z=1, rot_x=0, rot_y=0, rot_z=0, trans_x=0, trans_y=0, trans_z=0):
    '''Return transmation xml chunk, default unity if no params for scale, rot ans translation'''
    return transformation.format(transformation_id=name, \
                                 trans_scale_name=name+ '_scale' , \
                                 trans_scale_x= scale_x, trans_scale_y= scale_y, trans_scale_z= scale_z, \
                                 trans_rot_name=name+ '_rot' , \
                                 trans_rot_x= rot_x, trans_rot_y= rot_y, trans_rot_z= rot_z, \
                                 trans_trans_name=name+ '_transl' , \
                                 trans_trans_x= trans_x, trans_trans_y= trans_y, trans_trans_z= trans_z)


# template for position
positioning = \
  '''<positioning uID="{pos_id}">
      <name>{pos_name}</name>
      <length>{pos_len}</length>
      <sweepAngle>{pos_sweep}</sweepAngle>
      <dihedralAngle>{pos_dieth}</dihedralAngle>
      <fromSectionUID>{pos_fromID}</fromSectionUID>
      <toSectionUID>{pos_toID}</toSectionUID>
    </positioning>
  '''
def PositionXML(name, len=1, sweep=0, dieth=0, fromID='', toID=''):
    '''Return position xml chunk'''
    return positioning.format(pos_id=name, \
                              pos_name= name,  \
                              pos_len= len,  \
                              pos_sweep= sweep,  \
                              pos_dieth= dieth,  \
                              pos_fromID= fromID,  \
                              pos_toID= toID)



wing_section = \
'''<section uID="{wing_section_id}">
    <name>{wing_section_name}</name>
      {wing_section_trans}
      <elements>
        <element uID="{wing_el_ID}">
          <name>{wing_el_name}</name>
          <airfoilUID>{wing_el_foil}</airfoilUID>
          {wing_el_trans}
        </element>
      </elements>
  </section>
''' 
def WingSectionXML(name, section_foil, section_trans='', section_el_trans=''):
    '''Return wing section xml chunk'''
    return wing_section.format(wing_section_id=name, \
                               wing_section_name= name,  \
                               wing_section_trans= section_trans,  \
                               wing_el_ID= name + '_el',  \
                               wing_el_name= name + '_el',  \
                               wing_el_foil= section_foil,  \
                               wing_el_trans= section_el_trans)


wing_segment = \
'''<segment uID="{wing_seg_ID}">
    <name>{wing_seg_name}</name>
    <fromElementUID>{wing_seg_from}</fromElementUID>
    <toElementUID>{wing_seg_to}</toElementUID>
  </segment>
''' 
def WingSegmentXML(name, segment_from='', segment_to=''):
    '''Return wing section xml chunk'''
    return wing_segment.format(wing_seg_ID=name, \
                               wing_seg_name= name, \
                               wing_seg_from= segment_from, \
                               wing_seg_to= segment_to)


# template for wing
wing = \
'''<wing uID="{wing_id}" symmetry="x-z-plane">
    <name>{wing_name}</name>
    <description>{wing_descrition}</description>
    {wing_trans}
    <sections>
      {wing_sections}
    </sections>
    <positionings>
      {wing_sections_pos}
    </positionings>
    <segments>
      {wing_segments}
    </segments>
  </wing>
  
'''    

# template for wing profile
wing_profile = \
'''<wingAirfoil  uID="{id}" xsi:type="wingAirfoilsType">
    <name>{name}</name>
    <pointList>
       <x mapType="vector">{x_}</x>
       <y mapType="vector">{y_}</y>
       <z mapType="vector">{z_}</z>
     </pointList>
   </wingAirfoil>
'''    

fuse_section = \
'''<section uID="{fuse_section_id}  xsi:type="fuselageSectionType"">
    <name>{fuse_section_name}</name>
    <description>{fuse_section_desc}</description>
    <profileUID>{fuse_section_profile}</profileUID>
    {fuse_section_transf}
  </section>
''' 
# template for fuselage
fuselage = \
'''<fuselage uID="{fuse_id}" xsi:type="fuselageType">
    <name>{fuse_name}</name>
    <description>{fuse_descrition}</description>
    {fuse_transf}
    <sections xsi:type="fuselageSectionsType">
      {fuse_sections}
    </sections>
    <positionings xsi:type="positioningsType">
      {fuse_sections_pos}
    </positionings>
    <segments xsi:type="fuselageSegmentsType">
      {wing_segments}
    </segments>
  </fuselage>
'''    
# template for fuselage profiles
fuse_profile = \
'''<fuselageProfile  uID="{id}" xsi:type="profileGeometryType">
    <name>{name}</name>
    <description>{desc}</description>
    <pointList>
       <x mapType="vector">{x_}</x>
       <y mapType="vector">{y_}</y>
       <z mapType="vector">{z_}</z>
     </pointList>
   </fuselageProfile>
'''    
