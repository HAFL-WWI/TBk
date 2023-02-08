#!/bin/bash
# simply deploy the plugin without asking
# pb_tool must be installed and executable in the shell that this is run in
# also, this command must run in the main plugin directory, since pb_tools needs to find pb_tool.cfg
# consider adding a cd "absolute\path\to\plugin\dir" for your setup
pbt deploy -y