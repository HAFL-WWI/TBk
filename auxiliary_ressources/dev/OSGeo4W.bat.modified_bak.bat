@echo off
rem This provides an OSGeo4W Shell 
rem with all environment variables (PATH) set to enable using the OSGeo4W tools
rem (OSGeo4W Python, Grass, Qt)

rem Root OSGEO4W home dir to the same directory this script exists in
rem use variable OSGEO4W_ROOT
rem expands to script location without trailing backslash
SET OSGEO4W_ROOT=%~dp0.

call %OSGEO4W_ROOT%\bin\o4w_env.bat

rem sometimes the grass version (grassXX) needs to be updated
call %OSGEO4W_ROOT%\apps\grass\grass83\etc\env.bat
path %PATH%;%OSGEO4W_ROOT%\apps\grass\grass83\lib

rem add various other paths to PATH
path %PATH%;%OSGEO4W_ROOT%\apps\qgis-ltr\bin
path %PATH%;%OSGEO4W_ROOT%\apps\Qt5\bin
path %PATH%;%OSGEO4W_ROOT%\apps\Python39\Scripts
path %PATH%;C:\Users\hbh1\AppData\Roaming\Python\Python39\Scripts
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis-ltr\python
set PYTHONHOME=%OSGEO4W_ROOT%\apps\Python39

set PATH=C:\Program Files\Git\bin;%PATH%

rem List available o4w programs
rem but only if osgeo4w called without parameters
@echo on
@if [%1]==[] (echo [OSGEO4W custom shell with enhanced PATH] run o-help for a list of available commands & cd /d "%~dp0" & cmd.exe /k) else (cmd /c "%*")
