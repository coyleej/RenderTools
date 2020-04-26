import signac
from util_shapes import create_device
from util_pov import write_header_and_camera, render_pov
from os import system

# RECTANGLE
#json_file = "DeviceFiles/Rectangles/device.index.json.gz"
#device_id = "318a5dce269fc505ef665148c36a7677"

# CYLINDER
json_file = "DeviceFiles/Cylinders/device.index.json.gz"
device_id = "318a5dce269fc505ef665148c36a7677"

# HEX
#json_file = "DeviceFiles/Hex/device.index.json.gz"
#device_id = "318a5dce269fc505ef665148c36a7677"

# ELLIPSE
#json_file = "DeviceFiles/Ellipse/device.index.json.gz"
#device_id = "318a5dce269fc505ef665148c36a7677"

# SILO
#json_file = "DeviceFiles/Silos/device.index.json.gz"
#device_id = "437f653dd25dd99f9f54dc1081c9838e"

# POLYGON
#json_file = "DeviceFiles/device_batman/device.index.json.gz"
#device_id = "1fdbcb094cd9fd4a1a39d63ca957c988"

# MOTHEYE
json_file = "DeviceFiles/MothEye/device.index.json.gz"
device_id = "12b881f6b38c677000cf1e85818a0332"      # original device

####################################################

name = "test_3x3"

pov_name = name + ".pov"
image_name = name + ".png"

height = 600
width = height
num_UC = 3

# Open device dictionary
with signac.Collection.open(json_file, compresslevel=1) as d_index:
    device_dict = list(d_index.find(filter={"_id": device_id}))[0]
#print(device_dict)

extra_finish = (f"finish \n\t\t\t{{ \n\t\t\t"
        + "emission 0.2 \n\t\t\t"
        + "diffuse 0.3 \n\t\t\t"
        + "specular 0.8 \n\t\t\t"
        + "roughness 0.01 \n\t\t\t"
        + "reflection <0, 0, 1>  metallic \n\t\t\t"
        + " metallic \n\t\t\t"
        + f"}}\n\t\t")

# Starts at bottom coating layer and builds up (micrometers)
# [material_name, thickness]
extra_coatings = [  ]
#        ["coating1", 0.308],
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

# Render things #

# Create device string and output the device dimensions
#device, device_dims, coating_dims = write_pov(device_dict, 
device, device_dims, coating_dims = create_device(
        device_dict, 
        feature_color_finish=[[[0, 0.6667, 0.667, 0, 0], "dull"]],
        num_UC_x = num_UC, 
        num_UC_y = num_UC, 
        coating_layers = extra_coatings, 
        coating_color_dict = bg_coating_color_dict,
        coating_ior_dict = bg_coating_ior_dict,
        add_lines = True,
        line_color = [1,1,1],
        line_thickness = 0.0020)
#        custom_finish = extra_finish, 

# Generate a header with the camera and lighting information
header = write_header_and_camera(device_dims,
        coating_dims = coating_dims, 
        camera_style = "perspective",
        ortho_angle = 30, 
        camera_rotate = 60, 
        camera_options = "",
        camera_loc = [], 
        look_at = [], 
        light_loc = [],
        up_dir = [0, 0, 1], 
        right_dir = [0, 1, 0], 
        sky = [0, 0, 1.33],
        bg_color = [], 
        shadowless = False)

fID = open(pov_name,'w')
fID.write(header + device)
fID.close()

# Render the device
render_pov(pov_name, image_name, height, width, 
        display = True, 
        transparent = True, 
        antialias = True, 
        num_threads = 3, 
        open_png = True, 
        render = True,
        render_quality = 7
        )

