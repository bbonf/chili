import sys
from setuptools import setup, find_packages
import glob, subprocess
import os


PROJECT="Chili"
ICON="Chili.icns"

plist={
    "CFBundleIconFile" : ICON,
    "CFBundleIdentifier" : "com.minimal-project.%s" % PROJECT,
    "LSUIElement": "YES"
    }


setup(
    name="Chili",
    version="0.0.1",
    packages=find_packages(),
    author="Ben Bonfil",
    author_email="bonfil@gmail.com",
    description="OS X Desktop Multi-tool",
    license="MIT",
    app=["Application.py"],
    data_files=["English.lproj"] +glob.glob("Resources/*.*"),
    options=dict(py2app=dict(
        plist=plist,
    )),
)
