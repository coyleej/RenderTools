import signac
from rendering import write_pov
from util_pov import guess_camera
from os import system

# RECTANGLE
#json_file = "DeviceFiles/Rectangles/device.index.json.gz"

# CYLINDER
#json_file = "DeviceFiles/Cylinders/device.index.json.gz"

# ELLIPSE
#json_file = "DeviceFiles/Ellipse/device.index.json.gz"

# SILO
json_file = "DeviceFiles/Silos/device.index.json.gz"

#MOTHEYE
#json_file = "DeviceFiles/MothEye/device.index.json.gz"

# MISC
#json_file = "DeviceFiles/Test/device.index.json.gz"

####################################################
output_dir = "silo_test"
gif_name = "result.gif"
open_gif = True 
make_gif = True

# GIF settings:
# Number of times to loop before stopping (0 = never stop)
num_loop = 0
# Pause between animation frames
delay_time = 40
# Negate image (creates negative by replacing with complimentary color)
negate = False

#dirname="Devices"; if [ ! -d $dirname ]; then echo "True" && mkdir ${dirname}; fi
command = "if [ ! -d {0:s} ]; then mkdir -p {0:s}; fi".format(output_dir)
print(command)
system(command)

limit = 15       #  number of data points to load

height = 600
num_UC = 4

# List of IDs doesn't always have the same order!
# For actual application, the user must feed in their own list of
# device names. This is just for testing
with signac.Collection.open(json_file, compresslevel=1) as d_index:
    id_list = [doc.get("_id") for doc in d_index.find(limit=limit)]

#print(id_list)

# Guess camera, so that all images use the same camera settings
#
# NEED TO ADD THIS!!
# camera_position, camera_look_at, light_position
#
camera_loc = [2.8, 4.5, 2.9]
camera_look_at = [0, 0, -2]
light_loc = [4.2, 4.4, 4]
# cat *pov | grep location | sed -e "s/, / /g" -e "s/ </ /" -e "s/>/ /" | cut -d " " -f 2,3,4 | tee gif_camera_info.txt 

extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
        + "emission 0.2 \n\t\t\t" \
        + "diffuse 0.3 \n\t\t\t" \
        + "specular 0.8 \n\t\t\t" \
        + "roughness 0.01 \n\t\t\t" \
        + "reflection <0, 0, 1>  metallic \n\t\t\t" \
        + " metallic \n\t\t\t" \
        + "{cb:c}\n\t\t".format(cb=125)

custom_colors = [
#        [1.000, 0.000, 0.000],
#        [1.000, 0.506, 0.000], 
#        [1.000, 0.957, 0.000], 
#        [0.027, 0.824, 0.804], 
#        [0.024, 0.678, 1.000], 
        [0.212, 0.211, 0.835],
        [0.000, 0.000, 1.000], 
        [1.000, 0.000, 0.000]
        ]

#if pov_name:
for i in range(len(id_list)):
    device_id = id_list[i]

    with signac.Collection.open(json_file, compresslevel=1) as d_index:
        device_dict = list(d_index.find(filter={"_id": device_id}))[0]


    pov_name = output_dir + "/{:03d}.pov".format(i + 1)
    image_name = output_dir + "/{:03d}.png".format(i + 1)
    #print(device_dict)

    write_pov(device_dict, pov_name, image_name, 
            height = height, width = height, 
            num_UC_x = num_UC, num_UC_y = num_UC, 
            camera_style = "perspective", 
            camera_rotate = 60, ortho_angle = 30, 
            camera_loc = camera_loc,
            look_at = camera_look_at,
            light_loc = light_loc,
            add_edge_buffer = False, 
            use_default_colors = False, custom_colors = custom_colors, 
            use_finish = "dull", custom_finish = extra_finish, 
            display = False, render = True , num_threads = 2,
            open_png = False)

    #print("{:03d}".format(i + 1))

command = "cd {0:s}; convert ".format(output_dir)
command += "-delay {0} -loop {1} ".format(delay_time, num_loop)
if negate:
    command += "-negate "
command += "*.png {0:s}".format(gif_name)

if open_gif == True:
    command += "; eog {0:s}".format(gif_name)

if make_gif == True:
    system(command)
