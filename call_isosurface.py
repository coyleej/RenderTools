#!/bin/bash

from os import system
import numpy as np
from skimage.measure import marching_cubes_lewiner

import signac
from util import deep_access
from util_iso import create_mesh2, slice_isosurface, process_field_array
from util_iso import extract_e_field, calc_field_mag
from util_pov import write_header_and_camera, render_pov
from util_shapes import create_device_layer, isosurface_unit_cell
from util_shapes import add_slab, set_color_and_finish 

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

print(nx, ny, nz)


########################
# Isosurface variables #
########################

# ISOSURFACE CREATION
# Field
field = e_mag
# Isosurface values
cutoffs = [0.15, 0.5, 1.0, 1.5, 2.0, 2.5]
#cutoffs = [0.03, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7]

# Colormap and isosurface transparency
colormap = "hot"
transmit = 0.0

# Colormap min and max values; uses field extrema if unspecified
# (letters are unrealistic bounds)
#cmap_limits = ["a", "b"]
cmap_limits = [min(cutoffs), max(cutoffs)]

# INTERSECTION BOX
# Box bounds are the origin and (nx, ny, nz)
# Uses the intersection function if True
use_slice = False
# POV-Ray's intersect function behaves like 
# the difference function if True.
subtract_box = True
# Two opposite corners of the box 
corner1 = [(0.5 * nx), (0.5 * ny), 0]
corner2 = [nx, ny, nz]

# UNIT CELL
add_unit_cell = True
json_file = "DeviceFiles/Silos/device.index.json.gz"
device_id = "08dd6608e15a264449c78353509083d2"  # Optica Fig 3c
#UC_transmit = 0.0  ## Removed
use_slice_UC = True
subtract_box_UC = True
substrate_thickness = 25

# RENDERING PARAMETERS
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
        transmit = transmit,
        cmap_limits = cmap_limits)

# Use a box to slice the isosurface; modifies the mesh string 
if use_slice == True:
    mesh = slice_isosurface(mesh, corner1, corner2, 
            subtract_box = subtract_box)

# Add unit cell
if add_unit_cell == True:
    with signac.Collection.open(json_file, compresslevel=1) as d_index:
        device_dict = list(d_index.find(filter={"_id": device_id}))[0]

    mesh = isosurface_unit_cell(
            mesh, 
            device_dict, 
            n = [nx, ny, nz], 
            use_slice_UC = use_slice_UC, 
            corner1 = corner1, 
            corner2 = corner2, 
            subtract_box = True)

# Generate header and camera info
header = write_header_and_camera(device_dims=[nx, ny, nz], 
        camera_rotate=35, 
        isosurface=True)

fID = open(pov_name, 'w')
fID.write(header + mesh)
fID.close()

# Render
render_pov(pov_name, image_name, height, width, display,
    transparent, antialias, num_threads, open_png, render)

