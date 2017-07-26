Visualization for GOS

Introduction
------------

To visualize the result of simulation as a Geographic Heatmap in two different methods on Python.

Installation
------------

Visualization modules can run both on Python2 and Python3.

The following are dependencies:

- basemap
- plotly

They can be installed using conda and pip:

    conda(or conda3) install basemap
    sudo pip(or pip3) install plotly

Visualization Demo
------------------

Demo can be accessed by commond:

    cd GOS/examples/migration/
    python VizDemo.py

Note:
1. Basemap method is based on matplotlib library, and the output is a figure,
   while the Plotly is a commercial library and it will generate an interactive map within the html file.
2. You can switch the visualizaton methods by editing iVizDemo.py import part.
3. VizDemo.py should be in the same dictionary as migration.py.
