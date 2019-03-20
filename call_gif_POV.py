import signac
from rendering import write_pov
from os import system

##### File info #####
json_file = "DeviceFiles/Eric_poster/device.index.json.gz"
output_dir = "Poster/"
gif_name = "devices.gif"

##### Render settings #####
height = 300
# width = height #in function call

# All have the same camera information
camera_loc = [3.5, 6.5, 4.0]
camera_look_at = [0, 0, -2]
light_loc = [5.9, 6.6, 5.7]
# cat *pov | grep location | sed -e "s/, / /g" -e "s/ </ /" -e "s/>/ /" | cut -d " " -f 2,3,4 | tee gif_camera_info.txt

device_list = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]

num_UC = [20, 18, 16, 14, 12, 10, 9, 8, 24, 20, 20]

custom_colors = [
        [0.12156862745098, 0.466666666666667, 0.705882352941176], 
        [1, 0.498039215686275, 0.054901960784314], 
        [0.83921568627451, 0.152941176470588, 0.156862745098039], 
        [0.172549019607843, 0.627450980392157, 0.172549019607843], 
        [0.549019607843137, 0.337254901960784, 0.294117647058824], 
        [0.580392156862745, 0.403921568627451, 0.741176470588235], 
        [0.090196078431373, 0.745098039215686, 0.811764705882353], 
        [0.737254901960784, 0.741176470588235, 0.133333333333333], 
        [0.83921568627451, 0.152941176470588, 0.156862745098039], 
        [0.12156862745098, 0.466666666666667, 0.705882352941176], 
        [0.12156862745098, 0.466666666666667, 0.705882352941176]
        ]

##### Gif settings #####
make_gif = True 
open_gif = True

# GIF settings:
# Number of times to loop before stopping (0 = never stop)
num_loop = 0
# Pause between animation frames
delay_time = 40
# Negate image (creates negative by replacing with complimentary color)
negate = False

##### Renders stuff #####
for i in range(len(device_list)):
    device_id = device_list[i]

    pov_name = output_dir + device_list[i] + ".pov"
    image_name = output_dir + device_list[i] + ".png"

    # Open device dictionary
    with signac.Collection.open(json_file, compresslevel=1) as d_index:
        device_dict = list(d_index.find(filter={"_id": device_id}))[0]

    extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
            + "emission 0.2 \n\t\t\t" \
            + "diffuse 0.3 \n\t\t\t" \
            + "specular 0.8 \n\t\t\t" \
            + "roughness 0.01 \n\t\t\t" \
            + "reflection <0, 0, 1>  metallic \n\t\t\t" \
            + " metallic \n\t\t\t" \
            + "{cb:c}\n\t\t".format(cb=125)

    # The brackets around custom_colors[i] are required here because 
    # write_pov expects [[], [], ...], but we're only passing in one color.
    write_pov(device_dict, pov_name, image_name, 
            height = height, width = height, 
            num_UC_x = num_UC[i], num_UC_y = num_UC[i], 
            camera_style = "perspective", 
            camera_rotate = 60, ortho_angle = 30, 
            camera_loc = camera_loc,
            look_at = camera_look_at, 
            light_loc = light_loc, 
            add_edge_buffer = False, 
            use_default_colors = False, custom_colors = [custom_colors[i]], 
            use_finish = "dull", custom_finish = extra_finish, 
            display = False, render = True , num_threads = 3, 
            open_png = False)

##### Gif #####
command = "cd {0:s}; convert ".format(output_dir)
command += "-delay {0} -loop {1} ".format(delay_time, num_loop)
if negate:
    command += "-negate "
command += "*.png {0:s}".format(gif_name)

if open_gif == True:
    command += "; eog {0:s}".format(gif_name)

if make_gif == True:
    system(command)

print("All done :)")
