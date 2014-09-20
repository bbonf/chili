#!/bin/bash

rm -Rf dist/Chili.app
python setup.py py2app -A
dist/Chili.app/Contents/MacOS/Chili
