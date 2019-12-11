#!/bin/bash

from util_field import process_field_array, double_roll, extract_components
from util_field import extract_e_field, extract_h_field, extract_real_components
from util_field import calc_field_mag, calc_energy_density

from util import deep_access
from util_iso import create_mesh2, slice_isosurface
from util_pov import write_header_and_camera, render_pov
from util_shapes import create_device_layer

import signac

import numpy as np
from numpy.fft import fftn
from skimage.measure import marching_cubes_lewiner
from os import system
import pylab

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
colormap = "Greys"
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
height = 1800
width = height
pov_name = "mesh_test.pov"
image_name = "mesh_test.png"
display = False
transparent = True
antialias = True
num_threads = 4
open_png = True
render = True


#############################
#### Isosurface creation ####
#############################

# Generate povray mesh2 string09
#create_mesh2(field, cutoffs, colormap = "viridis", transmit = 0.3, cmap_limits = ["a","b"])
mesh = create_mesh2(field=e_mag, cutoffs = cutoffs, colormap = colormap, cmap_limits = cmap_limits)

# Use a box to slice the isosurface
# Modifies the mesh string to make it happen
if use_slice == True:
    mesh = slice_isosurface(mesh, corner1, corner2, subtract_box = subtract_box)


##########################
#### Render unit cell ####
##########################

if add_unit_cell == True:
    # Open device dictionary
    with signac.Collection.open(json_file, compresslevel=1) as d_index:
        device_dict = list(d_index.find(filter={"_id": device_id}))[0]

    default_color_dict = {
            "subst": [0.25, 0.25, 0.25, 0, UC_transmit],
            "Si": [0.25, 0.25, 0.25, 0, UC_transmit],
            "SiO2": [0.25, 0.25, 0.25, 0, UC_transmit]
            }

    number_of_layers = deep_access(device_dict, ['statepoint', 'num_layers'])

    # Counter for incrementing through colors
    c = 0
    # Track dimensions of the unit cell
    device_dims = [0, 0, 0]
    # Track coating layer thickness
    coating_dims = [0, 0, 0]
    # Store device
    device = "// Unit cell"

    # Lattice vectors
    lattice_dict = deep_access(device_dict, ['statepoint', 'lattice_vecs'])
    lattice_vecs = list()
    for v in ['a', 'b']:
        tmp_vec = list()
        for i in ['x', 'y']:
            tmp_vec.append(deep_access(lattice_dict, [v, i]))
        lattice_vecs.append(tmp_vec)

    # Begin unit cell merge
    # Necessary if multiple layers or multiple features per layer
    device = "\n\n#declare UnitCell = "
    device += "merge {ob:c}\n\t".format(ob=123)

    # Create all layers
    for i in range(number_of_layers):

        if deep_access(device_dict, ['statepoint', 'dev_layers', str(i)]).get('shapes') is not None:
            shapes = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'shapes'])
            background = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'background'])
            thickness = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'thickness'])
            # end = [top, bottom]
            end = [float(-1.0 * device_dims[2]), float(-1.0 * device_dims[2] - thickness)]

            device += "union\n\t{ob:c}\n\t".format(ob=123)

            # Create all features within a layer
            layer, c, device_dims = create_device_layer(shapes, device_dims,
                    end, thickness, default_color_dict, 
                    use_default_colors = True, custom_colors = [], c = c, 
                    use_finish = "dull", custom_finish = [], add_lines = [])
            device += layer

    # End unit cell merge
    device += "{cb:c}\n\n".format(cb=125)

    # Scale unit cell up to match field dimensions
    scaling_factor = nx / lattice_vecs[0][0]

    device += "object {ob:c} UnitCell ".format(ob=123)
    device += "\n\tscale <{0}, {0}, {0}> ".format(scaling_factor)
    device += "\n\ttranslate <{0}, ".format(0.5 * (device_dims[0] + nx))
    device += "{0}, ".format(0.5 * (device_dims[1] + ny))
    device += "{0}> \n\t{cb:c}\n\n".format(nz - device_dims[2], cb=125)

    # Can also subtract out pieces of the unit cell, 
    if use_slice_UC == True:
        device = slice_isosurface(device, corner1, corner2, subtract_box = subtract_box_UC)

    mesh += device

# Write to file
if True:
    fID = open("mesh_object.pov", 'w')
    fID.write(mesh)
    fID.close()

###########################
#### Render isosurface ####
###########################

# RENDERING
# Add camera, as written it will guess location
header = write_header_and_camera([nx, ny, nz], camera_rotate = 35, isosurface=True)
mesh = header + mesh

# Write to file
if True:
    fID = open(pov_name, 'w')
    fID.write(mesh)
    fID.close()

# Render
render_pov(pov_name, image_name, height, width, display,
    transparent, antialias, num_threads, open_png, render)

