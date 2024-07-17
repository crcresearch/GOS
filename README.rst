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

Commit Hooks
^^^^^^^^^^^^

To ensure easier tracking of changes and to keep the repository clean, pre-commit is included as part of the requirements.
After installing required packages the following should be executed to install the git commit hooks which will clean the outputs from any notebooks before they are commited.

::

  pre-commit install

Examples
--------

This repository contains a number of examples in the examples directory.


Global Migration Model
^^^^^^^^^^^^^^^^^^^^^^

THE POPULAR GLOBAL MIGRATION MODEL CAN BE FOUND HERE:
https://github.com/crcresearch/GOS/blob/master/examples/multiscale-migration/GOS%2BMultiscale%2BMigration%2BModel.ipynb
