@echo off
cd ..

python setup.py bdist_wininst
python setup.py bdist
python setup.py bdist --format=msi

echo "Python requirements:"
echo "  * Python >= 3.6"
