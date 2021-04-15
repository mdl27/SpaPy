# SpaPy
Fast and fun geospatial library based on open source software.
A website with installation instructions and tutorials is available at: <a href="http://spapy.org">spapy.org</a>.

#Installation instructions (for Windows only)

run:

git clone https://github.com/mdl27/SpaPy --branch SpaPy-whl

cd spapy

# in case wheel and setuptools are not installed already
pip install wheel setuptools

# creates the SpaPy whl file
python setup.py bdist_wheel
