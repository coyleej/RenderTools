import signac
from rendering import write_pov
#from rendering_ortho_only import write_pov
from os import system

# RECTANGLE
#json_file = "DeviceFiles/Rectangles/device.index.json.gz"
#device_id = "318a5dce269fc505ef665148c36a7677"

# CYLINDER
#json_file = "DeviceFiles/Cylinders/device.index.json.gz"
#device_id = "318a5dce269fc505ef665148c36a7677"
#device_id = "27e5abfcc1ac54f500b8c4dcdf2c64d3"      # device render for Eric
#device_id = "36ad443c99e81cfad04472861742cb8a"      # device for JV
#device_id = "a0ee6d635d581f6157393ba05eb81724"      # test for dimensions of zero (false silos)

# HEX
#json_file = "DeviceFiles/Hex/device.index.json.gz"
#device_id = "318a5dce269fc505ef665148c36a7677"

# ELLIPSE
#json_file = "DeviceFiles/Ellipse/device.index.json.gz"
#device_id = "318a5dce269fc505ef665148c36a7677"

# SILO
#json_file = "DeviceFiles/Silos/device.index.json.gz"
#device_id = "698bd2fc89cbb7439c2268a564569811"
#device_id = "ba263aa69972dfe6815121e83a28c923"      # device render for Eric
#device_id = "df27644a2bd4abae1eaddbcd8210428c"      # device for JV

#MOTHEYE
json_file = "DeviceFiles/MothEye/device.index.json.gz"
device_id = "12b881f6b38c677000cf1e85818a0332"      # original device
#device_id = "295ff62a2266c881b2bd83084cd8be43"      # my modified device

# MISC
json_file = "DeviceFiles/Test/device.index.json.gz"
device_id = "698bd2fc89cbb7439c2268a564569811"
#device_id = "318a5dce269fc505ef665148c36a7677"

####################################################

name = "hex_test"

pov_name = name + ".pov"
image_name = name + ".png"

height = 800
num_UC = 5

# Open device dictionary
with signac.Collection.open(json_file, compresslevel=1) as d_index:
    device_dict = list(d_index.find(filter={"_id": device_id}))[0]
#print(device_dict)

extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
        + "emission 0.2 \n\t\t\t" \
        + "diffuse 0.3 \n\t\t\t" \
        + "specular 0.8 \n\t\t\t" \
        + "roughness 0.01 \n\t\t\t" \
        + "reflection <0, 0, 1>  metallic \n\t\t\t" \
        + " metallic \n\t\t\t" \
        + "{cb:c}\n\t\t".format(cb=125)

custom_colors = [
        [1, 1, 1],
        [0.212, 0.211, 0.835],
        [0.000, 0.000, 1.000], 
        [1.000, 0.000, 0.000]
        ]

# Starts at bottom coating layer and builds up (micrometers)
# [material_name, thickness]
#extra_coatings = [
#        ["coating1", 0.308],
#        ["coating3", 0.130]]

extra_coatings = [ ]
#        ["coating1", 0.01824],
#        ["coating2", 0.04277],
#        ["coating1", 0.02885],
#        ["coating2", 0.04662],
#        ["coating1", 0.02885],
#        ["coating2", 0.04662],
#        ["coating1", 0.02885],
#        ["coating2", 0.05224],
#        ["coating1", 0.01557],
#        ["coating3", 0.130]]

# Coating color and ior definitions
bg_coating_ior_dict = { 
        "coating1":1.20,
        "coating2":1.50,
        "coating3":1.40}

bg_coating_color_dict = { 
        "coating1":[1.0, 0.1, 0.1, 0, 0],
        "coating2":[0.1, 1.0, 0.1, 0, 0],
        "coating3":[0.1, 0.1, 1.0, 0, 0]}

write_pov(device_dict, pov_name, image_name, 
        height = height, width = height, 
        num_UC_x = num_UC, num_UC_y = num_UC, 
        camera_style = "perspective", 
        camera_rotate = 60, ortho_angle = 30, 
        coating_layers = extra_coatings, 
        coating_color_dict = bg_coating_color_dict,
        coating_ior_dict = bg_coating_ior_dict,
        use_default_colors = False, custom_colors = custom_colors, 
        use_finish = "dull", custom_finish = extra_finish, 
        display = False, render = True , num_threads = 3, 
        open_png = True)
