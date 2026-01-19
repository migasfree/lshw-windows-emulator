@echo off
cd ..

echo Creating package...
python -m build

echo Python requirements:
echo   * Python >= 3.6
echo       - psutil
echo       - wmi
