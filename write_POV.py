# REFER TO THE FOLLOWING WHEN WRITING THIS:
# ~/Code/PovrayTools/write_POV.py
# ~/Code/S4Signac/device_init.json
# ~/Code/S4Signac/simulate.json
# povray difference: http://wiki.povray.org/content/Reference:Difference
# example: http://wiki.povray.org/content/Documentation:Tutorial_Section_2#Basic_Shapes

from os import system
from copy import deepcopy
import signac
from util import update_device_dims, guess_camera, color_and_finish
from util import deep_access

""" Generates a .pov and optionally render an image for a single device """

sim_id = ""
hdf_fname = "workspace/{}.h5".format(sim_id)

pov_name = "temp.pov"
image_name = "render.png"

camera_loc = []
look_at = [0,0,0]
up_dir= [0,0,1]
right_dir= [0,1,0]
camera_angle = 45           # rotates camera around the z-axis
camera_style = "perspective"
# Camera style options are: perspective (default)| orthographic | fisheye |
#   ultra_wide_angle | omnimax | panoramic | cylinder CylinderType | spherical
#   for orthographic you might have to use e.g. "orthographic angle 30"
# Currently only perspective is supported
light_loc = [0,4,0]
light_at_camera = False
shadowless = False
write_lights = True

bg_color = [1,1,1]
transparent = True
antialias = False

height = 1024
width = 1024

display = False
render = True

# FILE INPUT/OUTPUT

fID = open(pov_name,'w')

#with signac.Collection.open(id_fname, compresslevel=1) as g_index:
#    sp = list(g_index.find(filter={"_id": sim_id}))[0]
#    device_id = deep_access(sp, ['statepoint', 'device_id'])
#    settings_id = deep_access(sp, ['statepoint', 'settings_id'])
#with signac.Collection.open("device.index.json.gz", compresslevel=1) as d_index:
#    device_dict = list(d_index.find(filter={"_id": device_id}))[0]

# WRITE SHAPES

device_center = [0, 0]
device_dims = [0, 0, 0]     # maximum dimensions of the final device
# All components of this should be positive; update after adding each layer

device = ""

# Zero layer
background_0L = "vacuum"

# Device layers
num_layers = 1
layer_type = ["rectangle", "rectangle", "silo", "cylinder"]

for i in range(len(layer_type)):
    color = [1, 0, 0]

    if layer_type[i] == "cylinder":
        thickness = 5
        material = "Si"
        shape_0 = "circle"
        radius_0 = 6
        center_0 = [0, 0]
        end_0 = [(-1.0 * device_dims[2]), (-1.0 * device_dims[2] - thickness)]

        if shape_0 == "circle":
            shape_0 = "cylinder"
            
        device += "{0} \n\t{ob:c} \n\t".format(shape_0, ob=123) \
                + "<{0}, {1}, {2}>, ".format(center_0[0], center_0[1], (end_0[0])) \
                + "<{0}, {1}, {2}>, ".format(center_0[0], center_0[1], end_0[1]) \
                + "{0}\n\t".format(radius_1)#, cb=125)

        device = color_and_finish(device, color, finish = "billiard")

        device_dims = update_device_dims(device_dims, radius_0, radius_0, thickness)

    elif layer_type[i] == "silo":
        # will need to be able to search ahead to use difference function for silos
        # a simple for loop will be incapable of generating silos
        thickness = 5
        material = "Si"
        shape_0 = "circle"
        radius_0 = 5
        center_0 = [0, 0]
        end_0 = [(-1.0 * device_dims[2]), (-1.0 * device_dims[2] - thickness)]

        material = "vacuum"
        shape_1 = "circle"
        radius_1 = 3
        center_1 = [0, 0]

        if shape_0 == "circle":
            shape_0 = "cylinder"

        if shape_1 == "circle":
            shape_1 = "cylinder"

        device += "difference \n\t{ob:c}\n\t".format(ob=123)
        device += "{0} {ob:c} ".format(shape_0, ob=123) \
                + "<{0}, {1}, {2}>, ".format(center_0[0], center_0[1], end_0[0]) \
                + "<{0}, {1}, {2}>, ".format(center_0[0], center_0[1], end_0[1]) \
                + "{0} {cb:c}\n\t".format(radius_0, cb=125)
        device += "{0} {ob:c} ".format(shape_0, ob=123) \
                + "<{0}, {1}, {2}>, ".format(center_0[0], center_0[1], (end_0[0] + 0.01)) \
                + "<{0}, {1}, {2}>, ".format(center_0[0], center_0[1], end_0[1]) \
                + "{0} {cb:c}\n\t".format(radius_1, cb=125)

        device = color_and_finish(device, color, finish = "irid")

        device_dims = update_device_dims(device_dims, radius_0, radius_0, thickness)

    elif layer_type[i] == "ellipse":
        thickness = 5
        material = "Si"
        shape_0 = ""

    elif layer_type[i] == "rectangle":
        thickness = 5
        material = "Si"
        shape_0 = "rectangle"
        halfwidth = [3, 1]
        end_0 = [(-1.0 * device_dims[2]), (-1.0 * device_dims[2] - thickness)]

        device += "box\n\t{ob:c}\n\t".format(ob=123) \
            + "<{0}, {1}, {2}>\n\t".format( (-1 * halfwidth[0]), (-1 * halfwidth[1]), end_0[0] ) \
            + "<{0}, {1}, {2}>\n\t".format( halfwidth[0], halfwidth[1], end_0[1] )

        device = color_and_finish(device, color, finish = "glass")

        device_dims = update_device_dims(device_dims, halfwidth[0], halfwidth[1], thickness)

    else:
        print("\nWARNING: Invalid or unsupported layer specified.\n")

# Finish reference: ejcoyle@nyos: ~/Documents/Polyimide/PI-Cu100/render_atoms_at_interface.py


# Substrate layer
#lattice_dict = deep_access(device_dict, ['statepoint', 'lattice_vecs'])
#lattice_vecs = list()
#for v in ['a', 'b']0:
#    tmp_vec = list()
#    for i in ['x', 'y']:
#        tmp_vec.append(deep_access(lattice_dict, [v, i]))
#    lattice_vecs.append(tmp_vec)
thickness_sub = 3
background_sub = "Si"
L_vecs = [[18, 0], [0, 18]]

color = [0, 0, 1]

end_0 = [(-1.0 * device_dims[2]), (-1.0 * device_dims[2] - thickness_sub)]

device += "box\n\t{ob:c}\n\t".format(ob=123) \
        + "<{0}, {1}, {2}>\n\t".format( (-0.5 * L_vecs[0][0]), (-0.5 * L_vecs[1][1]), end_0[0] ) \
        + "<{0}, {1}, {2}>\n\t".format( (0.5 * L_vecs[0][0]), (0.5 * L_vecs[1][1]), end_0[1] ) 
#        + "pigment {ob:c} ".format(ob=123) \
#        + "color rgb <{0}, {1}, {2}>".format(color[0], color[1], color[2]) \
#        + "{cb:c}\n\t{cb:c}\n\n".format(cb=125)
device = color_and_finish(device, color, finish = "metal")

device_dims = update_device_dims(device_dims, radius_0, radius_0, thickness_sub)

print(device)

## HEADER AND CAMERA INFO
if camera_loc == []:
    camera_loc, look_at, light_loc = guess_camera(device_dims, device_center, camera_style, angle = camera_angle)

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
        + " right <{0}, {1}, {2}>\n".format(right_dir[0], right_dir[1], right_dir[2]) \
        + "sky <{0}, {1}, {2}>\n\t".format(up_dir[0], up_dir[1], up_dir[2]) \
        + "{cb:c}\n\n".format(cb=125)
#        + "{cb:c}\n\n".format(cb=125)


if write_lights:
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

    if light_at_camera == True:
        if shadowless:
            header += "light_source \n\t{ob:c}\n\t".format(ob=123) \
                    + "<{0}, {1}, {2}> \n\t".format(camera_loc[0], camera_loc[1], camera_loc[2]) \
                    + "color rgb <0.75,0.75,0.75> \n\t" \
                    + "shadowless \n\t" \
                    + "{cb:c}\n\n".format(cb=125)
        else:
            header += "light_source \n\t{ob:c}\n\t".format(ob=123) \
                    + "<{0}, {1}, {2}> \n\t".format(camera_loc[0], camera_loc[1], camera_loc[2]) \
                    + "color rgb <0.75,0.75,0.75> \n\t" \
                    + "{cb:c}\n\n".format(cb=125)

# WRITE POV FILE
fID.write(header + device)
fID.close()

# RENDER
if render == True:
    command = "povray Input_File_Name=%s Output_File_Name=%s +H%i +W%i" % (pov_name, image_name, height, width)

    if display:
        command += " Display=on"
    else:
        command += " Display=off"

    if transparent:
        command += " +ua" 

    if antialias:
        command += " +A"

    system(command)
    div = '------------------------------------------'
    print("write_POV: \n{0}\n{1}\n{0}".format(div,command))

    system("eog {}".format(image_name) )
