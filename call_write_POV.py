import signac
from rendering import write_pov
from os import system

# RECTANGLE
json_file = "DeviceFiles/Rectangles/device.index.json.gz"
device_id = "318a5dce269fc505ef665148c36a7677"

# CYLINDER
#json_file = "DeviceFiles/Cylinders/device.index.json.gz"
#device_id = "318a5dce269fc505ef665148c36a7677"
#device_id = "27e5abfcc1ac54f500b8c4dcdf2c64d3"      # device render for Eric
#device_id = "36ad443c99e81cfad04472861742cb8a"      # device for JV
#device_id = "a0ee6d635d581f6157393ba05eb81724"      # test for dimensions of zero (false silos)
#device_id = "1551fb029499a0c37d654e7da3da0957"  # Optica Fig 2a (modes)

# HEX
json_file = "DeviceFiles/Hex/device.index.json.gz"
device_id = "318a5dce269fc505ef665148c36a7677"     # cylinder
#device_id = "12b881f6b38c677000cf1e85818a0332"      # motheye, original device
#device_id = "698bd2fc89cbb7439c2268a564569811"     # misc

# ELLIPSE
#json_file = "DeviceFiles/Ellipse/device.index.json.gz"
#device_id = "318a5dce269fc505ef665148c36a7677"

# SILO
#json_file = "DeviceFiles/Silos/device.index.json.gz"
##device_id = "698bd2fc89cbb7439c2268a564569811"
##device_id = "ba263aa69972dfe6815121e83a28c923"      # device render for Eric
##device_id = "df27644a2bd4abae1eaddbcd8210428c"      # device for JV
#device_id = "4c74bbb6504dd1f16ea80ee8f5f61c2d"  # Optica Fig 1  (schematic)
#device_id = "479c5d573f2cf86128785ed5d6aa352a"  # Optica Fig 2b (modes)
#device_id = "437f653dd25dd99f9f54dc1081c9838e"  # Optica Fig 3a
#device_id = "3a0a1f83fbe9f5e82d69b57967d9216c"  # Optica Fig 3b (hex)
#device_id = "08dd6608e15a264449c78353509083d2"  # Optica Fig 3c
#device_id = "9ee095d902088fdee601633897986842"  # Optica Fig 3d (hex)


#MOTHEYE
#json_file = "DeviceFiles/MothEye/device.index.json.gz"
#device_id = "12b881f6b38c677000cf1e85818a0332"      # original device
#device_id = "295ff62a2266c881b2bd83084cd8be43"      # my modified device

# MISC
#json_file = "DeviceFiles/Test/device.index.json.gz"
#device_id = "698bd2fc89cbb7439c2268a564569811"
#device_id = "318a5dce269fc505ef665148c36a7677"

####################################################

name = "test_3x3"
#name = "test_add_lines"

pov_name = name + ".pov"
image_name = name + ".png"

height = 2000
num_UC = 3

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
##        [0.765, 0.217, 0.580], 
##        [0.000, 0.267, 1.000], 
##        [1, 1, 1],
##        [1.000, 0.196, 0.196],
##        [1, 1, 1],
##        [1.000, 0.196, 0.196]
#        [1.000, 0.196, 0.196],
#        [1.000, 0.749, 0.000],
        [0.016, 0.494, 0.160],
        [0.024, 0.678, 1.000],
        [0.765, 0.217, 0.580] 
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

# Optica square lattice setting (side view)s
#        camera_loc = [2.0, 3.6, 3.4444],
#        camera_style = "perspective", 
#        look_at = [], 
#        light_loc = [3.5, 4.5, 3.75],
#        shadowless = False,
# Optica hex lattice settings (side view)
#        camera_style = "perspective", 
#        camera_loc = [1.75, 3.2, 3.4444],
#        look_at = [], 
#        light_loc = [3.5, 3.9, 3.75],
#        shadowless = False,
# Optica top down view
#        camera_loc = [0, 0, 3.4444],
#        camera_style = "orthographic", 
#        ortho_angle = 30,
#        look_at = [], 
#        light_loc = [3.5, 4.5, 3.75],
#        shadowless = False,


write_pov(device_dict, pov_name, image_name, 
        height = height, width = height, 
        num_UC_x = num_UC, num_UC_y = num_UC, 
        camera_style = "perspective", 
        camera_rotate = 60, 
        ortho_angle = 30, 
        camera_loc = [],
        shadowless = False,
        look_at = [], 
        light_loc = [],
        coating_layers = extra_coatings, 
        coating_color_dict = bg_coating_color_dict,
        coating_ior_dict = bg_coating_ior_dict,
        use_default_colors = False, custom_colors = custom_colors, 
        use_finish = "billiard", custom_finish = extra_finish, 
        add_lines = True,
        display = False, render = True , num_threads = 3, 
        open_png = True)
