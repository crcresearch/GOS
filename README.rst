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

    pip3 install numpy pandas
    
    Note: If you are running the code on a shared space, use the following:
	module load python/3.6.0       #enables usage of pip3 
	pip3 install --user numpy pandas

Migration Example
-----------------
Migration is the primary and most robust example of using the global open simulator (GOS). 

GOS is designed to be run via commandline or more interactively Jupyter.

Command Line example

::

    1. Clone into the git repository (https://github.com/paulrbrenner/GOS.git) using:
	
	    git clone https://github.com/crcresearch/GOS
	
    2. Install required packages (if you have not already done so). From within the GOS directory, use:
	
	    pip3 install -r requirements.txt

    3. Navigate to GOS/examples/migration

    4. Execute migration.py with :

	    python3 migration.py
	    
For interactive Plotly Data Visualization in the command line

::
    
    1. Install plotly with:
    	
	pip3 install plotly
	
	If using a shared space use:
		pip3 install --user plotly 
	
    2. In VizDemo.py, comment out the basemap import. The imports should read:
    
    	#import basemapviz as viz
	import plotlyviz as viz
	
    3. Run VizDemo.py
    

Jupyter Example with Data Visualization
