#!/bin/bash

import signac
from util import deep_access
from util_field import *
#from util_field import process_field_array, double_roll, extract_components
#from util_field import extract_e_field, extract_h_field, extract_real_components
#from util_field import calc_field_mag, calc_energy_density
from util_iso import create_mesh2, slice_isosurface
from util_pov import write_header_and_camera, render_pov
from util_shapes import create_device_layer, isosurface_unit_cell

import numpy as np
from skimage.measure import marching_cubes_lewiner
from os import system

############################
# Extract field from data  #
############################

np_data = "silo_contour.npy"

all_sims = np.load(np_data)
num_sims = len(all_sims)    # the number of simulations

# Grab a single simulation
field_array = all_sims[1]
field_array, nx, ny, nz = process_field_array(field_array, center=True)

# Choose the field type to plot
# Extract E-field, E-field magnitude
e_field, ex, ey, ez = extract_e_field(field_array)
e_mag = calc_field_mag(e_field)

########################
# Isosurface variables #
########################

# ISOSURFACE CREATION
# Field
field = e_mag
# Isosurface values
#cutoffs = [0.5, 1.0, 1.5]
cutoffs = [0.03, 0.5, 1.0, 1.5, 2.0, 2.7]
#cutoffs = [0.03, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7]
# Colormap and isosurface transparency
colormap = "viridis"
transmit = 0.6
# Colormap min and max values; uses field extrema if unspecified (letters are unrealistic bounds)
#cmap_limits = ["a", "b"]
cmap_limits = [min(cutoffs), max(cutoffs)]

# INTERSECTION BOX
# box bounds are the origin and (nx, ny, nz)
# Uses the intersection function if True
use_slice = False
# Makes POV-Ray's intersect function behave like the difference function
subtract_box = True
# Two opposite corners of the box 
corner1 = [(0.5 * nx), (0.5 * ny), 0]
corner2 = [nx, ny, nz]

# UNIT CELL
add_unit_cell = True
json_file = "DeviceFiles/Silos/device.index.json.gz"
device_id = "08dd6608e15a264449c78353509083d2"  # Optica Fig 3c
UC_transmit = 0
use_slice_UC = True
subtract_box_UC = True


# RENDERING PARAMETERS
# Code currently expects all camera values to be set in a separate file
height = 800
width = height
pov_name = "mesh_test.pov"
image_name = "mesh_test.png"
display = False
transparent = True
antialias = True
num_threads = 4
open_png = True
render = True


#### Isosurface creation ####

# Generate povray mesh2 string
mesh = create_mesh2(
        field=e_mag, 
        cutoffs = cutoffs, 
        colormap = colormap, 
        cmap_limits = cmap_limits)

# Use a box to slice the isosurface; modifies the mesh string 
if use_slice == True:
    mesh = slice_isosurface(mesh, corner1, corner2, 
            subtract_box = subtract_box)

# Add unit cell
if add_unit_cell == True:
    with signac.Collection.open(json_file, compresslevel=1) as d_index:
        device_dict = list(d_index.find(filter={"_id": device_id}))[0]

    mesh = isosurface_unit_cell(mesh, device_dict, 
            n = [nx, ny, nz], 
            use_slice_UC = use_slice_UC, 
            transmit = UC_transmit, 
            corner1 = corner1, 
            corner2 = corner2, 
            subtract_box = True)

# Generate header and camera info
header = write_header_and_camera(device_dims = [nx, ny, nz], 
        camera_rotate = 35, 
        isosurface=True)

fID = open(pov_name, 'w')
fID.write(header + mesh)
fID.close()

# Render
render_pov(pov_name, image_name, height, width, display,
    transparent, antialias, num_threads, open_png, render)

