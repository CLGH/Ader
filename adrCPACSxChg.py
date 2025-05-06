# -*- coding: utf-8 -*-
# ******************************************************************************
#*  Ader workbench                                                             *
#*    For more details see InitGui.py and the LICENCE text file.               *
#*                                                                             *
#*  Module : adrCPACSxChg.py                                                   *
#*    Library to handle exchanges with CPACS xml files                         *
#*                                                                             *
#*  Dependencies :                                                             *
#*                                                                             *
#*  History :                                                                  *
#*    2023-07-15 : Initial release, tested on FreeCAD 0.20                     *
#*                                                                             *
#*******************************************************************************

__title__  = "Ader Workbench - CPACS read/write utilities"
__author__ = "Claude GUTH"

import os
import re
import math, cProfile, string
from pathlib import Path
import xml.etree.ElementTree as ET
import adrWBCommon as wb
import adrLibShapes as shapes
import adrCPACSTemplates as CPACS_templates

# debug messages handling
localDebug= True;        # debug msg for this unit     


def WingInCPACS(cpacs_file_path, wing_id, span, sweep, foil_in, cord_in, wedge_in, foil_out, cord_out, wedge_out):
     # Load CAPCS file
    tree = ET.parse(cpacs_file_path)
    root = tree.getroot()
  
    # Get wing elements transformations
    xml_wing_transformation_el_in= CPACS_templates.TransformationXML(name= wing_id + "_el_in_transf", \
                                                                      scale_x=cord_in, scale_y=cord_in, scale_z=cord_in, \
                                                                      rot_y=wedge_in)
    xml_wing_transformation_el_out= CPACS_templates.TransformationXML(name=wing_id + "_el_out_transf", \
                                                                      scale_x=cord_out, scale_y=cord_out, scale_z=cord_out, \
                                                                      rot_y=wedge_out)

    # Get wing sections ( + elements )
    sect_in_id = wing_id + "_sect_in"
    xml_wing_sect_in= CPACS_templates.WingSectionXML(sect_in_id, section_foil= foil_in, \
                                                     section_trans=CPACS_templates.TransformationXML(sect_in_id + "_transf"), \
                                                     section_el_trans=xml_wing_transformation_el_in)
    sect_out_id = wing_id + "_sect_out"
    xml_wing_sect_out= CPACS_templates.WingSectionXML(sect_out_id, section_foil= foil_out, \
                                                     section_trans=CPACS_templates.TransformationXML(sect_out_id + "_transf"), \
                                                     section_el_trans=xml_wing_transformation_el_out)
    xml_wing_sections= xml_wing_sect_in + xml_wing_sect_out
    el_in_id = sect_in_id + "_el"
    el_out_id = sect_out_id + "_el"


    # Get wing sections positions
    xml_wing_sections_pos_in= CPACS_templates.PositionXML(wing_id + "_pos_in", len=0, sweep=-90, dieth=0, fromID='', toID=sect_in_id)
    xml_wing_sections_pos_out= CPACS_templates.PositionXML(wing_id + "_pos_out", len=span/2, sweep=sweep, dieth=0, fromID=sect_in_id, toID=sect_out_id)
    xml_wing_sections_pos= xml_wing_sections_pos_in + xml_wing_sections_pos_out

    # Get wing segments
    xml_wing_segments= CPACS_templates.WingSegmentXML(name=wing_id + "_segment", segment_from=el_in_id, segment_to=el_out_id)

    # Get wing xml
    xml_wing= CPACS_templates.wing.format(wing_id=wing_id, wing_name=wing_id, wing_descrition="", \
                                          wing_trans=CPACS_templates.TransformationXML(wing_id + "_transf"), \
                                          wing_sections=xml_wing_sections, \
                                          wing_sections_pos=xml_wing_sections_pos, \
                                          wing_segments= xml_wing_segments)
    wb.debugMsg("xml : \n" + xml_wing, localDebug)
 
    # Get wing tree element, remove if required
    xmle_wings = root.find(".//wings")
    for wing in xmle_wings.findall("./wing"):
      if wing.get("uID") == wing_id:
        xmle_wings.remove(wing)
        break
          
    # insert new wing        
    xmle_wing= ET.fromstring(xml_wing)
    xmle_wings.append(xmle_wing)
 
    # make it pretty and save
    #ET.indent(tree, space="  ", level=0)  #Note, the indent() function was added in Python 3.9.  >> FreeCAD 0.21
    tree.write(cpacs_file_path, xml_declaration=True, encoding='utf-8', method="xml")

def FuselageInCPACS(cpacs_file_path, fuselage_def):
     # Load CAPCS file
    tree = ET.parse(cpacs_file_path)
    root = tree.getroot()
  
    # Get wing elements transformations
    xml_wing_transformation_el_in= CPACS_templates.TransformationXML(name= wing_id + "_el_in_transf", \
                                                                      scale_x=cord_in, scale_y=cord_in, scale_z=cord_in, \
                                                                      rot_y=wedge_in)
    xml_wing_transformation_el_out= CPACS_templates.TransformationXML(name=wing_id + "_el_out_transf", \
                                                                      scale_x=cord_out, scale_y=cord_out, scale_z=cord_out, \
                                                                      rot_y=wedge_out)

    # Get wing sections ( + elements )
    sect_in_id = wing_id + "_sect_in"
    xml_wing_sect_in= CPACS_templates.WingSectionXML(sect_in_id, section_foil= foil_in, \
                                                     section_trans=CPACS_templates.TransformationXML(sect_in_id + "_transf"), \
                                                     section_el_trans=xml_wing_transformation_el_in)
    sect_out_id = wing_id + "_sect_out"
    xml_wing_sect_out= CPACS_templates.WingSectionXML(sect_out_id, section_foil= foil_out, \
                                                     section_trans=CPACS_templates.TransformationXML(sect_out_id + "_transf"), \
                                                     section_el_trans=xml_wing_transformation_el_out)
    xml_wing_sections= xml_wing_sect_in + xml_wing_sect_out
    el_in_id = sect_in_id + "_el"
    el_out_id = sect_out_id + "_el"


    # Get wing sections positions
    xml_wing_sections_pos_in= CPACS_templates.PositionXML(wing_id + "_pos_in", len=0, sweep=-90, dieth=0, fromID='', toID=sect_in_id)
    xml_wing_sections_pos_out= CPACS_templates.PositionXML(wing_id + "_pos_out", len=span/2, sweep=sweep, dieth=0, fromID=sect_in_id, toID=sect_out_id)
    xml_wing_sections_pos= xml_wing_sections_pos_in + xml_wing_sections_pos_out

    # Get wing segments
    xml_wing_segments= CPACS_templates.WingSegmentXML(name=wing_id + "_segment", segment_from=el_in_id, segment_to=el_out_id)

    # Get wing xml
    xml_wing= CPACS_templates.wing.format(wing_id=wing_id, wing_name=wing_id, wing_descrition="", \
                                          wing_trans=CPACS_templates.TransformationXML(wing_id + "_transf"), \
                                          wing_sections=xml_wing_sections, \
                                          wing_sections_pos=xml_wing_sections_pos, \
                                          wing_segments= xml_wing_segments)
    wb.debugMsg("xml : \n" + xml_wing, localDebug)
 
    # Get wing tree element, remove if required
    xmle_wings = root.find(".//wings")
    for wing in xmle_wings.findall("./wing"):
      if wing.get("uID") == wing_id:
        xmle_wings.remove(wing)
        break
          
    # insert new wing        
    xmle_wing= ET.fromstring(xml_wing)
    xmle_wings.append(xmle_wing)
 
    # make it pretty and save
    #ET.indent(tree, space="  ", level=0)  #Note, the indent() function was added in Python 3.9.  >> FreeCAD 0.21
    tree.write(cpacs_file_path, xml_declaration=True, encoding='utf-8', method="xml")

def DatInCPACS(cpacs_file_path, dat_file_path):
    # read .dat file
    fname, fcoords = shapes.FoilCoordsFromDat(dat_file_path)
    fid= Path(dat_file_path).stem

    # Convert .dat lines to CPACS Vector type
    sx = ";".join([coord[0] for coord in fcoords])
    sy = ";".join(['0'] * len(fcoords))
    sz = ";".join([coord[1] for coord in fcoords])
	
    # Load CAPCS file
    tree = ET.parse(cpacs_file_path)
    root = tree.getroot()
  
    # Get wingAirfoils element remove foil if required
    xmle_foils = root.find(".//wingAirfoils")
    for foil in xmle_foils.findall("./wingAirfoil"):
      if foil.get("uID") == fid:
        xmle_foils.remove(foil)
        break

    # insert new wingAirfoil        
    xml_text = CPACS_templates.wing_profile.format(id=fid, name=fname, x_=sx, y_=sy, z_=sz)
    wb.debugMsg("xml text : " + '\n' + xml_text + '\n', localDebug)
    xmle_foil= ET.fromstring(xml_text)
    xmle_foils.append(xmle_foil)
 
    # make it pretty and save
    #ET.indent(tree, space="  ", level=0)  #Note, the indent() function was added in Python 3.9.  >> FreeCAD 0.21
    tree.write(cpacs_file_path, xml_declaration=True, encoding='utf-8', method="xml")


def DatInCPACSOld(dat_file_path, cpacs_file_path):
    # Lecture du fichier .dat
    fname, fcoords = shapes.FoilCoordsFromDat(dat_file_path)

    # Conversion des lignes du fichier .dat en éléments XML
    sx = fcoords[0][0]
    sy = '0'
    sz = fcoords[0][1]
    for coords in fcoords[1:]:
        # Concaténation des valeurs
        sx = sx + ';' + coords[0]
        sy = sy + ';' + "0"
        sz = sz + ';' + coords[1]

	# Chargement du fichier XML existant
    tree = ET.parse(cpacs_file_path)
    root = tree.getroot()
  
    # Recherche de l'emplacement profils DB 
    xmle_foils = root.find(".//wingAirfoils")

    # Création de l'élément wingAirfoil pour les données du fichier .dat
    xmle_foil_dat = ET.SubElement(xmle_foils, "wingAirfoil", uID=Path(dat_file_path).stem)

    # Création de l'élément name
    xmle_foil_name = ET.SubElement(xmle_foil_dat, "name")
    xmle_foil_name.text = fname

    # Insertion des points
    xmle_foil_points = ET.SubElement(xmle_foil_dat, "pointList")
    xmle_foil_points_x = ET.SubElement(xmle_foil_points, "x", mapType="vector")
    xmle_foil_points_x.text = sx
    xmle_foil_points_y = ET.SubElement(xmle_foil_points, "y", mapType="vector")
    xmle_foil_points_y.text = sy
    xmle_foil_points_z = ET.SubElement(xmle_foil_points, "z", mapType="vector")
    xmle_foil_points_z.text = sz

    # Enregistrement des modifications dans le fichier XML
    ET.indent(tree, space="  ", level=0)
    tree.write(cpacs_file_path, xml_declaration=True, encoding='utf-8', method="xml")