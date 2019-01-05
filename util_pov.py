#### ---- NEW FUNCTIONS ---- ####

def create_cylinder(center, end, radius, for_silo=False):
    cyl_string = "cylinder {ob:c} ".format(ob=123) \
            + "<{0}, {1}, {2}>, ".format(center[0], center[1], end[0]) \
            + "<{0}, {1}, {2}>, ".format(center[0], center[1], end[1]) 
    if for_silo:
        cyl_string += "{0} {cb:c}\n\t\t".format(radius, cb=125)
    else:
        cyl_string += "{0}\n\t\t".format(radius)
    return cyl_string

def create_rectangle(center, end, halfwidth, for_silo=False):
    print("WARNING: create_rectangle function has not been tested!!")
    rect_string = "box\n\t\t{ob:c}\n\t\t".format(ob=123) \
            + "<{0}, ".format(center[0] - halfwidth[0]) \
            + "{0}, {1}>\n\t\t".format((center[1] - halfwidth[1]), end[0]) \
            + "<{0} ".format(center[0] + halfwidth[0]) \
            + "{0}, {1}>\n\t\t".format((center[1] + halfwidth[1]), end[1])
    if for_silo:
        rect_string += "{cb:c}\n\t\t".format(cb=125)
    return rect_string

def update_device_dims(device_dims, new_x, new_y, new_z):
    """ tracks overall device dimensions to aid in guessing camera placement"""
    device_dims[0] = max(new_x, device_dims[0])
    device_dims[1] = max(new_y, device_dims[1])
    #device_dims[2] = max(new_z, device_dims[2])
    device_dims[2] += new_z
    return device_dims

def guess_camera(device_dims, center, camera_style="perspective", angle=0):
    """ This is a guess that assumes you have no idea what the camera position is.
    Can look at the device from the side (straight down the x-axis; default)
    or at an angle in the xy-plane (rotate around z-axis, *DEGREES* from x-axis). """
    from math import sin, cos, pi

    camera_position = [0,0,0]
    light_position = [0, 0, 0]

    deg_to_rads = pi / 180.0
    angle = deg_to_rads * angle  # to radians!

    if camera_style == "perspective":
        x_offset = 1.2
    else:
        x_offset = 1.2
        print("WARNING: Camera parameters have not been optimized for this style!")

    camera_offset = x_offset * max(device_dims) 

    camera_position[0] = (camera_offset + device_dims[0]) * cos(angle)
    camera_position[1] = (camera_offset + device_dims[0]) * sin(angle)
    camera_position[2] = 0.5 * (device_dims[2])            # was 0.4
    camera_look_at = [center[0], center[1], (-0.66 * device_dims[2])]

    light_offset = camera_offset * 1.25 #* 4.0/3.0
    light_position[0] = (device_dims[0] + light_offset) * cos(angle - 10 * deg_to_rads)
    light_position[1] = (device_dims[1] + light_offset/1.0) * sin(angle - 10 * deg_to_rads)
    #light_position[2] = device_dims[2] + light_offset/3.0
    light_position[2] = camera_position[2] + light_offset/3.0

    print("Write_POV estimated camera parameters:")
    print("camera_position : " , camera_position)
    print("camera_look_at : ", camera_look_at)

    return camera_position, camera_look_at, light_position

def color_and_finish(dev_string, color, filter_ = 0, transmit = 0, finish = "dull"):
    """ Sets the color and transmission of the object and adds to the string.
    The filter and transmit terms are both 0 by default.
    Do not remove the underscore from filter_, as filter is a function in python.
    Reference explaining rgbft:
    http://www.povray.org/documentation/view/3.6.1/230/ 
    POVRay finish examples:
    http://www.povray.org/documentation/view/3.6.0/79/"""

    if finish == "glass":
        filter_ = 0.95
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "phong 0.8 \n\t\t\t" \
                + "reflection 0.2 \n\t\t\t" \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior 1.5 {cb:c}\n\t\t".format(ob=123, cb=125)

    elif finish == "metal":
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "ambient 0.1 \n\t\t\t" \
                + "diffuse 0.1 \n\t\t\t" \
                + "specular 1.0 \n\t\t\t" \
                + "roughness 0.001 \n\t\t\t" \
                + "reflection 0.5 metallic \n\t\t\t" \
                + "{cb:c}\n\t\t".format(cb=125)

    elif finish == "irid":
        filter_ = 0.7
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "phong 0.1 \n\t\t\t" \
                + "reflection {ob:c} 0.2 metallic {cb:c}\n\t\t\t".format(ob=123, cb=125) \
                + "diffuse 0.3 \n\t\t\t" \
                + "irid {ob:c} 0.75 thickness 0.5 ".format(ob=123) \
                + "turbulence 0.5 {cb:c}\n\t\t\t".format(cb=125) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior 1.5 {cb:c}\n\t\t".format(ob=123, cb=125)

    elif finish == "billiard":
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "ambient 0.8 \n\t\t\t" \
                + "diffuse 1 \n\t\t\t" \
                + "specular 1 \n\t\t\t" \
                + "roughness 0.005 \n\t\t\t" \
                + "metallic 0.5 \n\t\t\t" \
                + "{cb:c}\n\t\t".format(cb=125)

    # color declaration for ALL finishes
    dev_string += "pigment {ob:c} ".format(ob=123) \
            + "color rgbft <{0}, {1}, {2}, {3}, {4}> ".format(color[0], color[1], color[2], filter_, transmit) \
            + "{cb:c}\n\t\t".format(cb=125)

    # add the extra bits describing the finish
    if finish != "dull":
        dev_string += extra_finish 

    dev_string += "{cb:c}\n\n\t".format(cb=125)

    return dev_string

