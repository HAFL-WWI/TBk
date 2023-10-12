rem This script sets Environment variables for your Python interpreter
rem It is only useful when working with an IDE that supports code inspection/auto completion/...
rem in order for it to find all Python modules (QGIS and Plugin)

rem The script is based on the python-qgis-ltr.bat (which calls o4w_env.bat) adjusted to be called from here
rem If the original scripts change with updates, this might need to be updated as well.

rem author: Hannes Horneber, 2023-10-12

@echo off
rem ------------------------------------------------
rem Original contents of python-qgis-ltr.bat

rem This replaces call "%~dp0\o4w_env.bat"
rem .....................
set OSGEO4W_ROOT=C:\OSGeo4W
rem start with clean path
set path=%OSGEO4W_ROOT%\bin;%WINDIR%\system32;%WINDIR%;%WINDIR%\system32\WBem
for %%f in ("%OSGEO4W_ROOT%\etc\ini\*.bat") do call "%%f"
rem .....................

path %OSGEO4W_ROOT%\apps\qgis-ltr\bin;%PATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis-ltr
set GDAL_FILENAME_IS_UTF8=YES
rem Set VSI cache to be used as buffer, see #6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%PYTHONPATH%

rem ------------------------------------------------

rem ------------------------------------------------
rem Get the tbk plugin directory relative to this directory
setlocal enabledelayedexpansion
rem Get the directory of this script
set "script_dir=%~dp0"
rem Define the relative directory
set "relative_dir=..\..\tbk_qgis"
rem Use pushd to change to the script's directory and then navigate to the relative directory
pushd "%script_dir%"
cd "%relative_dir%"
rem get absolute directory
set tbk_plugin_dir=!CD!
popd
end local

rem We add the tbk plugin directory to the PYTHONPATH
set PYTHONPATH=%tbk_plugin_dir%;%PYTHONPATH%
rem ------------------------------------------------

rem Test if everything worked (uncomment for debugging)
rem ------------------------------------------------
rem echo %OSGEO4W_ROOT%
rem echo %PATH%
rem echo %PYTHONPATH%

C:\OSGeo4W\bin\python-qgis-ltr.bat
rem ------------------------------------------------