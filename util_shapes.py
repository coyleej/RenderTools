########## SUMMARY OF CONTENTS ##########
# All functions here pertain to creating features (shapes),
# device layers, and accent lines.
#
# A quick summary of these functions:
# (only create_device and isosurface_unit cell called directly by user)
# - create_* creates a string describing the shape in the function name
#     device features: cylinder, ellipse, rectangle, polygon
#     accent line shapes: torus, sphere [, cylinder]
# - add_slab is used to create coating layers and the substrate
# - add_accent_lines adds accent lines to features, chooses lines based
#     on feature geometry
# - update_device_dims tracks the device size; device size is used to
#     place layers, determine camera location, and add isosurface
# - write_*_feature create strings describing the feature and calls
#     functions including create_*, add_accent_lines, and others
# - check_for_false_silos omits anything with dimension = 0
# - create_device_layer creates a single layer of a device using 
#     write_*_feature and others
# - create_device loops through all layers using create_device_layer, 
#     replicates the unit cell as requested, and adds the substrate and
#     and all coatings, 
# - isosurface_unit_cell generates a single unit cell using many of the
#     functions in this file, but with isosurface-specific modifications
#     including a different origin and scaling the device

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


def create_polygon(center, end, vertices, angle=0, for_silo=False):
    """ 
    Creates povray instructions for a polygon/prism

    ** Currently untested!! **

    :param center: Point on the x,y-plane where the shape is centered
    :type center: list

    :param end: Limits on the z-dimensions, as [upper, lower]
    :type end: list

    :param num_points: The number of vertices
    :type num_points: list

    :param vertices: List of x-,y-coordinates in counter-clockwise order
    :type vertices: list

    :param angle: Rotation angle (deg) of the polygon about its center
    :type angle: float

    :param for_silo: Adjusts the syntax if the shape is part of a silo
    :type for_silo: bool

    :return: POV-Ray code describing the prism
    :rtype: string
    """

    print("\ncreate_polygon is UNTESTED!\n")
    print("The substrate portion of write_POV contains a working prism implementation\n")
    print("Need to remove \"halfwidths\" from the function call; it shouldnt be there.\n")

    # Povray requires that you close the shape
    # The first and last point must be the same
    num_points = len(vertices) + 1

    poly_string = "prism\n\t\t{ob:c}\n\t\t".format(ob=123) \
            + "linear_sweep \n\t\tlinear_spline \n\t\t" \
            + "{0:.5f}, {1:.5f}, {2} \n\t\t".format(end[0], end[1], num_points)

    # Must spawn prism at origin, then rotate and translate into position
    # Thanks, povray's weird coordinate system
    for i in range(len(num_points)):
        vertices[i][0] -= (center[0])
        vertices[i][1] -= (center[1])
        poly_string += "<{0}, {1}>, ".format(vertices[i][0], vertices[i][1])
    poly_string += "<{0}, {1}> \n\t\t".format(vertices[0][0], vertices[0][1])

    poly_string += "rotate <90, 0, 0> \n\t\t"
    poly_string += "translate <{0}, {1}, {2}> \n\t\t".format( \
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
    :type lattice_vecs: list

    :param thickness: Thickness of the layer
    :type thickness: float

    :param device_dims: Dimensions of the existing device, in order to
                        know how far to shift the slab. Depending on the
                        slab to be inserted.
    :type device_dims: list

    :param layer_type: Type of the layer to be inserted. Determines which
                       direction everything is shifted. Accepts arguments
                       "coating", "background", "isosurface", and 
                       "substrate" (default)
    :type layer_type: string

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
    elif layer_type == "isosurface":
        x_translate = 0.5 * device_dims[0]
        y_translate = 0.5 * device_dims[1]
        z_translate = -0.5 * thickness
    else:            # "substrate"
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

    """
    Creates a circle feature within a layer, complete with color and
    finish specifications.
    """

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

    """
    Creates a ellipse feature within a layer, complete with color and
    finish specifications.
    """

    from util import deep_access
    from util_pov import color_and_finish

    material = deep_access(shapes, [str(k), 'material'])
    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
    hw = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
    halfwidths = [hw.get("x"), hw.get("y")]
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

    """
    Creates a rectangle feature within a layer, complete with color and
    finish specifications.
    """

    from util import deep_access
    from util_pov import color_and_finish

    material = deep_access(shapes, [str(k), 'material'])
    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
    hw = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
    halfwidths = [hw.get("x"), hw.get("y")]
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

    """
    Creates a polygon feature within a layer, complete with color and
    finish specifications. The polygon vertices must be specified in 
    counter-clockwise order for S4. (POV-Ray doesn't care about the 
    direction as long as the shape is closed.)
    """

    from util import deep_access
    from util_pov import color_and_finish

    print("WARNING: create_polygon function has not been tested!!")
    print("The substrate is an example of a working povray prism!")
    material = deep_access(shapes, [str(k), 'material'])
    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
    angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
    points = deep_access(shapes, [str(k), 'shape_vars', 'vertices'])

    # Grab the vertices out of the points dictionary
    # Must be formatted as a list (not a numpy array), to
    # match what create_polygon expects.
    # Don't worry about closing the array here because
    # create_polygon does that for you automatically
    # Eric and his never-ending dictionaries...
    vertices = []
    for k in range(len(points)):
        vertex = [deep_access(vert_dict2, [f"{k}", "x"]), 
                deep_access(vert_dict2, [f"{k}", "y"])]
        vertices.append(vertex)

    # Not sure why Kerry is tracking polygon halfwidths in her stuff.
    # Halfwidths only matter for rectangles and ellipses.
    # (It was here only as a copy-pasta error on my part.)
    # The shape should be fully specifed by the center and vertices.

    polygon = "// Polygon\n\t" \
            + create_polygon(center, end, vertices, angle=0)

    polygon = color_and_finish(rectangle, default_color_dict, material, \
            use_default_colors, custom_color = custom_colors[c], \
            use_finish = use_finish, custom_finish = custom_finish)

    # Increments through custom color list
    if not use_default_colors:
        c += 1

    # Add lines edges of the feature
    if add_lines == True:
        print("\nWARNING: add_accent_lines does not support polygons at this time!\n")

    device_dims = update_device_dims(device_dims, halfwidths[0], halfwidths[1], 0)

    return polygon, c, device_dims


def check_for_false_silos(shapes, layer_type):
    """
    'False silos' are instances where the layer to be subtracted has a
    dimension of zero. POV-Ray fill crash if given a 'false silo'.
    This function keeps POV-Ray happy by resetting all 'false silos'
    to the fully solid shape.
    """

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

    """
    Creates a silo. Should be able to handle any possible combination 
    of features, including multiple holes in a single feature.
    """

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
        hw = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
        halfwidths = [hw.get("x"), hw.get("y")]
        angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
        device += create_ellipse(center, end, halfwidths, angle, for_silo=True)
        print("WARNING: this function has not been tested in silos!!")

        # Set up for add_lines=True, even if not actually used
        shape = "ellipse"
        dims_outer = deepcopy(halfwidths)

    elif deep_access(shapes, [str(k), 'shape']) == "rectangle":
        material = deep_access(shapes, [str(k), 'material'])
        center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
        hw = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
        halfwidths = [hw.get("x"), hw.get("y")]
        angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
        device += create_rectangle(center, end, halfwidths, angle, for_silo=True)
        print("WARNING: this function has not been tested in silos!!")

        # Set up for add_lines=True, even if not actually used
        shape = "rectangle"
        dims_outer = deepcopy(halfwidths)

    elif deep_access(shapes, [str(k), 'shape']) == "polygon":
        print("WARNING: create_polygon function has not been tested!!")

        material = deep_access(shapes, [str(k), 'material'])
        center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
        hw = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
        halfwidths = [hw.get("x"), hw.get("y")]
        angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
        device += create_polygon(center, end, vertices, angle, for_silo=True)

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
            hw = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
            halfwidths = [hw.get("x"), hw.get("y")]
            angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
            device += create_ellipse(center, end2, halfwidths, angle, for_silo=True)
            print("WARNING: this function has not been tested in silos!!")

            # Set up for add_lines=True, even if not actually used
            shape = "ellipse"
            dims_inner = deepcopy(halfwidths)

        elif deep_access(shapes, [str(j), 'shape']) == "rectangle":
            material = deep_access(shapes, [str(k), 'material'])
            center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
            hw = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
            halfwidths = [hw.get("x"), hw.get("y")]
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

    """
    Generates a single layer of a device. Called by create_device,
    which creates the full unit cell. Adds a color and finish to each
    feature as it's created.
    """

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



def create_device(device_dict, 
    num_UC_x = 5, num_UC_y = 5, 
    coating_layers = [], 
    coating_color_dict = {"background":[1, 0, 0, 0, 0]}, 
    coating_ior_dict = {"background":1.0}, 
    use_default_colors = True, custom_colors = [[0, 0.667, 0.667, 0, 0]], 
    use_finish = "", custom_finish = "", 
    add_lines = True, 
    line_thickness = 0.0025, line_color = [0, 0, 0, 0, 0],
    display = False, render = True, num_threads = 0): #, 

    """ 
    Generates a string containing the device information.

    The required input information is
    * the dictionary entry from the json file (device_dict)

    The color and finish of the device can be specified by the user 
    via the ``color_and_finish`` function. The substrate will always 
    be a dull, dark grey; this cannot be modified by the user.

    Some assumptions:
    * All shapes describing holes in silos are the vacuum layers 
      immediately following the shape layer
    * xy-plane is centered at 0

    Returns a tuple containing
    * a string containing the device information (device)
    * the device dimensions (device_dims)
    * the coating dimensions (coating_dims)

    :param device_dict: Dictionary entry from a json file
    :type device_dict: dict

    :param num_UC_x: Number of unit cells in the y direction (default 5)
    :type num_UC_x: int 

    :param num_UC_y: Number of unit cells in the y direction (default 5)
    :type num_UC_y: int 

    :param coating_layers: List containing material and thickness of each
                           layer, starting with the bottom layer and
                           working up
    :type coating_layers: list

    :param bg_coating_color_dict: Dictionary containing color definitions
                                  for all coating layers present
    :type bg_coating_color_dict: dict

    :param bg_coating_ior_dict: Dictionary containing ior definitions
                                for all coating layers present
    :type bg_coating_ior_dict: dict

    :param bg_color: Sets the background color (default [1.0, 1.0, 1.0])
    :type bg_color: list

    :param use_default_colors: Determine color selection: True will set 
                               the color based on the material specified 
                               in ``device_dict``. False allows for use of 
                               a custom color, which is specified in 
                               ``custom_color`` (default True)
    :type use_default_colors: bool

    :param custom_colors: Define a list of custom RBGFT colors (each color is 
                          a list of five values); each shape can be assigned
                          its own color (default [[0, 0.667, 0.667, 0, 0]])
    :type custom_colors: list

    :param use_finish: The finish on the device; see ``color_and_finish`` 
                       for the full list of options (default "dull")
    :type use_finish: str

    :param custom_finish: User-specified custom finish, see ``color_and_finish`` 
                          for formatting (default "dull")
    :type custom_finish: str

    :param add_lines: Adds lines to highlight shape edges (default False)
    :type add_lines: bool

    :param line_thickness: Half-thickness of lines used when add_lines = True
                           (default 0.0025)
    :type line_thickness: float

    :param line_color: Color (as rgbft) of lines used when add_lines = True
                       (default [0, 0, 0, 0, 0] (opaque black))
    :type line_color: list

    :param render: Tells POV-Ray to render the image (default True)
    :type render: bool

    :return: device, device_dims, coating_dims
    :rtype: tuple
    """

    from os import system
    from copy import deepcopy
    from util import deep_access
#    from util_shapes import add_slab, update_device_dims
#    from util_shapes import create_device_layer 
#    from util_shapes import bg____stuff
    from util_pov import guess_camera, color_and_finish, write_header_and_camera, render_pov

    default_color_dict = {
            "subst": [0.15, 0.15, 0.15, 0, 0], 
            "Si":[0.2, 0.2, 0.2, 0, 0], 
            "SiO2":[0.99, 0.99, 0.96, 0, 0.1]
            }

    number_of_layers = deep_access(device_dict, ['statepoint', 'num_layers'])

    # Set up custom color dictionary
    orig_custom_colors = deepcopy(custom_colors)

    # Assumes no more than THREE shapes per layer
    if not use_default_colors:
        while len(custom_colors) < 3 * number_of_layers:
            for i in range(len(orig_custom_colors)):
                custom_colors.append(orig_custom_colors[i])

    # Counter for incrementing through colors
    c = 0

    # Track dimensions of the unit cell
    device_dims = [0, 0, 0] 

    # Track coating layer thickness
    coating_dims = [0, 0, 0]

    # Store device
    device = ""

    # Lattice vectors
    lattice_dict = deep_access(device_dict, ['statepoint', 'lattice_vecs'])
    lattice_vecs = list()
    for v in ['a', 'b']:
        tmp_vec = list()
        for i in ['x', 'y']:
            tmp_vec.append(deep_access(lattice_dict, [v, i]))
        lattice_vecs.append(tmp_vec)

    # Zero layer
    # Currently no need to render anything from this layer

    #### ---- DEVICE UNIT CELL ---- ####

    device += "#declare UnitCell = "
    device += "merge\n\t{ob:c}\n\t".format(ob=123)

    # Create all layers
    for i in range(number_of_layers):

        if deep_access(device_dict, ['statepoint', 'dev_layers', str(i)]).get('shapes') is not None:
            shapes = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'shapes'])
            background = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'background'])
            thickness = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'thickness'])
            # end = [top, bottom]
            end = [float(-1.0 * device_dims[2]), float(-1.0 * device_dims[2] - thickness)]

            device += "union\n\t{ob:c}\n\t".format(ob=123)

            # Check for background material
            bg_slab = ""
            #if background != "Vacuum":
            if background in coating_color_dict:
                # Forcing elimination of internal boundaries
                # (They appear if you use lattice_vecs instead of temp_vecs)
                temp_vecs = deepcopy(lattice_vecs)
                for k in range(2):
                    for l in range(2):
                        temp_vecs[k][l] += 0.0002

                device += "// Layer background\n\t"
                bg_slab, halfwidth = add_slab(temp_vecs, thickness, device_dims, 
                        layer_type="background")
                bg_slab = color_and_finish(bg_slab, default_color_dict, background, 
                        use_default_colors = False, 
                        custom_color = coating_color_dict[background],
                        ior = coating_ior_dict[background],
                        use_finish = "translucent")

                device += bg_slab

                # Prevent end caps from being overwritten by background layer(s)
                end[0] -= 0.00010
                end[1] -= 0.00010

            # Create all features within a layer
            layer, c, device_dims = create_device_layer(shapes, device_dims, 
                    end, thickness, default_color_dict, use_default_colors, 
                    custom_colors, c, use_finish, custom_finish, add_lines)
            device += layer

    # End unit cell merge
    device += "{cb:c}\n\n".format(cb=125)

    #### ---- REPLICATE UNIT CELL ---- ####

    # Shift translation so that the original device is roughly in the center
    device += "merge\n\t{ob:c} \n\t".format(ob=123)

    adj_x = int(0.5 * (num_UC_x - (1 + (num_UC_x - 1) % 2)))
    adj_y = int(0.5 * (num_UC_y - (1 + (num_UC_y - 1) % 2)))
    # Explanation: 
    # Subtracts 1 because one row stays at origin
    # Uses modulo to subtract again if odd number
    # Sends half of the remaining rows backward

    for i in range(num_UC_x):
        for j in range(num_UC_y):
            device += "object {ob:c} UnitCell translate <{0}, {1}, {2}> {cb:c}\n\t".format( 
                    ((i - adj_x) * lattice_vecs[0][0] - (j - adj_y) * lattice_vecs[1][0]), 
                    ((j - adj_y) * lattice_vecs[1][1] - (i - adj_x) * lattice_vecs[0][1]), 
                    0, ob=123, cb=125)

    #### ---- COATING AND SUBSTRATE ---- ####

    # NOTE: substrate and coatings use prism instead of box because
    # lattice isn't necessarily rectangular

    # temp_vecs are the full dimensions of the material
    temp_vecs = deepcopy(lattice_vecs)
    for j in range(2):
        temp_vecs[j][0] *= num_UC_x
        temp_vecs[j][1] *= num_UC_y

    # Slabs must remain centered at origin if num_UC_* is odd
    # Must shift slab by one unit cell if even
    if num_UC_x % 2 == 0:
        coating_dims[0] += 0.5 * lattice_vecs[0][0]
        coating_dims[0] -= 0.5 * lattice_vecs[1][0]
    if num_UC_y % 2 == 0:
        coating_dims[1] += 0.5 * lattice_vecs[1][1]
        coating_dims[1] -= 0.5 * lattice_vecs[0][1]

    substrate_dims = [coating_dims[0], coating_dims[1], device_dims[2]]
    coating_dims = update_device_dims(coating_dims, 
            coating_dims[0], coating_dims[1], 0)

    # Add coatings on top of device
    if coating_layers != []:
        for j in range(len(coating_layers)):
            device += "// Coating layer {0}\n\t".format(j + 1)
            coating, halfwidth = add_slab(temp_vecs, coating_layers[j][1], 
                    coating_dims, layer_type="coating")
            coating = color_and_finish(coating, default_color_dict, 
                    background, use_default_colors = False, 
                    custom_color=coating_color_dict[coating_layers[j][0]], 
                    ior=coating_ior_dict[coating_layers[j][0]], 
                    use_finish = "translucent")
            device += coating

            coating_dims = update_device_dims(coating_dims, 0, 0, coating_layers[j][1])

    # End device and coating merge
    device += "{cb:c}\n\n".format(cb=125)

    # Substrate
    device += "// Substrate\n\t"
    material = "subst"
    thickness_sub = max(1, deep_access(device_dict, ['statepoint', 'sub_layer', 'thickness']))

    substrate, halfwidth = add_slab(temp_vecs, thickness_sub, substrate_dims, layer_type="substrate")
    device += substrate

    device = color_and_finish(device, default_color_dict, material, 
            use_default_colors = True, use_finish = "dull")

    halfwidth = [(0.5 * (lattice_vecs[0][0] + lattice_vecs[1][0])), 
            (0.5 * (lattice_vecs[0][1] + lattice_vecs[1][1]))]

    device_dims = update_device_dims(device_dims, 0, 0, thickness_sub)

    
    # Cap how far out the camera will go when replicating unit cell
    device_dims = update_device_dims(device_dims, 
            (min(5, num_UC_x) * device_dims[0]), 
            (min(5, num_UC_y) * device_dims[1]), 
            device_dims[2])

    return device, device_dims, coating_dims


def isosurface_unit_cell(mesh, 
        device_dict, 
        n = [0, 0, 0], 
        use_slice_UC = True, 
        transmit = 0,
        corner1 = [0,0,0], 
        corner2 = [0,0,0], 
        subtract_box = True):

    """ 
    Generates a string containing the device information.

    The required input information is
    * the isosurface mesh
    * the device dictionary

    Returns a tuple containing
    * updated mesh string containing the device unit cell

    :param mesh: the mesh object describing the isosurface
    :type mesh: str

    :param device_dict: Dictionary entry from a json file
    :type device_dict: dict

    :param n: Dimensions of the numpy field array, used as the isosurface 
              dimensions
    :type n: list

    :param slice_UC: Gives you the option to take a slice out of the unit
                     cell to help visualize the field (default True)
    :type slice_UC: bool

    :param transmit: Set transparency of the unit cell (competely opaque 
                     by default); also the color cannot be changed (always 
                     a dark-ish grey)
    :type transmit: float

    :param corner1: A corner of the slice you wish to remove/keep, used
                    with corner2 to define a box for an intersection or
                    difference object
    :type corner1: list 

    :param corner2: The corner diagonally opposite corner1
    :type corner2: list 

    :param subtract_box: Controls whether POV-Ray uses a difference
                         object (True, default) or an intersection (False)
    :type subtract_box: bool 

    """

    from util import deep_access
    from util_iso import slice_isosurface
    from util_shapes import create_device_layer

    default_color_dict = {
            "subst": [0.25, 0.25, 0.25, 0, transmit],
            "Si": [0.25, 0.25, 0.25, 0, transmit],
            "SiO2": [0.25, 0.25, 0.25, 0, transmit]
            }

    number_of_layers = deep_access(device_dict, ['statepoint', 'num_layers'])

    # Counter for incrementing through colors
    c = 0
    # Track dimensions of the unit cell
    device_dims = [0, 0, 0]
    # Track coating layer thickness
    coating_dims = [0, 0, 0]
    # Store device
    device = "// Unit cell"

    # Lattice vectors
    lattice_dict = deep_access(device_dict, ['statepoint', 'lattice_vecs'])
    lattice_vecs = list()
    for v in ['a', 'b']:
        tmp_vec = list()
        for i in ['x', 'y']:
            tmp_vec.append(deep_access(lattice_dict, [v, i]))
        lattice_vecs.append(tmp_vec)

    # Begin unit cell merge
    # Necessary if multiple layers or multiple features per layer
    device = "\n\n#declare UnitCell = "
    device += "merge {ob:c}\n\t".format(ob=123)

    # Create all layers
    for i in range(number_of_layers):

        if deep_access(device_dict, ['statepoint', 'dev_layers', str(i)]).get('shapes') is not None:
            shapes = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'shapes'])
            background = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'background'])
            thickness = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'thickness'])
            # end = [top, bottom]
            end = [float(-1.0 * device_dims[2]), float(-1.0 * device_dims[2] - thickness)]

            device += "union\n\t{ob:c}\n\t".format(ob=123)

            # Create all features within a layer
            layer, c, device_dims = create_device_layer(shapes, device_dims,
                    end, thickness, default_color_dict,
                    use_default_colors = True, custom_colors = [], c = c,
                    use_finish = "dull", custom_finish = [], add_lines = [])
            device += layer

    # End unit cell merge
    device += "{cb:c}\n\n".format(cb=125)

    # Scale unit cell up to match field dimensions
    scaling_factor = n[0] / lattice_vecs[0][0]

    device += "object {ob:c} UnitCell ".format(ob=123)
    device += "\n\tscale <{0}, {0}, {0}> ".format(scaling_factor)
    device += "\n\ttranslate <{0}, ".format(0.5 * (device_dims[0] + n[0]))
    device += "{0}, ".format(0.5 * (device_dims[1] + n[1]))
    device += "{0}> \n\t{cb:c}\n\n".format(n[2] - device_dims[2], cb=125)

    # Can also subtract out pieces of the unit cell, 
    if use_slice_UC == True:
        device = slice_isosurface(device, corner1, corner2, subtract_box = subtract_box)

    # Append unit cell to mesh object
    mesh += device

    return mesh


