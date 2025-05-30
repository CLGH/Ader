::WinTools\adrTranslate
cd %AppData%\FreeCAD\Mod\Ader\translations
WinTools\pylupdate5 ..\InitGui.py -ts InitGui.ts
WinTools\pylupdate5 ..\adrNew.py -ts adrNew_py.ts
WinTools\pylupdate5 ..\adrInfos.py -ts adrInfos_py.ts
WinTools\pylupdate5 ..\adrSheetMain.py -ts adrSheetMain_py.ts
WinTools\pylupdate5 ..\adrFoil.py -ts adrFoil_py.ts
WinTools\pylupdate5 ..\adrNacelle.py -ts adrNacelle_py.ts
WinTools\pylupdate5 ..\adrFrame.py -ts adrFrame_py.ts
WinTools\pylupdate5 ..\adrExport.py -ts adrExport_py.ts

WinTools\lupdate ..\resources\adrInfos.ui -ts adrInfos_ui.ts
WinTools\lupdate ..\resources\adrFoil.ui -ts adrFoil_ui.ts
WinTools\lupdate ..\resources\adrNacelle.ui -ts adrNacelle_ui.ts
WinTools\lupdate ..\resources\adrFrame.ui -ts adrFrame_ui.ts

WinTools\lconvert -i adrInfos_ui.ts adrFoil_ui.ts adrNacelle_ui.ts adrFrame_ui.ts ^
   InitGui.ts adrNew_py.ts adrInfos_py.ts adrSheetMain_py.ts adrFoil_py.ts adrNacelle_py.ts adrFrame_py.ts adrExport_py.ts ^
  -o adrWB.ts

:: après traduction
:: lrelease adrWB_fr.ts

::WinTools\lupdate ..\resources\*.ui -ts translations/uifiles.ts
::WinTools\lconvert -i adrInfos_ui.ts adrFoil_ui.ts adrNacelle_ui.ts adrFrame_ui.ts -o adrWB.ts