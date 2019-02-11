=========================
The Global Open Simulator
=========================

A system for global social modelling written in Python for Jupyter.

Installation
------------

GOS is designed to run on Python 3.

The following are dependencies:

- numpy
- pandas
- 

They can both be installed using pip:

::

    pip3 install numpy pandas
    
    # Note: If you are running the code on a shared space, use the following:
    # module load python/3.6.0       #enables usage of pip3 
    # pip3 install --user numpy pandas

Migration Example
-----------------

Our multi-scale migration model is the primary and most robust
example of using the global open simulator (GOS). 

::

    1. Clone into the git repository (https://github.com/crcresearch/GOS.git) using:
	
	    git clone https://github.com/crcresearch/GOS
	
    2. Install required packages (if you have not already done so). From within the GOS directory, use:
	
	    pip3 install -r requirements.txt

    3. Navigate to GOS/examples/multiscale-migration
