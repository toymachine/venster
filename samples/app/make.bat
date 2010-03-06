del /s /q dist
rd dist
python setup.py py2exe
copy COW.ICO dist
copy sampleapp.exe.manifest dist
REM update the line below if you installed NSIS in a different location:
"C:\Program Files\NSIS\makensis" installer.nsi