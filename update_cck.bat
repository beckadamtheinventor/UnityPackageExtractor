@echo off
rem Removes the directory "ABI.CCK" if it exists, extract the desired package
rem Place this and "UnityPackageExtractor.exe" in your project's Assets folder.
rem Note that this should be done while Unity is closed to avoid needing to re-import.
rem Replace "ChilloutVR CCK v3.8 RELEASE" with the package name
set packagename=ChilloutVR CCK v3.8 RELEASE
set curdir=%0\..

rmdir /S /Q %curdir%\ABI.CCK
UnityPackageExtractor %packagename%.unitypackage %curdir%\..
