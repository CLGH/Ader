# The FreeCAD Ader Workbench

[![en](https://img.shields.io/badge/lang-en-blue.svg)](README.md)
[![fr](https://img.shields.io/badge/lang-fr-blue.svg)](README.fr.md)

![L'Avion](/doc/resources/avion_ader.png)

This workbench includes tools to facilitate aircraft design.  
WARNING: workbench under development, for experimental use only.

## Prerequisites
* FreeCAD &gt;= v 1.0.0

## Installation
Copy the Ader folder into the add-ons folder and restart FreeCAD.  
Note: on Windows, add-ons are located in %AppData%\FreeCAD\Mod

## Quickstart
Click the "New" button to create a new aircraft. Give your project a name, specify the length, width and height of the fuselage. Optionally, a CPACS filename (see note below).  
Ader creates two sketches, front view and top view, for the fuselage and a specifications sheet for your project's characteristics.

## Usage
### Fuselage
Edit the front and top sketches of the fuselage. Use the "Sections" function to create fuselage cross-section planes. Position these planes (right-click &gt; Transform) then use the "Frames" function to get adapted frames in the respective plane, frames that can be reworked? The "Build fuselage" button performs a loft operation.

### Wing / stabilizer
Fill in the specifications sheet:  
![Specs](/doc/resources/ader_spec.png)  
For airfoils, provide the name of the dat file. The .dat files, compiled by the UUIC (https://m-selig.ae.illinois.edu/ads/coord_database.html), are in the dat_profiles directory of the workbench.

Click the "Build wings and satbs" button to build and obtain the wing and stabilizers.  
![Build](/doc/resources/ader_build.png)

After construction, all airfoils and frames can be modified via the sketcher.  
You can also add airfoils, frames, nacelles (streamlined shapes https://fr.wikipedia.org/wiki/Corps_de_moindre_tra%C3%AEn%C3%A9e).

A user documentation is available in the workbench's doc folder.

This workbench is named Ader in homage to Clément Ader, aviation pioneer. Hoping it will have as rich a future as aviation since Mr. Ader.  
![Ader-Clement](/doc/resources/clement_ader_1891.png)

If you are interested in aircraft design, joining the Inter-Action association http://inter-action-aero.fr/ is highly recommended!

## Feedback


## Roadmap
Development of basic functions is done according to my available time for this project.  
If you wish to participate in the project, you are welcome.  
A programmer documentation is available in the workbench's doc folder.  
Note: originally, it was planned to enable file exchange in the CPACS standard (https://cpacs.de/) which describes an aircraft (and more) as an XML file. A code stub has been written, to be completed by a volunteer.

## Release Notes


## License
MIT
See [LICENSE](LICENSE) file

#Illustrations 
Wikipedia Creative Commons.