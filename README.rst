=========================
The Global Open Simulator
=========================

A parallel agent-based platform for global social modelling.

Introduction
------------

GOS is designed to enable high scale agent-based modeling in Python (and Jupyter).
By using the ``multiprocessing`` library, GOS is able to run in parallel.

Installation
------------

GOS is designed to run on Python 3.

The following are dependencies:

- numpy
- pandas

They can both be installed using pip:

::

    pip install numpy pandas

Migration Example
-----------------

GOS is designed to be run via commandline or more interactively Jupyter.

Command Line example

::

    1. Clone into the git repository (https://github.com/paulrbrenner/GOS.git) using:
	
	    git clone https://github.com/crcresearch/GOS
	
    2. Install required packages. Navigate to gosdemo/GOS. Then use:
	
	    pip3 install -r requirements.txt

    3. Navigate to GOS/examples/migration

    4. Execute migration.py with:

	    python3 migration.py
	    
For interactive Plotly Data Visualization in the command line

::
    
    1. Install plotly with:
    	
	pip3 install plotly
	
    2. In VizDemo.py, comment out the basemap import. The imports should read:
    
    	#import basemapviz as viz
	import plotlyviz as viz
	
    3. Run VizDemo.py
    

Jupyter Example with Data Visualization
