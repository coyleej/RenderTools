#### ---- NEW FUNCTIONS ---- ####

def create_cylinder(center, end, radius, for_silo=False):
    """ Creates a circular pillar """
    cyl_string = "cylinder \n\t\t{ob:c}\n\t\t ".format(ob=123) \
            + "<{0}, {1}, {2}>, \n\t\t".format(center[0], center[1], end[0]) \
            + "<{0}, {1}, {2}>, \n\t\t".format(center[0], center[1], end[1]) 
    if for_silo:
        cyl_string += "{0} {cb:c}\n\t\t".format(radius, cb=125)
    else:
        cyl_string += "{0}\n\t\t".format(radius)
    return cyl_string

def create_ellipse(center, end, halfwidths, angle=0, for_silo=False):
    """ Creates an elliptical pillar """
    ellipse_string = "cylinder \n\t\t{ob:c}\n\t\t ".format(ob=123) \
            + "<{0}, {1}, {2}>, \n\t\t".format(center[0], center[1], end[0]) \
            + "<{0}, {1}, {2}>, 1 \n\t\t".format(center[0], center[1], end[1]) \
            + "scale <{0}, {1}, 1> \n\t\t".format(halfwidths[0], halfwidths[1])
    if angle != 0:      # in degrees
        ellipse_string += "rotate <0, 0, {0}> \n\t\t".format(angle)
    if for_silo:
        ellipse_string += "{cb:c}\n\t\t".format(cb=125)
    return ellipse_string

def create_rectangle(center, end, halfwidths, angle=0, for_silo=False):
    """ Creates a rectangular box """
    rect_string = "box\n\t\t{ob:c}\n\t\t".format(ob=123) \
            + "<{0}, ".format(center[0] - halfwidths[0]) \
            + "{0}, {1}>\n\t\t".format((center[1] - halfwidths[1]), end[0]) \
            + "<{0} ".format(center[0] + halfwidths[0]) \
            + "{0}, {1}>\n\t\t".format((center[1] + halfwidths[1]), end[1])
    if angle != 0:      # in degrees
        rect_string += "rotate <0, 0, {0}> \n\t\t".format(angle)
    if for_silo:
        rect_string += "{cb:c}\n\t\t".format(cb=125)
    return rect_string

def create_polygon(center, end, num_points, points, angle=0, for_silo=False):
    """ Creates a polygon. CURRENTLY UNTESTED!!"""
    print("\ncreate_polygon is untested!\n")
    poly_string = "prism\n\t\t{ob:c}\n\t\t".format(ob=123) \
            + "linear_sweep \n\t\tlinear_spline \n\t\t" \
            + "{0}, {1}, {2} \n\t\t".format(num_points, end[0], end[1])
    for i in range(len(num_points)):
        poly_string += "<{0}, {1}>, ".format(points[i][0], points[i][1])
    poly_string += "<{0}, {1}> ".format(points[0][0], points[0][1])
    if center != [0.0, 0.0]:
        poly_string += "translate <{0}, {1}, 0> \n\t\t".format(center[0], center[1])
    if angle != 0:      # in degrees
        poly_string += "rotate <0, 0, {0}> \n\t\t".format(angle)
    if for_silo:
        poly_string += "{cb:c}\n\t\t".format(cb=125)
    return

def update_device_dims(device_dims, new_x, new_y, new_z):
    """ Tracks overall device dimensions to aid in guessing camera placement"""
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
    angle *= deg_to_rads    # to radians!

    if camera_style == "perspective":
        x_offset = 1.2
    else:
        x_offset = 1.2
        print("WARNING: Camera parameters have not been optimized for this style!")

    camera_offset = x_offset * max(device_dims) 
    camera_z_scale = 1.0            # was 0.5 

    camera_position[0] = (camera_offset + device_dims[0]) * cos(angle)
    camera_position[1] = (camera_offset + device_dims[0]) * sin(angle)
    camera_position[2] = camera_z_scale * (device_dims[2])
    camera_look_at = [center[0], center[1], (-0.66 * device_dims[2])]

    light_offset = camera_offset * 1.25 #* 4.0/3.0
    light_position[0] = (device_dims[0] + light_offset) * cos(angle - 12 * deg_to_rads)
    light_position[1] = (device_dims[1] + light_offset/1.0) * sin(angle - 12 * deg_to_rads)
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

    if finish == "Si" or finish == "silicon":
        filter_ = 0.5
        transmist = 1.5
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "ambient 0.1 \n\t\t\t" \
                + "diffuse 0.1 \n\t\t\t" \
                + "specular 1.0 \n\t\t\t" \
                + "brilliance 5 \n\t\t\t" \
                + "roughness 0.001 \n\t\t\t" \
                + "reflection 0.4 metallic \n\t\t\t" \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior 4.24 {cb:c}\n\t\t".format(ob=123, cb=125)
                # IOR taken from blender documentation: https://docs.blender.org/manual/en/latest/render/blender_render/materials/properties/transparency.html#examples

    elif finish == "SiO2":
        extra_finish = ""
        filter_ = 0.98
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "specular 0.6 \n\t\t\t" \
                + "phong 0.8 \n\t\t\t" \
                + "brilliance 5 \n\t\t\t" \
                + "reflection {ob:c} 0.0, 1.0 fresnel on {cb:c}\n\t\t\t".format(ob=123, cb=125) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior 1.45 {cb:c}\n\t\t".format(ob=123, cb=125)

    elif finish == "glass":
        filter_ = 0.95
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "specular 0.6 \n\t\t\t" \
                + "phong 0.8 \n\t\t\t" \
                + "brilliance 5 \n\t\t\t" \
                + "reflection {ob:c} 0.2, 1.0 fresnel on {cb:c}\n\t\t\t".format(ob=123, cb=125) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior 1.5 {cb:c}\n\t\t".format(ob=123, cb=125)
                #+ "phong 0.8 \n\t\t\t" \
                #+ "reflection 0.2 \n\t\t\t" \
                #+ "{cb:c}\n\t\t".format(cb=125) \
                #+ "interior {ob:c} ior 1.5 {cb:c}\n\t\t".format(ob=123, cb=125)

    elif finish == "metal":
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "emission 0.1 \n\t\t\t" \
                + "diffuse 0.1 \n\t\t\t" \
                + "specular 1.0 \n\t\t\t" \
                + "roughness 0.001 \n\t\t\t" \
                + "reflection 0.5 metallic \n\t\t\t" \
                + "{cb:c}\n\t\t".format(cb=125)
                #+ "ambient 0.1 \n\t\t\t" \ # ambient replaced by emission in 3.7

    elif finish == "irid":
        filter_ = 0.7
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "phong 0.5 \n\t\t\t" \
                + "reflection {ob:c} 0.2 metallic {cb:c}\n\t\t\t".format(ob=123, cb=125) \
                + "diffuse 0.3 \n\t\t\t" \
                + "irid {ob:c} 0.75 thickness 0.5 ".format(ob=123) \
                + "turbulence 0.5 {cb:c}\n\t\t\t".format(cb=125) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior 1.5 {cb:c}\n\t\t".format(ob=123, cb=125)
                #+ "phong 0.1 \n\t\t\t" \

    elif finish == "billiard":
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "ambient 0.3 \n\t\t\t" \
                + "diffuse 0.8 \n\t\t\t" \
                + "specular 0.2 \n\t\t\t" \
                + "roughness 0.005 \n\t\t\t" \
                + "metallic 0.5 \n\t\t\t" \
                + "{cb:c}\n\t\t".format(cb=125)
                #+ "ambient 0.8 \n\t\t\t" \ # ambient replaced by emission in 3.7

    # color declaration for ALL finishes
    dev_string += "pigment {ob:c} ".format(ob=123) \
            + "color rgbft <{0}, {1}, {2}, {3}, {4}> ".format(color[0], color[1], color[2], filter_, transmit) \
            + "{cb:c}\n\t\t".format(cb=125)

    # add the extra bits describing the finish
    if finish != "dull":
        dev_string += extra_finish 

    dev_string += "{cb:c}\n\n\t".format(cb=125)

    return dev_string

