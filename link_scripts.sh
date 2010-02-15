#!/bin/bash
tmp=`pwd`
cd /Applications/blender.app/Contents/MacOS/.blender/scripts/modules
ln -s "${tmp}/volume.py"
cd ../ui
ln -s "${tmp}/panel_measure.py"
