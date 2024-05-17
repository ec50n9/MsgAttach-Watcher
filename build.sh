#!/bin/bash

pyinstaller -F -w qt_main.py
cp -r ./assets ./dist/
cp ./version_list.json ./dist/
echo "Build finished!"