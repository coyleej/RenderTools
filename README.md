# RenderTools
POV-Ray tools for use with MANTIS

This repository is a stand-alone development branch for the MANTIS rendering tools. 

The following is a brief description of what all files here do. For additional details, please refer to the docstrings in the functions.

Example scripts

* call_write_POV.py : example for rendering an image of a single device from a MANTIS json file, calls rendering.py

* call_gif_POV.py : example for rendering a gif containing a series of devices from a MANTIS json file, calls rendering.py

* call_isosurface.py : example for rendering a set of isosurfaces with a single unit cell

* povray_slurm.sh : example slurm batch file

Functional bits

* util.py : contains functions to extract data from the MANTIS json

* util_pov.py : contains all camera, header, and rendering functions

* util_shapes.py : functions describing/building a device

* util_iso.py : contains all isosurface-specific functions and functions for extracting the field information from a numpy array
