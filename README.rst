=========================
The Global Open Simulator
=========================

A system for global social modelling written in Python for Jupyter.

Installation
------------

GOS is designed to run on Python 3.

The following are the main dependencies:

- numpy
- pandas
- cartopy

Dependencies can be installed using pip:

::

   pip3 install -r requirements.txt

If you run into issues with installation using pip, try `conda
<https://conda.io/>`_ instead.

First, append conda-forge to your conda channels:

::

  conda config --append channels conda-forge

Then install the dependencies:

::

  conda install --file requirements.txt

If Jupyter Notebook doesn't recognize your conda environment, do:

::

  conda install -c anaconda ipykernel
  python -m ipykernel install --user --name=[conda_env_name]
  
replacing [conda_env_name] with the name of your conda environment.
