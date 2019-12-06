#from util import deep_access
#from util_pov import color_and_finish
#from copy import deepcopy

def create_cylinder(center, end, radius, for_silo=False):
    """ 
    Creates povray instructions for a cylindrical pillar 

    :param center: Point on the x,y-plane where the shape is centered
    :type center: list

    :param end: Limits on the z-dimensions, as [upper, lower]
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

    :param end: Limits on the z-dimensions, as [upper, lower]
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

    :param end: Limits on the z-dimensions, as [upper, lower]
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

    :param end: Limits on the z-dimensions, as [upper, lower]
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
        slab += "<{0:.6f}, {1:.6f}>, ".format(points[i][0], points[i][1])
    slab += "<{0:.6f}, {1:.6f}> \n\t\t".format(points[0][0], points[0][1])

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
    slab += "translate <{0}, {1}, {2:.6f}> \n\t\t".format( \
            x_translate, y_translate, z_translate)

    return slab, halfwidth


def create_torus(major_radius, minor_radius, center, z_top, angle=0, color=[0,0,0]):
    """
    Creates a torus for the purpose of adding lines to circular and elliptical features
    (povray torus docs: http://wiki.povray.org/content/Reference:Torus)

    major_radius: Radius of the circular or elliptical features. It takes 
                  either the halfwidths as a list (circles and ellipses) or
                  a single float/int (circles only). The function handles
                  the difference automatically.
    minor_radius: Called "line_thickness" in other functions
    center: The x-,y-coordinates of the center
    z_top: The z-coordinate of the center
    angle: Only relevant for the elliptical pillars, should they be rotated 
           about the z-axis (default 0)
    color: Torus color (defaults to black)
    """

    # Create initial torus using smaller of the major radii
    # Determine ellipse v circle based on type of major_radius
    if isinstance(major_radius, list):
        # Ellipse
        smaller_dim = min(major_radius)
        ratio = 0.0
    else:
        # Circle
        smaller_dim = major_radius
        ratio = 1.0

    torus = "torus\n\t\t{ob:c}\n\t\t\t".format(ob=123) \
            + "{0}, {1}\n\t\t\t".format(smaller_dim, minor_radius) \
            + "pigment {ob:c} color rgbft ".format(ob=123) \
            + "<{0}, {1}, {2}, 0, 0> ".format(color[0], color[1], color[2]) \
            + "{cb:c}\n\t\t\t".format(cb=125) \
            + "rotate <90, 0, 0>\n\t\t\t" \
            + "translate <{0}, {1}, {2}>\n\t\t".format(center[0], center[1], z_top)

    # Scale dimensions to make elliptical torus
    if ratio == 0.0:
        if smaller_dim == major_radius[0]:
            ratio = major_radius[1] / major_radius[0]
            torus += "scale <1, {0}, 1>".format(ratio)
        else:
            ratio = major_radius[0] / major_radius[1]
            torus += "scale <{0}, 1, 1>\n\t\t\t".format(ratio)

    if angle != 0:      # in degrees
        torus += "rotate <0, 0, {0}> \n\t\t".format(angle)

    torus += "no_shadow\n\t\t{cb:c}\n\t".format(cb=125) 
    return torus


def create_sphere(radius, center, color=[0,0,0]):
    """
    Creates a sphere for the accent line stuff

    radius: Sphere radius ("line_thickness" in other functions)
    center: The x-,y-,z-coordinates of the center
    color: Torus color (defaults to black)
    """

    sphere = "sphere\n\t\t{ob:c}\n\t\t".format(ob=123) \
            + "<{0}, {1}, {2}>, {3}\n\t\t".format(center[0], center[1], center[2], radius) \
            + "pigment {ob:c} color rgbft ".format(ob=123) \
            + "<{0}, {1}, {2}, 0, 0> ".format(color[0], color[1], color[2]) \
            + "{cb:c}\n\t\t".format(cb=125) \
            + "no_shadow\n\t\t{cb:c}\n\t".format(cb=125) 
    return sphere


def add_accent_lines(shape, z_top, center, dims, feature_height, angle=0, line_thickness=0.0020, color=[0,0,0]):
    """
    Adds lines to accentuate the edges of the device
    shape: geometry of feature, accepts "circle", "ellipse", "rectangle", and "polygon"
    z_top: z-component of the top of the device, grab from device_dims (before updating) 
    dims: Dimensions for the geometry. Required type depends on ``shape``. 
          "circle" requires a float (the radius), 
          "ellipse" and "rectangle" require [halfwidth1, halfwidth2], 
          "polygon" requires [point1, point2, ...]
    angle: Rotation angle of feature in degrees (default 0)
    feature_height: Height of the device (required for rectangles and polygons)
    line_thickness: Thickness of the line to add (default 0.0025)
    line_color: Color of line to add, as rgb (default [0,0,0], aka black)

    """
    from math import sin, cos, radians

    line = "//Accent Lines\n\t"

    # Just doublechecking, because I've screwed this up before
    feature_height = abs(feature_height)

    # Must make negative to appear in proper location
    # (Reason: Top of device located at z=0 and builds down.
    # Also, device_dims stores dimensions, not coordinates)
    z_top *= -1.0

    if shape == "circle":
        # dims is the radius
        line_upper = create_torus(dims, line_thickness, center, z_top, angle=0, color=color)
        line_lower = create_torus(dims, line_thickness, center, (z_top - feature_height), angle=0, color=color)
        line += line_upper
        line += line_lower

    elif shape == "ellipse":
        # dims is the halfwidths
        line_upper = create_torus(dims, line_thickness, center, z_top, angle=angle, color=color)
        line_lower = create_torus(dims, line_thickness, center, (z_top - feature_height), angle=angle, color=color)
        line += line_upper
        line += line_lower

    elif shape == "rectangle":
        # dims is the halfwidths

        # Define end points for each direction, pre-rotation ([min,max])
        # write_pov() defines end = [top, bottom]
        x_limits = [(-1.0 * dims[0]), (1.0 * dims[0])]
        y_limits = [(-1.0 * dims[1]), (1.0 * dims[1])]
        z_limits = [(z_top - feature_height), z_top]

        # Declare cylinders parallel to X-,Y-,Z-axes
        # All spawn parallel to the Z-axis because create_cylinder,
        # but are then rotated into place
        x_cyl = "#declare Xcyl = "
        x_cyl += create_cylinder([0.0, 0.0], x_limits, line_thickness)
        x_cyl += "pigment {ob:c} color rgbft ".format(ob=123) \
                + "<{0}, {1}, {2}, 0, 0> ".format(color[0], color[1], color[2]) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "rotate <0, 90, 0>\n\t\t".format(angle) \
                + "no_shadow\n\t\t{cb:c}\n\t".format(cb=125)

        y_cyl = "#declare Ycyl = "
        y_cyl += create_cylinder([0.0, 0.0], y_limits, line_thickness)
        y_cyl += "pigment {ob:c} color rgbft ".format(ob=123) \
                + "<{0}, {1}, {2}, 0, 0> ".format(color[0], color[1], color[2]) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "rotate <90, 0, 0>\n\t\t".format(angle) \
                + "no_shadow\n\t\t{cb:c}\n\t".format(cb=125)

        z_cyl = "#declare Zcyl = "
        z_cyl += create_cylinder([0.0, 0.0], z_limits, line_thickness)
        z_cyl += "pigment {ob:c} color rgbft ".format(ob=123) \
                + "<{0}, {1}, {2}, 0, 0> ".format(color[0], color[1], color[2]) \
                + "{cb:c}\n\t\t".format(cb=125) \
                + "no_shadow\n\t\t{cb:c}\n\t".format(cb=125)

        # Create spheres to fill corners to cover rough cylinder ends
        sph = "#declare Corner = "
        sph += create_sphere(line_thickness, [0.0, 0.0, 0.0], color=[0,0,0])

        line += x_cyl
        line += y_cyl
        line += z_cyl
        line += sph

        # Rotate and translate lines into position
        # NOTE: Povray has a left-handed coordinate system
        # This makes the trig looks weird, but it works

        # Xcyl, Ycyl
        for ii in range(2):
            vector1 = y_limits[ii] * sin(radians(angle))
            vector2 = -1.0 * y_limits[ii] * cos(radians(angle))
            for jj in range(2):
                line += "object {ob:c} Xcyl ".format(ob=123) \
                        + "rotate <{0}, {1}, {2:.6f}>\n\t\t".format(0, 0, angle) \
                        + "translate " \
                        + "<{0:.6f}, {1:.6f}, {2:.6f}>".format(vector1, vector2, z_limits[jj]) \
                        + "{cb:c}\n\t".format(cb=125)

            vector1 = x_limits[ii] * cos(radians(angle))
            vector2 = x_limits[ii] * sin(radians(angle))
            for jj in range(2):
                line += "object {ob:c} Ycyl ".format(ob=123) \
                        + "rotate <{0}, {1}, {2:.6f}>\n\t\t".format(0, 0, angle) \
                        + "translate " \
                        + "<{0:.6f}, {1:.6f}, {2:.6f}>".format(vector1, vector2, z_limits[jj]) \
                        + "{cb:c}\n\t".format(cb=125)

        # Zcyl, Corner
        for x in x_limits:
            for y in y_limits:
                vector1 = x * cos(radians(angle)) - y * sin(radians(angle))
                vector2 = y * cos(radians(angle)) + x * sin(radians(angle))
                line += "object {ob:c} Zcyl ".format(ob=123) \
                        + "translate " \
                        + "<{0:.6f}, {1:.6f}, {2:.6f}>".format(vector1, vector2, 0.0) \
                        + "{cb:c}\n\t".format(cb=125)
                for z in z_limits:
                    line += "object {ob:c} Corner ".format(ob=123) \
                            + "translate " \
                            + "<{0:.6f}, {1:.6f}, {2:.6f}>".format(vector1, vector2, z) \
                            + "{cb:c}\n\t".format(cb=125)


        print("WARNING: add_accent_lines NOT FULLY TESTED!!!")
        print("It is NOT guaranteed to work with rectangles not centered at origin!!!")

    elif shape == "polygon":
        print("Not supported yet")

    return line


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


def write_circle_feature(shapes, k, device_dims, end, default_color_dict,
        use_default_colors, custom_colors, c, use_finish, custom_finish,
        add_lines = False):

    from util import deep_access
    from util_pov import color_and_finish

    material = deep_access(shapes, [str(k), 'material'])
    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
    radius = deep_access(shapes, [str(k), 'shape_vars', 'radius'])

    circle = "// Circular pillar\n\t" \
            + create_cylinder(center, end, radius)

    circle = color_and_finish(circle, default_color_dict, material, \
            use_default_colors, custom_color = custom_colors[c], \
            use_finish = use_finish, custom_finish = custom_finish)

    # Increments through custom color list
    if not use_default_colors:
        c += 1

    # Add lines to the top and bottom of the feature
    if add_lines == True:
        lines = add_accent_lines("circle", device_dims[2], center, 
                radius, (end[1]-end[0]))
        circle += lines

    device_dims = update_device_dims(device_dims, radius, radius, 0)

    return circle, c, device_dims


def write_ellipse_feature(shapes, k, device_dims, end, default_color_dict,
        use_default_colors, custom_colors, c, use_finish, custom_finish,
        add_lines = False):

    from util import deep_access
    from util_pov import color_and_finish

    material = deep_access(shapes, [str(k), 'material'])
    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
    halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
    angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])

    ellipse = "// Ellipse\n\t" \
            + create_ellipse(center, end, halfwidths, angle)

    ellipse = color_and_finish(ellipse, default_color_dict, material, \
            use_default_colors, custom_color = custom_colors[c], \
            use_finish = use_finish, custom_finish = custom_finish)

    # Increments through custom color list
    if not use_default_colors:
        c += 1

    # Add lines to the top and bottom of the feature
    if add_lines == True:
        lines = add_accent_lines("ellipse", device_dims[2], center, 
                halfwidths, (end[1]-end[0]), angle=angle)
        ellipse += lines

    device_dims = update_device_dims(device_dims, halfwidths[0], halfwidths[1], 0)

    return ellipse, c, device_dims


def write_rectangle_feature(shapes, k, device_dims, end, default_color_dict,
        use_default_colors, custom_colors, c, use_finish, custom_finish,
        add_lines = False):

    from util import deep_access
    from util_pov import color_and_finish

    material = deep_access(shapes, [str(k), 'material'])
    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
    halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
    angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])

    rectangle = "// Rectangle\n\t" \
            + create_rectangle(center, end, halfwidths, angle)

    rectangle = color_and_finish(rectangle, default_color_dict, material, \
            use_default_colors, custom_color = custom_colors[c], \
            use_finish = use_finish, custom_finish = custom_finish)

    # Increments through custom color list
    if not use_default_colors:
        c += 1

    # Add lines edges of the feature
    if add_lines == True:
        lines = add_accent_lines("rectangle", device_dims[2], center, 
                halfwidths, (end[1]-end[0]), angle=angle)
        rectangle += lines

    device_dims = update_device_dims(device_dims, halfwidths[0], halfwidths[1], 0)

    return rectangle, c, device_dims


def write_polygon_feature(shapes, k, device_dims, end, default_color_dict,
        use_default_colors, custom_colors, c, use_finish, custom_finish,
        add_lines = False):

    from util import deep_access
    from util_pov import color_and_finish

    print("WARNING: create_polygon function has not been tested!!")
    print("The substrate is an example of a working povray prism!")
    material = deep_access(shapes, [str(k), 'material'])
    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
    angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])

    polygon = "// Polygon\n\t"
    #points = 
    #halfwidths = 

    return polygon, c, device_dims


def check_for_false_silos(shapes, layer_type):
    from util import deep_access

    for iii in range(len(layer_type)-1):
        if layer_type[iii] != "Vacuum" and layer_type[iii+1] == "Vacuum":
            layer_shape = deep_access(shapes, [str(iii+1), 'shape'])

            # Checks shapes containing radii for zero dimensions
            if layer_shape == "circle" and deep_access(shapes, [str(iii+1), 'shape_vars', 'radius']) == 0:
                print("Warning: Ignoring vacuum layer with dimensions equal to zero")

            # Checks shapes containing halfwidths for zero dimensions         
            elif layer_shape in ["ellipse", "rectangle"] and deep_access(shapes, [str(iii+1), 'shape_vars', 'halfwidths']) == [0, 0]:
                print("Warning: Ignoring vacuum layer with dimensions equal to zero")

            # Is actually a silo
            else:
                layer_type[iii] = "silo"

    return layer_type


def write_silo_feature(shapes, k, layer_type, device_dims, end, default_color_dict,
        use_default_colors, custom_colors, c, use_finish, custom_finish,
        add_lines = False):

    from util import deep_access
    from util_pov import color_and_finish
    from copy import deepcopy

    material = deep_access(shapes, [str(k), 'material'])

    device = "// Silo\n\t" \
            + "difference \n\t\t{ob:c}\n\t\t".format(ob=123)

    # First shape
    if deep_access(shapes, [str(k), 'shape']) == "circle":
        center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
        radius = deep_access(shapes, [str(k), 'shape_vars', 'radius'])
        halfwidths = [radius, radius]           # to make things work

        device += create_cylinder(center, end, radius, for_silo=True)

        # Set up for add_lines=True, even if not actually used
        shape = "circle"
        dims_outer = deepcopy(radius)

    elif deep_access(shapes, [str(k), 'shape']) == "ellipse":
        material = deep_access(shapes, [str(k), 'material'])
        center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
        halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
        angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
        device += create_ellipse(center, end, halfwidths, angle, for_silo=True)
        print("WARNING: this function has not been tested in silos!!")

        # Set up for add_lines=True, even if not actually used
        shape = "ellipse"
        dims_outer = deepcopy(halfwidths)

    elif deep_access(shapes, [str(k), 'shape']) == "rectangle":
        material = deep_access(shapes, [str(k), 'material'])
        center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
        halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
        angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
        device += create_rectangle(center, end, halfwidths, angle, for_silo=True)
        print("WARNING: this function has not been tested in silos!!")

        # Set up for add_lines=True, even if not actually used
        shape = "rectangle"
        dims_outer = deepcopy(halfwidths)

    elif deep_access(shapes, [str(k), 'shape']) == "polygon":
        print("WARNING: create_polygon function has not been tested!!")

        # Set up for add_lines=True, even if not actually used
        shape = "polygon"
        dims_outer = deepcopy(someVar)

    else:
        print("ERROR: This shape is not supported!!")

    # Create line to the top of the feature, added later
    # Also storing outer radius for later
    if add_lines == True:
        lines = add_accent_lines(shape, device_dims[2], center, 
                dims_outer, (end[1]-end[0]))

    # Hole(s)
    # Required for the hole pass to through the ends of the first shape
    end2 = [(end[0] + 0.001), (end[1] - 0.001)]

    j = k + 1
    while j < len(shapes) and layer_type[j] == "Vacuum":

        if deep_access(shapes, [str(j), 'shape']) == "circle":
            center = deep_access(shapes, [str(j), 'shape_vars', 'center'])
            radius = deep_access(shapes, [str(j), 'shape_vars', 'radius'])
            device += create_cylinder(center, end2, radius, for_silo=True)

            # Set up for add_lines=True, even if not actually used
            shape = "circle"
            dims_inner = deepcopy(radius)

        elif deep_access(shapes, [str(j), 'shape']) == "ellipse":
            material = deep_access(shapes, [str(k), 'material'])
            center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
            halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
            angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
            device += create_ellipse(center, end2, halfwidths, angle, for_silo=True)
            print("WARNING: this function has not been tested in silos!!")

            # Set up for add_lines=True, even if not actually used
            shape = "ellipse"
            dims_inner = deepcopy(halfwidths)

        elif deep_access(shapes, [str(j), 'shape']) == "rectangle":
            material = deep_access(shapes, [str(k), 'material'])
            center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
            halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
            angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
            device += create_rectangle(center, end2, halfwidths, angle, for_silo=True)
            print("WARNING: this function has not been tested in silos!!")

            # Set up for add_lines=True, even if not actually used
            shape = "rectangle"
            dims_inner = deepcopy(halfwidths)

        elif deep_access(shapes, [str(j), 'shape']) == "polygon":
            print("WARNING: create_polygon function has not been tested!!")

            # Set up for add_lines=True, even if not actually used
            shape = "polygon"
            dims_inner = deepcopy(someVar)

        else:
            print("ERROR: This shape is not supported!!")

        # Create inner lines and append to the silo master list
        if add_lines == True:
            lines_inner = add_accent_lines(shape, device_dims[2], center, 
                    dims_inner, (end[1]-end[0]))
            lines += lines_inner

        j += 1

    device = color_and_finish(device, default_color_dict, material, \
            use_default_colors, custom_color = custom_colors[c], \
            use_finish = use_finish, custom_finish = custom_finish)

    # Increments through custom color list
    if not use_default_colors:
        c += 1

    # Add all silo lines
    if add_lines == True:
        device += lines

    device_dims = update_device_dims(device_dims, halfwidths[0], halfwidths[1], 0)

    return device, c, device_dims


def create_device_layer(shapes, device_dims, end, thickness, 
        default_color_dict, use_default_colors, custom_colors, 
        c, use_finish, custom_finish, add_lines):

    from util import deep_access

    if use_default_colors == True:
        custom_colors = [[]]
        c = 0

    # Determine feature types in layer
    layer_type = []
    has_silo = False
    for ii in range(len(shapes)):
        if deep_access(shapes, [str(ii), 'material']) in ["Vacuum", "vacuum"]:
            layer_type.append("Vacuum")
            has_silo = True
        else:
            layer_type.append(deep_access(shapes, [str(ii), 'shape']))

    # Sets layer type as silo where relevant
    # Includes check for "false" silos (dimensions of zero confuse povray)
    if has_silo == True:
        layer_type = check_for_false_silos(shapes, layer_type)

    # Write device layers
    device_layer = ""
    for k in range(len(layer_type)):

        if layer_type[k] == "circle":
            feature, c, device_dims = write_circle_feature(shapes, k,
                    device_dims, end, default_color_dict,
                    use_default_colors, custom_colors, c, use_finish,
                    custom_finish, add_lines)
            device_layer += feature

        elif layer_type[k] == "silo":
            feature, c, device_dims = write_silo_feature(shapes, k,
                    layer_type, device_dims, end, default_color_dict,
                    use_default_colors, custom_colors, c, use_finish,
                    custom_finish, add_lines)
            device_layer += feature

        elif layer_type[k] == "ellipse":
            feature, c, device_dims = write_ellipse_feature(shapes, k,
                    device_dims, end, default_color_dict,
                    use_default_colors, custom_colors, c, use_finish,
                    custom_finish, add_lines)
            device_layer += feature

        elif layer_type[k] == "rectangle":
            feature, c, device_dims = write_rectangle_feature(shapes, k,
                    device_dims, end, default_color_dict,
                    use_default_colors, custom_colors, c, use_finish,
                    custom_finish, add_lines)
            device_layer += feature

        elif layer_type[k] == "polygon":
            feature, c, device_dims = write_polygon_feature(shapes, k,
                    device_dims, end, default_color_dict,
                    use_default_colors, custom_colors, c, use_finish,
                    custom_finish, add_lines)
            device_layer += feature

            print("WARNING: create_polygon function has not been tested!!")
            print("The substrate is an example of a working povray prism!")

        elif layer_type[k] == "Vacuum":
            k = k

        else:
            print("\nWARNING: Invalid or unsupported layer specified.\n")

    # End of device layer (update thickness and close union
    device_dims = update_device_dims(device_dims, 0, 0, thickness)
    device_layer += "{cb:c}\n\t".format(cb=125)

    return device_layer, c, device_dims

