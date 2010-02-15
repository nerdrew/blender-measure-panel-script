#!/bin/bash
tmp=`pwd`
if [[ -n $1 ]]; then
  app=$1
else
  app=/Applications/blender.app
fi
cd "${app}/Contents/MacOS/.blender/scripts/modules"
ln -s "${tmp}/volume.py"
cd ../ui
ln -s "${tmp}/panel_measure.py"
