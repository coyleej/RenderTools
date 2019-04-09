def create_cylinder(center, end, radius, for_silo=False):
    """ 
    Creates povray instructions for a cylindrical pillar 

    :param center: Point on the x,y-plane where the shape is centered
    :type center: list

    :param end: The lower and upper limits on the z-dimensions
    :type end: list
      
    :param radius: Cylinder radius
    :type radius: float

    :param for_silo: Adjusts the syntax if the shape is part of a silo
    :type for_silo: bool

    :return: POV-Ray code describing the cylinder
    :rtype: string

    """
    cyl_string = "cylinder \n\t\t{ob:c}\n\t\t ".format(ob=123) \
            + "<{0}, {1}, {2:.5f}>, \n\t\t".format(center[0], center[1], end[0]) \
            + "<{0}, {1}, {2:.5f}>, \n\t\t".format(center[0], center[1], end[1]) 

    if for_silo:
        cyl_string += "{0} {cb:c}\n\t\t".format(radius, cb=125)
    else:
        cyl_string += "{0}\n\t\t".format(radius)

    return cyl_string

def create_ellipse(center, end, halfwidths, angle=0, for_silo=False):
    """ 
    Creates povray instructions for a ellipical pillar 

    :param center: Point on the x,y-plane where the shape is centered
    :type center: list

    :param end: The lower and upper limits on the z-dimensions
    :type end: list
      
    :param halfwidths: Semi-major and semi-minor axes of the ellipse
    :type halfwidths: list

    :param angle: Rotation angle (deg) of the ellipse about its center
    :type angle: float

    :param for_silo: Adjusts the syntax if the shape is part of a silo
    :type for_silo: bool

    :return: POV-Ray code describing the elliptical cylinder
    :rtype: string
    """
    ellipse_string = "cylinder \n\t\t{ob:c}\n\t\t ".format(ob=123) \
            + "<{0}, {1}, {2:.5f}>, \n\t\t".format(center[0], center[1], end[0]) \
            + "<{0}, {1}, {2:.5f}>, 1 \n\t\t".format(center[0], center[1], end[1]) \
            + "scale <{0}, {1}, 1> \n\t\t".format(halfwidths[0], halfwidths[1])

    if angle != 0:      # in degrees
        ellipse_string += "rotate <0, 0, {0}> \n\t\t".format(angle)
    if for_silo:
        ellipse_string += "{cb:c}\n\t\t".format(cb=125)

    return ellipse_string

def create_rectangle(center, end, halfwidths, angle=0, for_silo=False):
    """ 
    Creates povray instructions for a rectangular box

    :param center: Point on the x,y-plane where the shape is centered
    :type center: list

    :param end: The lower and upper limits on the z-dimensions
    :type end: list

    :param halfwidths: Halfwidths describing lengths in the x-, y-dims
    :type halfwidths: list

    :param angle: Rotation angle (deg) of the rectangle about its center
    :type angle: float

    :param for_silo: Adjusts the syntax if the shape is part of a silo
    :type for_silo: bool

    :return: POV-Ray code describing the box
    :rtype: string
    """
    rect_string = "box\n\t\t{ob:c}\n\t\t".format(ob=123) \
            + "<{0}, ".format(center[0] - halfwidths[0]) \
            + "{0}, {1:.5f}>\n\t\t".format((center[1] - halfwidths[1]), end[0]) \
            + "<{0} ".format(center[0] + halfwidths[0]) \
            + "{0}, {1:.5f}>\n\t\t".format((center[1] + halfwidths[1]), end[1])

    if angle != 0:      # in degrees
        rect_string += "rotate <0, 0, {0}> \n\t\t".format(angle)
    if for_silo:
        rect_string += "{cb:c}\n\t\t".format(cb=125)

    return rect_string

def create_polygon(center, end, halfwidths, points, device_dims, angle=0, for_silo=False):
    """ 
    Creates povray instructions for a polygon/prism

    ** Currently untested!! **

    :param center: Point on the x,y-plane where the shape is centered
    :type center: list

    :param end: The lower and upper limits on the z-dimensions
    :type end: list

    :param num_points: The number of vertices
    :type num_points: list

    :param points: List of x-,y-coordinates in counter-clockwise order
    :type points: list

    :param angle: Rotation angle (deg) of the polygon about its center
    :type angle: float

    :param for_silo: Adjusts the syntax if the shape is part of a silo
    :type for_silo: bool

    :return: POV-Ray code describing the prism
    :rtype: string
    """

    print("\ncreate_polygon is UNTESTED!\n")
    print("The substrate portion of write_POV contains a working prism implementation\n")

    # Povray requires that you close the shape
    # The first and last point must be the same
    num_points = len(points) + 1

    poly_string = "prism\n\t\t{ob:c}\n\t\t".format(ob=123) \
            + "linear_sweep \n\t\tlinear_spline \n\t\t" \
            + "{0:.5f}, {1:.5f}, {2} \n\t\t".format(end[0], end[1], num_points)

    # Must spawn prism at origin, then rotate and translate into position
    # Thanks, povray's weird coordinate system
    for i in range(len(num_points)):
        points[i][0] -= (center[0] + halfwidth[0])
        points[i][1] -= (center[1] + halfwidth[1])
        poly_string += "<{0}, {1}>, ".format(points[i][0], points[i][1])
    poly_string += "<{0}, {1}> \n\t\t".format(points[0][0], points[0][1])

    device += "rotate <90, 0, 0> \n\t\t"
    device += "translate <{0}, {1}, {2}> \n\t\t".format( \
            (-1.0 * center[0]), (-1.0 * center[1]), (end[0] - device_dims[2]))

    if angle != 0:      # in degrees
        poly_string += "rotate <0, 0, {0}> \n\t\t".format(angle)
    if for_silo:
        poly_string += "{cb:c}\n\t\t".format(cb=125)

    return poly_string

def add_slab(lattice_vecs, thickness, device_dims, layer_type="substrate"):
    """
    Adds a slab using the lattice vectors as the dimensions. Use this 
    for the substrate, background, and any coating layers. You must
    specify the type in the function call. Designed so that lattice_vecs
    and device_dims can be either a unit cell or the full device.

    :param lattice_vecs: The lattice vectors defining the slab. In the 
                         case of the substrate and coatings, these are
                         the full length and width of the material
    :type center: list

    :param thickness: Thickness of the layer
    :type center: float

    :param device_dims: Dimensions of the existing device, in order to
                        know how far to shift the slab. Depending on the
                        slab to be inserted.
    :type center: list

    :param thickness: Type of the layer to be inserted. Determines which
                      direction everything is shifted. Accepts arguments
                      "coating", "background", and "substrate" (default)
    :type center: string

    :return: POV-Ray code describing the slab and the slab halfwidths
    :rtype: tuple
    """

    halfwidth = [(0.5 * (lattice_vecs[0][0] + lattice_vecs[1][0])),
            (0.5 * (lattice_vecs[0][1] + lattice_vecs[1][1]))]

    # Curse povray's weird coordinate system, only the prism is affected by it 
    # Must spawn at center, then rotate and translate later
    end = [(-0.5 * thickness), (0.5 * thickness)]

    # Defining slab vertices from lattice_vecs
    # The shape is closed later (Povray requires that the first & last points match)
    points = [ [0, 0],
            [lattice_vecs[0][0], lattice_vecs[0][1]],
            [(lattice_vecs[0][0] + lattice_vecs[1][0]), (lattice_vecs[0][1] + lattice_vecs[1][1])],
            [lattice_vecs[1][0], lattice_vecs[1][1]] ]

    # Write slab layer, adding teensy extra height to prevent weird artifacts
    slab = "prism\n\t\t{ob:c}\n\t\t".format(ob=123) \
            + "linear_sweep \n\t\tlinear_spline \n\t\t" \
            + "{0}, {1}, {2} \n\t\t".format(end[0] * 1.0, end[1] * 1.000001, (len(points) + 1))

    for i in range(len(points)):
        points[i][0] -= halfwidth[0]
        points[i][1] -= halfwidth[1]
        slab += "<{0}, {1}>, ".format(points[i][0], points[i][1])
    slab += "<{0}, {1}> \n\t\t".format(points[0][0], points[0][1])

    # Determine translation vector
    if layer_type == "coating":
        x_translate = device_dims[0]
        y_translate = device_dims[1]
        z_translate = end[1] + device_dims[2]
    elif layer_type == "background":
        x_translate, y_translate = 0, 0
        z_translate = end[0] - device_dims[2]
    else:           # "substrate"
        x_translate = device_dims[0]
        y_translate = device_dims[1]
        z_translate = end[0] - device_dims[2]

    # Move slab to final location
    slab += "rotate <90, 0, 0> \n\t\t"
    slab += "translate <{0}, {1}, {2}> \n\t\t".format( \
            x_translate, y_translate, z_translate)

    return slab, halfwidth

def update_device_dims(device_dims, new_x, new_y, new_z):
    """
    Tracks maximum unit device dimensions to aid in camera placement.
    MAlso used to track coating thickness in the case of multiple
    coatings.
    
    These dimensions will always be positive, even though the device 
    is built with the top at z=0.

    :param device_dims: Existing device dimensions
    :type device_dims: list

    :param new_x: x-dimensions of the newest layer
    :type new_x: float

    :param new_y: x-dimensions of the newest layer
    :type new_y: float

    :param new_z: Thickness of the newest layer
    :type new_z: float

    :return: Updated device dimensions
    :rtype: list
    """
    device_dims[0] = max(new_x, device_dims[0])
    device_dims[1] = max(new_y, device_dims[1])
    device_dims[2] += new_z
    return device_dims

def guess_camera(device_dims, coating_dims=[0,0,0], camera_style="perspective", angle=0, center=[0, 0]):
    """ 
    Guesses the camera location if you have no idea what a good camera 
    position is. Can look at the device from the side (angle = 0) or at an 
    angle in the xy-plane (rotate around z-axis, *DEGREES* from x-axis). 
    It has been optimized to give decent results, though fine-tuning in the
    .pov file is always encouraged.
    
    :param device_dims: Dimensions of the unit cell
    :type device_dims: list

    :param coating_dims: Dimensions of the coating layer(s)
    :type device_dims: list

    :param camera_style: The desired camera style, currently accepts perspective and orthographic
    :type camera_sylte: string

    :param angle: Rotates the camera around the z-axis (in degrees)
                  0 will look down the x-axis at the side of the device
    :type angle: float
    
    :param center: The center of the device
    :type center: list

    :return: Tuple containing the camera position, camera look at location, and the light position
    :rtype: tuple
    """
    from math import sin, cos, pi

    camera_position = [0, 0, 0]
    light_position = [0, 0, 0]

    deg_to_rads = pi / 180.0
    angle *= deg_to_rads 

    if camera_style == "perspective":
        x_offset = 1.2
        z_scale = 1.0
    elif camera_style == "orthographic":
        x_offset = 1.2
        z_scale = 1.0
    else:
        x_offset = 1.2
        z_scale = 1.0
        print("WARNING: Camera parameters have not been optimized for this style!")

    # Offset for x,y-dimensions
    camera_offset = x_offset * (max(device_dims) + 0.8 * max(coating_dims))

    camera_position[0] = (camera_offset + device_dims[0]) * cos(angle)
    camera_position[1] = (camera_offset + device_dims[0]) * sin(angle)
    camera_position[2] = z_scale * (device_dims[2] + 0.5 * coating_dims[2])
    camera_look_at = [center[0], center[1], (-0.66 * device_dims[2] + 0.50 * coating_dims[2])]

    light_offset = camera_offset * 1.25 
    light_position[0] = (device_dims[0] + light_offset) * cos(angle - 12 * deg_to_rads)
    light_position[1] = (device_dims[1] + light_offset/1.0) * sin(angle - 12 * deg_to_rads)
    light_position[2] = camera_position[2] + light_offset/3.0

    #print("Write_POV estimated camera parameters:")
    #print("camera_position : " , camera_position)
    #print("camera_look_at : ", camera_look_at)

    return camera_position, camera_look_at, light_position

def color_and_finish(dev_string, default_color_dict, material, use_default_colors, 
        custom_color = [0, 0.6667, 0.667, 0, 0], ior = 1, use_finish = "dull",
        custom_finish = ""):
    """ 
    Sets the color and finish of the object and appends this to the device string.
    The filter and transmit terms are both 0 by default.
    Do not remove the underscore from filter_, as filter is a function in python.

    Users may specify their own custom color scheme or use the default, 
    which is based on the material type specified in the device file.

    Available finishes: see ``use_finish``  parameter for details. 
    Specifying "material" will use the material finish (currently "Si", 
    "SiO2", or "subst") finish in order to accomodate multiple material 
    types in a device. The substrate will always have the "dull" finish.

    If using the "custom" finish, the finish details must be specified in the
    custom_finish variable or it will default to "dull".

    If you request one of the following finishes, the code will overwrite 
    your transmit and filter values. If you do now want this to happen, you
    should declare your own custom finish.

    :param dev_string: String describing the device
    :type dev_string: str

    :param default_color_dict: Dictionary containing the default finishes for the 
                               various material types
    :type default_color_dict: dict

    :param use_default_colors: Boolean to select which color set to use. True will 
                               assign colors based on the material type ("Si", 
                               "SiO2", and "subst"). False will use user-assigned 
                               custom colors.
    :type use_default_colors: bool

    :param custom_color: RGBFT values describing a single color. If you set 
                         ``use_default_colors=False`` but forget to specify a 
                         custom color, it will use #00aaaa (the Windows 95 
                         default desktop color).

                         RGB values must be in the range [0,1]. F and T are
                         filter and transmit, respectively. F and T are 
                         optional and both default to 0.
    :type custom_color: list

    :param ior: Index of refraction for transparent finish only
    :type ior: float

    :param use_finish: Select the finish that you want. Current options are:
                       "material", "Si", "SiO2", "glass", "bright_metal", 
                       "dull_metal", "irid", "billiard", "dull", "custom"
    :type use_finish: str

    :param custom_finish: User-defined custom finish. Set ``use_finish=custom``
                          to call this option.
    :type custom_finish: str
    """

    # These two values only matter for SiO2, translucent, glass, and irid finishes
    transmit, filter_ = 0, 0

    # Set finish
    if use_finish == "material":
        use_finish = material

    if use_finish == "Si" or use_finish == "silicon":
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "diffuse 0.2 \n\t\t\t" \
                + "brilliance 5 \n\t\t\t" \
                + "phong 1 \n\t\t\t" \
                + "phong_size 250 \n\t\t\t" \
                + "roughness 0.01 \n\t\t\t" \
                + "reflection <0.10, 0.10, 0.5> metallic \n\t\t\t" \
                + " metallic \n\t\t\t" \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior 4.24 {cb:c}\n\t\t".format(ob=123, cb=125)
                # IOR taken from blender

    elif use_finish == "SiO2":
        filter_ = 0.98
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "specular 0.6 \n\t\t\t" \
                + "brilliance 5 \n\t\t\t" \
                + "roughness 0.001 \n\t\t\t" \
                + "reflection {ob:c} 0.0, 1.0 fresnel on {cb:c}\n\t\t\t".format(ob=123, cb=125) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior 1.45 {cb:c}\n\t\t".format(ob=123, cb=125)

    elif use_finish == "translucent":
        transmit = 0.02
        filter_ = 0.50
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "emission 0.25 \n\t\t\t" \
                + "diffuse 0.75 \n\t\t\t" \
                + "specular 0.4 \n\t\t\t" \
                + "brilliance 4 \n\t\t\t" \
                + "reflection {ob:c} 0.5 fresnel on {cb:c}\n\t\t\t".format(ob=123, cb=125) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior {0} {cb:c}\n\t\t".format(ior, ob=123, cb=125)

    elif use_finish == "glass":
        filter_ = 0.95
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "specular 0.6 \n\t\t\t" \
                + "phong 0.8 \n\t\t\t" \
                + "brilliance 5 \n\t\t\t" \
                + "reflection {ob:c} 0.2, 1.0 fresnel on {cb:c}\n\t\t\t".format(ob=123, cb=125) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior 1.5 {cb:c}\n\t\t".format(ob=123, cb=125)

    elif use_finish == "dull_metal":
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "emission 0.1 \n\t\t\t" \
                + "diffuse 0.1 \n\t\t\t" \
                + "specular 1.0 \n\t\t\t" \
                + "roughness 0.001 \n\t\t\t" \
                + "reflection 0.5 metallic \n\t\t\t" \
                + " metallic \n\t\t\t" \
                + "{cb:c}\n\t\t".format(cb=125)

    elif use_finish == "bright_metal":
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "emission 0.2 \n\t\t\t" \
                + "diffuse 0.3 \n\t\t\t" \
                + "specular 0.8 \n\t\t\t" \
                + "roughness 0.01 \n\t\t\t" \
                + "reflection 0.5 metallic \n\t\t\t" \
                + " metallic \n\t\t\t" \
                + "{cb:c}\n\t\t".format(cb=125)

    elif use_finish == "irid":
        filter_ = 0.7
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "phong 0.5 \n\t\t\t" \
                + "reflection {ob:c} 0.2 metallic {cb:c}\n\t\t\t".format(ob=123, cb=125) \
                + "diffuse 0.3 \n\t\t\t" \
                + "irid {ob:c} 0.75 thickness 0.5 ".format(ob=123) \
                + "turbulence 0.5 {cb:c}\n\t\t\t".format(cb=125) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "interior {ob:c} ior 1.5 {cb:c}\n\t\t".format(ob=123, cb=125)

    elif use_finish == "billiard":
        extra_finish = "finish \n\t\t\t{ob:c} \n\t\t\t".format(ob=123) \
                + "ambient 0.3 \n\t\t\t" \
                + "diffuse 0.8 \n\t\t\t" \
                + "specular 0.2 \n\t\t\t" \
                + "roughness 0.005 \n\t\t\t" \
                + "metallic 0.5 \n\t\t\t" \
                + "{cb:c}\n\t\t".format(cb=125)

    elif use_finish == "custom":
        extra_finish = custom_finish

    else:
        extra_finish = ""

    # Color declaration for ALL finishes
    if use_default_colors:
        color = default_color_dict[material]
    else:
        color = custom_color

    if len(color) == 3:
        color.append(0)     # filter
        color.append(0)     # transmit

    if use_finish in ["SiO2", "translucent", "glass", "irid"]: 
        print("\nWARNING: color_and_finish is overriding transmit and/or filter value!!")
        color[3] = transmit
        color[4] = filter_

    dev_string += "pigment {ob:c} ".format(ob=123) \
            + "color rgbft " \
            + "<{0}, {1}, {2}, {3}, {4}>".format(color[0], color[1], color[2], color[3], color[4]) \
            + " {cb:c}\n\t\t".format(cb=125)

    # Add the extra bits describing the finish
    #if use_finish != "dull":
    if extra_finish:
        dev_string += extra_finish 

    dev_string += "{cb:c}\n\n\t".format(cb=125)

    return dev_string

