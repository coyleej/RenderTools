# REFER TO THE FOLLOWING WHEN WRITING THIS:
# ~/Code/PovrayTools/write_POV.py
# ~/Code/S4Signac/device_init.json
# ~/Code/S4Signac/simulate.py
# example: http://wiki.povray.org/content/Documentation:Tutorial_Section_2#Basic_Shapes

from os import system
import signac
from util_pov import update_device_dims, guess_camera, color_and_finish
from util_pov import create_cylinder, create_ellipse, create_rectangle, create_polygon
from util import deep_access

""" Generates a .pov and optionally render an image for a single device """

# RECTANGLE
json_file = "DeviceFiles/Rectangles/device.index.json.gz"
device_id = "318a5dce269fc505ef665148c36a7677"

# CYLINDER
#json_file = "DeviceFiles/Cylinders/device.index.json.gz"
#device_id = "318a5dce269fc505ef665148c36a7677"

# ELLIPSE
#json_file = "DeviceFiles/Ellipse/device.index.json.gz"
#device_id = "318a5dce269fc505ef665148c36a7677"

# SILO
#json_file = "DeviceFiles/Silos/device.index.json.gz"
#device_id = "698bd2fc89cbb7439c2268a564569811"

#MOTHEYE
#json_file = "DeviceFiles/MothEye/device.index.json.gz"
#device_id = "12b881f6b38c677000cf1e85818a0332"     # original device
#device_id = "295ff62a2266c881b2bd83084cd8be43"      # my modified device

####################################################
pov_name = "temp.pov"
image_name = "render.png"

camera_loc = []
look_at = [0,0,0]
up_dir= [0,0,1]
right_dir= [0,1,0]
camera_angle = 45           # rotates camera around the z-axis
camera_style = "perspective"
# Currently only perspective is supported
# Full list of style options : perspective (default)| orthographic | fisheye |
#   ultra_wide_angle | omnimax | panoramic | cylinder CylinderType | spherical
#   for orthographic you might have to use e.g. "orthographic angle 30"
shadowless = False

bg_color = [1.0, 1.0, 1.0]
transparent = True
antialias = True 

height = 900
width = 1200

num_UC_x = 6
num_UC_y = 6

display = False
render = True
open_png = True

color = [[1, 0, 1], [0, 1, 1], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1]]
Si_color = [0.196, 0.298, 0.525]
SiO2_color = [1.0, 1.0, 0.96]

color_dict = {"subst": [0, 0, 0,6], "Si":[0.196, 0.298, 0.525], "SiO2":[0.99, 0.99, 0.93], "test":[1, 0, 1]}

# FILE INPUT/OUTPUT

with signac.Collection.open(json_file, compresslevel=1) as d_index:
    device_dict = list(d_index.find(filter={"_id": device_id}))[0]

fID = open(pov_name,'w')

# CREATE DEVICE

device_center = [0, 0]  # location in xy-plane
device_dims = [0, 0, 0] # maximum dimensions of the final device
                        # All components must be positive; update after adding each layer

device = ""             # stores the device
device += "#include \"colors.inc\"\n" \
        + "#include \"textures.inc\"\n"
# default include files are in /usr/share/povray-3.7/include/

# Lattice vectors
lattice_dict = deep_access(device_dict, ['statepoint', 'lattice_vecs'])
lattice_vecs = list()
for v in ['a', 'b']:
    tmp_vec = list()
    for i in ['x', 'y']:
        tmp_vec.append(deep_access(lattice_dict, [v, i]))
    lattice_vecs.append(tmp_vec)

# Zero layer
# currently no need to render anything from this layer
#background_0L = deep_access(device_dict, ["statepoint", "zero_layer", "background"])
#thickness_0L = deep_access(device_dict, ["statepoint", "zero_layer", "thickness"])

# Device layers
device += "#declare UnitCell = "
device += "merge\n\t{ob:c}\n\t".format(ob=123)
#device += "union\n\t{ob:c}\n\t".format(ob=123)

for i in range(deep_access(device_dict, ['statepoint', 'num_layers'])):
#    thickness = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'thickness'])

    if deep_access(device_dict, ['statepoint', 'dev_layers', str(i)]).get('shapes') is not None:
        shapes = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'shapes'])
        thickness = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'thickness'])

        print("layer ", str(i), "\nthickness ", thickness)

        # Determine shape(s) in layer
        # WARNING: CURRENTLY VERY RUDIMENTARY!
        # Will work on generalizing this later
        # For now, you must deal with it as is
        k = 0
        if len(shapes) == 1:
            #layer_type = deep_access(shapes, [str(k), 'shape'])
            if deep_access(shapes, [str(k), 'shape']) == "circle":
                layer_type = "cylinder"
            elif deep_access(shapes, [str(k), 'shape']) == "ellipse":
                layer_type = "ellipse"
            elif deep_access(shapes, [str(k), 'shape']) == "rectangle":
                layer_type = "rectangle"
            else:
                print("ERROR: This shape is not currently supported!")
        elif len(shapes) == 2:
            if deep_access(shapes, [str(k), 'material']) != "Vacuum" and \
                    deep_access(shapes, [str(k+1), 'material']) == "Vacuum": 
                layer_type = "silo"
            else:
                print("ERROR: This shape is not currently supported!")
        else:
            print("ERROR: This shape is not currently supported!")

        ######################

        if layer_type == "cylinder":
            material = deep_access(shapes, [str(k), 'material'])
            center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
            radius = deep_access(shapes, [str(k), 'shape_vars', 'radius'])
            end = [(-1.0 * device_dims[2]), (-1.0 * device_dims[2] - thickness)]

            device += create_cylinder(center, end, radius)
            device = color_and_finish(device, color_dict["test"], finish = "glass")

            device_dims = update_device_dims(device_dims, radius, radius, thickness)

        elif layer_type == "silo":
            # will need to be able to search ahead to use difference function for silos
            # a simple for loop will be incapable of generating silos
            material = deep_access(shapes, [str(k), 'material'])
            end = [(-1.0 * device_dims[2]), (-1.0 * device_dims[2] - thickness)]

            device += "difference \n\t\t{ob:c}\n\t\t".format(ob=123)

            # First shape
            if deep_access(shapes, [str(k), 'shape']) == "circle":
                center_0 = deep_access(shapes, [str(k), 'shape_vars', 'center'])
                radius_0 = deep_access(shapes, [str(k), 'shape_vars', 'radius'])
                device += create_cylinder(center_0, end, radius_0, for_silo=True)
            elif deep_access(shapes, [str(k), 'shape']) == "ellipse":
                print("WARNING: This function is not operational!!")
            elif deep_access(shapes, [str(k), 'shape']) == "rectangle":
                print("WARNING: create_rectangle function has not been tested!!")
            else:
                print("ERROR: This shape is not supported!!")

            # REQUIRED for the hole pass to through the ends of the first shape
            end = [(end[0] + 0.001), (end[1] - 0.001)]

            # Second shape (the hole)
            if deep_access(shapes, [str(k+1), 'shape']) == "circle":
                center_1 = deep_access(shapes, [str(k + 1), 'shape_vars', 'center'])
                radius_1 = deep_access(shapes, [str(k + 1), 'shape_vars', 'radius'])
                device += create_cylinder(center_1, end, radius_1, for_silo=True)
            elif deep_access(shapes, [str(k), 'shape']) == "ellipse":
                print("WARNING: This function is not operational!!")
            elif deep_access(shapes, [str(k), 'shape']) == "rectangle":
                print("WARNING: create_rectangle function has not been tested!!")
            else:
                print("ERROR: This shape is not supported!!")

            #device = color_and_finish(device, color[i], finish = "irid")
            #device = color_and_finish(device, color[i], finish = "glass")
            device = color_and_finish(device, color_dict["SiO2"], finish = "SiO2")

            device_dims = update_device_dims(device_dims, radius_0, radius_0, thickness)

        elif layer_type == "ellipse":
            material = deep_access(shapes, [str(k), 'material'])
            center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
            halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
            angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
            end = [(-1.0 * device_dims[2]), (-1.0 * device_dims[2] - thickness)]

            device += create_ellipse(center, end, halfwidths, angle)
            device = color_and_finish(device, color_dict["SiO2"], finish = "glass")

            device_dims = update_device_dims(device_dims, halfwidths[0], halfwidths[1], thickness)


        elif layer_type == "rectangle":
            material = deep_access(shapes, [str(k), 'material'])
            center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
            halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
            angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
            end = [(-1.0 * device_dims[2]), (-1.0 * device_dims[2] - thickness)]

            device += create_rectangle(center, end, halfwidths, angle)
            device = color_and_finish(device, color_dict["test"], finish = "irid")

            device_dims = update_device_dims(device_dims, halfwidths[0], halfwidths[1], thickness)

        else:
            print("\nWARNING: Invalid or unsupported layer specified.\n")

# Finish references:
#   ejcoyle@nyos: ~/Documents/Polyimide/PI-Cu100/render_atoms_at_interface.py
#   http://www.povray.org/documentation/view/3.6.0/79/
#   http://www.povray.org/documentation/view/3.6.1/230/
#   http://www.f-lohmueller.de/pov_tut/addon/00_Basic_Templates/10_Ready_made_scenes/__index.htm

# Substrate layer
thickness_sub = max(1, deep_access(device_dict, ['statepoint', 'sub_layer', 'thickness']))
background_sub = deep_access(device_dict, ['statepoint', 'sub_layer', 'background'])
halfwidth = [(0.5 * lattice_vecs[0][0]), (0.5 * lattice_vecs[1][1])]

color = [0, 0, 0.8]
#color = [0, 0, 0]

end_0 = [(-1.0 * device_dims[2]), (-1.0 * device_dims[2] - thickness_sub)]

device += "box\n\t\t{ob:c}\n\t\t".format(ob=123) \
        + "<{0}, {1}, {2}>\n\t\t".format((-1.0 * halfwidth[0]), (-1.0 * halfwidth[1]), end_0[0]) \
        + "<{0}, {1}, {2}>\n\t\t".format(halfwidth[0], halfwidth[1], end_0[1]) 

device = color_and_finish(device, color, finish = "dull")

device_dims = update_device_dims(device_dims, halfwidth[0], halfwidth[1], thickness_sub)

device += "{cb:c}\n\n".format(cb=125)

# Display one unit cell
# For just the one:
#device += "object {ob:c} UnitCell {cb:c}\n".format(ob=123, cb=125)

# For a bunch of them
device += "merge\n\t{ob:c} \n\t".format(ob=123)

# Shift translation so that the original device is roughly in the center
# subtracts 1 because one row stays at origin
# uses modulo to subtract again if odd number
# sends half of the remaining rows backward
adj_x = int(0.5 * (num_UC_x - (1 + (num_UC_x - 1) % 2)))
adj_y = int(0.5 * (num_UC_y - (1 + (num_UC_y - 1) % 2)))

for i in range(num_UC_x):
    for j in range(num_UC_y):
        device += "object {ob:c} UnitCell translate <{0}, {1}, {2}> {cb:c}\n\t".format( \
                ((i - adj_x) * lattice_vecs[0][0]), ((j - adj_y) * lattice_vecs[1][1]), 0, ob=123, cb=125)
                #(i * lattice_vecs[0][0]), (j * lattice_vecs[1][1]), 0, ob=123, cb=125)

device += "{cb:c}\n\n".format(cb=125)

device_dims = update_device_dims(device_dims, (num_UC_x * device_dims[0]), \
        (num_UC_y * device_dims[1]), device_dims[2])

## HEADER AND CAMERA INFO
if camera_loc == [] or look_at == [] or light_loc == []:
    camera_loc, look_at, light_loc = \
            guess_camera(device_dims, device_center, camera_style, angle = camera_angle)

if camera_style == "":
    camera_style = "perspective"
    print("Assumed camera_style : ", camera_style)

header = "#version 3.7;\n" 
header += "global_settings {ob:c} assumed_gamma 1.0 {cb:c}\n\n".format(ob=123, cb=125) 
header += "background {ob:c} ".format(ob=123) \
        + "color rgb <{0}, {1}, {2}> ".format(bg_color[0], bg_color[1], bg_color[2]) \
        + "{cb:c}\n\n".format(cb=125) \
        + "camera \n\t{ob:c}\n\t".format(ob=123) \
        + "{0}\n\t".format(camera_style) \
        + "location <{0}, {1}, {2}>\n\t".format(camera_loc[0], camera_loc[1], camera_loc[2])  \
        + "look_at <{0}, {1}, {2}>\n\t".format(look_at[0], look_at[1], look_at[2]) \
        + "up <{0}, {1}, {2}>\n\t".format(up_dir[0], up_dir[1], up_dir[2]) \
        + "right <{0}, {1}, {2}>\n\t".format(right_dir[0], right_dir[1], right_dir[2]) \
        + "sky <{0}, {1}, {2}>\n\t".format(up_dir[0], up_dir[1], up_dir[2]) \
        + "{cb:c}\n\n".format(cb=125)

if shadowless:
    header += "light_source \n\t{ob:c} \n\t".format(ob=123) \
            + "<{0}, {1}, {2}> \n\t".format(light_loc[0], light_loc[1], light_loc[2]) \
            + "color rgb <1.0,1.0,1.0> \n\t" \
            + "shadowless \n\t" \
            + "{cb:c}\n\n".format(cb=125)
else:
    header += "light_source \n\t{ob:c} \n\t".format(ob=123) \
            + "<{0}, {1}, {2}> \n\t".format(light_loc[0], light_loc[1], light_loc[2]) \
            + "color rgb <1.0,1.0,1.0> \n\t" \
            + "{cb:c}\n\n".format(cb=125)

# WRITE POV FILE
fID.write(header + device)
fID.close()

# RENDER
if render == True:
    command = "povray Input_File_Name={0} Output_File_Name={1} ".format(pov_name, image_name) \
            + "+H{0} +W{1}".format(height, width)

    if display:
        command += " Display=on"
    else:
        command += " Display=off"

    if transparent:
        command += " +ua" 

    if antialias:
        command += " +A"

    if open_png == True:
        command += " && eog {}".format(image_name)

    system(command)
    div = '------------------------------------------'
    print("write_POV: \n{0}\n{1}\n{0}".format(div,command))

