import signac
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
#json_file = "DeviceFiles/Silos/device.index.json.gz"
#device_id = "698bd2fc89cbb7439c2268a564569811"

#MOTHEYE
#json_file = "DeviceFiles/MothEye/device.index.json.gz"
#device_id = "12b881f6b38c677000cf1e85818a0332"     # original device
#device_id = "295ff62a2266c881b2bd83084cd8be43"      # my modified device

# MISC
json_file = "DeviceFiles/Test/device.index.json.gz"
device_id = "698bd2fc89cbb7439c2268a564569811"
#device_id = "318a5dce269fc505ef665148c36a7677"

####################################################
pov_name = "temp.pov"
image_name = "render.png"

with signac.Collection.open(json_file, compresslevel=1) as d_index:
    device_dict = list(d_index.find(filter={"_id": device_id}))[0]




extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
        + "metallic 0.5 \n\t\t\t" \
        + "{cb:c}\n\t\t".format(cb=125)



write_pov(device_dict, pov_name, image_name, \
        height = 1000, width = 1000, \
        num_UC_x = 3, num_UC_y = 3, \
        camera_style = "perspective", \
        camera_rotate = 45, ortho_angle = 30, \
        use_default_colors = True , custom_color = [0, 0.667, 0.667], \
        use_finish = "material", custom_finish = extra_finish, \
        display = False, render = True, open_png = True)

