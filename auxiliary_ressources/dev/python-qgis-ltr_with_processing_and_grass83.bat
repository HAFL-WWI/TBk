@echo off
rem This script sets Environment variables for your Python interpreter
rem It is only useful when working with an IDE that supports code inspection/auto completion/...
rem in order for it to find all Python modules (QGIS and Plugin)

rem This .bat should be added to your C:\OSGeo4W\bin directory
rem where the python-qgis-ltr.bat is located
rem (default installation folder - adjust to your OSGeo4W install folder if needed)
rem In addition to the python-qgis-ltr.bat, it simply adds the GRASS env and QGIS Core plugins (e.g. Processing)

rem manually created by Hannes Horneber
rem 2023-10-18

rem ------------------------------------------------
rem Original contents of python-qgis-ltr.bat
rem this "cleans" PATH and maybe PYTHONPATH, therefore we need to add TBk dir at the end
call "%~dp0\o4w_env.bat"

path %OSGEO4W_ROOT%\apps\qgis-ltr\bin;%PATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis-ltr
set GDAL_FILENAME_IS_UTF8=YES
rem Set VSI cache to be used as buffer, see #6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%PYTHONPATH%

rem ------------------------------------------------
rem We call the grass env setup. Sometimes the grass version needs to be updated
call "%OSGEO4W_ROOT%\apps\grass\grass83\etc\env.bat"
rem We add Python core plugins to the PYTHONPATH (mainly for Processing to be found)
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python\plugins;%PYTHONPATH%

rem We can also add specific plugins to the PYTHONPATH
rem for an IDE to find them for debugging/code completion/inspection ...
rem We recommend manually configuring your IDE PYTHONPATH configuration
rem set TBK_QGIS_PLUGIN_DIR=C:\Users\hbh1\Projects\H07_TBk\Dev\TBk_QGIS_Plugin
rem set PYTHONPATH=%TBK_QGIS_PLUGIN_DIR%;%PYTHONPATH%
rem ------------------------------------------------

rem Finally run python
python %*