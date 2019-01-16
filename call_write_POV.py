import signac
#from util import deep_access
from rendering import write_pov

# RECTANGLE
#json_file = "DeviceFiles/Rectangles/device.index.json.gz"
#device_id = "318a5dce269fc505ef665148c36a7677"

# CYLINDER
#json_file = "DeviceFiles/Cylinders/device.index.json.gz"
#device_id = "318a5dce269fc505ef665148c36a7677"

# ELLIPSE
#json_file = "DeviceFiles/Ellipse/device.index.json.gz"
#device_id = "318a5dce269fc505ef665148c36a7677"

# SILO
json_file = "DeviceFiles/Silos/device.index.json.gz"
device_id = "698bd2fc89cbb7439c2268a564569811"

#MOTHEYE
#json_file = "DeviceFiles/MothEye/device.index.json.gz"
#device_id = "12b881f6b38c677000cf1e85818a0332"     # original device
#device_id = "295ff62a2266c881b2bd83084cd8be43"      # my modified device

# MISC
#json_file = "DeviceFiles/Test/device.index.json.gz"
#device_id = "698bd2fc89cbb7439c2268a564569811"
#device_id = "318a5dce269fc505ef665148c36a7677"

####################################################
pov_name = "temp.pov"
image_name = "render.png"

with signac.Collection.open(json_file, compresslevel=1) as d_index:
    device_dict = list(d_index.find(filter={"_id": device_id}))[0]

write_pov(device_dict, pov_name, image_name, \
        height = 800, width = 800, \
        num_UC_x = 15, num_UC_y = 15, \
        camera_style = "perspective", \
        camera_rotate = 45, ortho_angle = 30, \
        display = False, render = True, open_png = True)

