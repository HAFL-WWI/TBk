#!/bin/bash
# This simply deploys the plugin without asking (-y) according to the pb_tool.cfg

# pb_tool must be installed and executable in the shell that this script runs in.
# Also, this command must run in the main plugin directory, since pb_tools needs to find pb_tool.cfg
# For this consider one of the following
#   - run with "scripts\pbt_deploy.sh" from main plugin directory
#   - in pyCharm (or the IDE of your choice), create a run configuration with plugin dir as working directory
#   - add a cd "absolute\path\to\plugin\dir" for your setup (don't commit this to git though)
cd C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/tbk_qgis
pbt deploy -y