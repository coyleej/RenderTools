"""Create features (shapes), device layers, and accent lines.

Only create_device and isosurface_unit cell called directly by user.

A quick summary:
  * create_* creates a string describing the shape in the function name
    device features: cylinder, ellipse, rectangle, polygon
    accent line shapes: torus, sphere [, cylinder]
  * add_slab is used to create coating layers and the substrate
  * add_accent_lines adds accent lines to features, chooses lines based
    on feature geometry
  * update_device_dims tracks the device size; device size is used to
    place layers, determine camera location, and add isosurface
  * write_*_feature create strings describing the feature and calls
    functions including create_*, add_accent_lines, and others
  * check_for_false_silos omits anything with dimension = 0
  * create_device_layer creates a single layer of a device using 
    write_*_feature and others
  * create_device loops through all layers using create_device_layer, 
    replicates the unit cell as requested, and adds the substrate and
    and all coatings, 
  * isosurface_unit_cell generates a single unit cell using many of the
    functions in this file, but with isosurface-specific modifications
    including a different origin and scaling the device
  * create_finish_dict creates a dictionary containing the default,
    custom, and coating finishes as relevant
  * set_color_and_finish sets the color and finish based on values 
    specified by the user and available in finish_dict
"""

def create_cylinder(center, end, radius, for_silo=False):
    """Create and return povray instructions for a cylindrical pillar.

    Args:
      center (list): Point on the x,y-plane where the shape is centered
      end (list): Limits on the z-dimensions, as [upper, lower]
      radius (float): Cylinder radius
      for_silo (bool, optional): Adjusts the syntax if the shape is
          part of a silo (Default value = False)

    Returns:
      string: POV-Ray code describing the cylinder

    """
    cyl_string = (f"cylinder \n\t\t{{\n\t\t "
            + f"<{center[0]}, {center[1]}, {end[0]:.5f}>, \n\t\t"
            + f"<{center[0]}, {center[1]}, {end[1]:.5f}>, \n\t\t")

    if for_silo:
        cyl_string += f"{radius} }}\n\t\t"
    else:
        cyl_string += f"{radius}\n\t\t"

    return cyl_string


def create_ellipse(center, end, halfwidths, angle=0, for_silo=False):
    """Create and return povray instructions for a ellipical pillar.

    Args:
      center (list): Point on the x,y-plane where the shape is centered
      end (list): Limits on the z-dimensions, as [upper, lower]
      halfwidths (list): Semi-major and semi-minor axes of the ellipse
      angle (float, optional): Rotation angle (deg) of the ellipse 
          about its center (Default value = 0)
      for_silo(bool, optional): Adjusts the syntax if the shape is part
          of a silo (Default value = False)

    Returns:
      string: POV-Ray code describing the elliptical cylinder

    """
    # Added radius=1 because it was omitted for some reason
    ellipse_string = (f"cylinder \n\t\t{{\n\t\t "
            + f"<{center[0]}, {center[1]}, {end[0]:.5f}>, \n\t\t"
            + f"<{center[0]}, {center[1]}, {end[1]:.5f}>, \n\t\t"
            + f"1\n\t\t"
            + f"scale <{halfwidths[0]}, {halfwidths[1]}, 1>\n\t\t")

    if angle != 0:      # in degrees
        ellipse_string += f"rotate <0, 0, {angle}> \n\t\t"
    if for_silo:
        ellipse_string += f"}}\n\t\t"

    return ellipse_string


def create_rectangle(center, end, halfwidths, angle=0, for_silo=False):
    """Create and return povray instructions for a rectangular box.

    Args:
      center (list): Point on the x,y-plane where the shape is centered
      end (list): Limits on the z-dimensions, as [upper, lower]
      halfwidths (list): Halfwidths describing lengths in the x-, y-dims
      angle (float, optional): Rotation angle (deg) of the rectangle
          about its center (Default value = 0)
      for_silo (bool, optional): Adjusts the syntax if the shape is
          part of a silo (Default value = False)

    Returns:
      string: POV-Ray code describing the box

    """
    rect_string = (f"box\n\t\t{{\n\t\t"
            + f"<{(center[0] - halfwidths[0])}, "
            + f"{(center[1]-halfwidths[1])}, {end[0]:.5f}>\n\t\t"
            + f"<{(center[0] + halfwidths[0])} "
            + f"{(center[1]+halfwidths[1])}, {end[1]:.5f}>\n\t\t")

    if angle != 0:      # in degrees
        rect_string += f"rotate <0, 0, {angle}> \n\t\t"

    if for_silo:
        rect_string += f"}}\n\t\t"

    return rect_string


def create_polygon(center, end, vertices, device_dims, angle=0, 
        for_silo=False):
    """Create and return povray instructions for a polygon/prism.

    Args:
      center (list): Point on the x,y-plane where the shape is centered
      end (list): Limits on the z-dimensions, as [upper, lower]
      vertices (list): The x-,y-coordinates in counter-clockwise order
      device_dims (list): Existing device dimensions
      angle (float, optional): Rotation angle (deg) of the polygon
          about its center (Default value = 0)
      for_silo (bool, optional): Adjusts the syntax if the shape is
          part of a silo (Default value = False)

    Returns:
      string: POV-Ray code describing the prism

    """
    # Povray requires that you close the shape
    # The first and last point must be the same
    num_points = len(vertices) + 1

    poly_string = (f"prism\n\t\t{{\n\t\t"
            + "linear_sweep \n\t\tlinear_spline \n\t\t"
            + f"{end[0]:.5f}, {end[1]:.5f}, {num_points} \n\t\t")

    # Must spawn prism at origin, then rotate and translate into position
    # Thanks, povray's weird coordinate system
    for i in range(len(vertices)):
        vertices[i][0] -= (center[0])
        vertices[i][1] -= (center[1])
        poly_string += f"<{vertices[i][0]}, {vertices[i][1]}>, "
    poly_string += f"<{vertices[0][0]}, {vertices[0][1]}>\n\t\t"

    poly_string += "rotate <90, 0, 0> \n\t\t"
    poly_string += (f"translate -<{center[0]}, -{center[1]}, "
            + f"{(end[0]-device_dims[2])}> \n\t\t")

    if angle != 0:      # in degrees
        poly_string += f"rotate <0, 0, {angle}> \n\t\t"

    if for_silo:
        poly_string += f"}}\n\t\t"

    return poly_string


def add_slab(lattice_vecs, thickness, device_dims, layer_type="substrate"):
    """Return a slab using lattice vectors as the dimensions.
    
    Use this for the substrate, background, and any coating layers.
    You must specify the type in the function call. Designed so that
    lattice_vecs and device_dims can be either a unit cell or the full
    device.

    Args:
      lattice_vecs (list): The lattice vectors defining the slab. In
          the case of the substrate and coatings, these are the full
          length and width of the material
      thickness (float): Thickness of the layer
      device_dims (list): Dimensions of the existing device, in order
          to know how far to shift the slab. Depending on the slab to
          be inserted.
      layer_type (string, optional): Type of the layer to be inserted.
          Determines which direction everything is shifted. Accepts 
          arguments "coating", "background", "isosurface", and 
          "substrate" (default)

    Returns:
      tuple: POV-Ray code describing the slab and the slab halfwidths

    """
    halfwidth = [(0.5 * (lattice_vecs[0][0] + lattice_vecs[1][0])),
            (0.5 * (lattice_vecs[0][1] + lattice_vecs[1][1]))]

    # Curse povray's weird coordinate system, only the prism is affected
    # Must spawn at center, then rotate and translate later
    end = [(-0.5 * thickness), (0.5 * thickness)]

    # Defining slab vertices from lattice_vecs
    # The shape is closed later 
    # (Povray requires that the first & last points match)
    points = [
            [0, 0],
            [lattice_vecs[0][0], lattice_vecs[0][1]],
            [(lattice_vecs[0][0] + lattice_vecs[1][0]), 
                    (lattice_vecs[0][1] + lattice_vecs[1][1])],
            [lattice_vecs[1][0], lattice_vecs[1][1]]
            ]

    # Write slab layer, adding teensy extra height to prevent weird artifacts
    slab = (f"prism\n\t\t{{\n\t\t"
            + "linear_sweep \n\t\tlinear_spline \n\t\t"
            + f"{end[0]}, {end[1]*1.000001}, {len(points)+1} \n\t\t")

    for i in range(len(points)):
        points[i][0] -= halfwidth[0]
        points[i][1] -= halfwidth[1]
        slab += f"<{points[i][0]:.6f}, {points[i][1]:.6f}>, "
    slab += f"<{points[0][0]:.6f}, {points[0][1]:.6f}> \n\t\t"

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
    slab += f"translate <{x_translate}, {y_translate}, {z_translate:.6f}>"
    slab += "\n\t\t"

    return slab, halfwidth


def create_torus(major_radius, minor_radius, center, z_top, angle=0, 
        color=[0,0,0]):
    """Create and return a torus for accent line functionality.
    
    Used for adding accent lines to circular and elliptical features.
    (povray torus docs: http://wiki.povray.org/content/Reference:Torus)

    Args:
      major_radius (list or int): Radius of the circular or elliptical
          features.  It takes either the halfwidths as a list (circles
          and ellipses) or a single float/int (circles only). The
          function handles the difference automatically.
      minor_radius (float): Called "line_thickness" in other functions
      center (list): The x-,y-coordinates of the center
      z_top (float): The z-coordinate of the center
      angle (float, optional): Only relevant for elliptical pillars, 
          should they be rotated about the z-axis (default 0)
      color (list, optional): Torus color (defaults to black ([0,0,0]))

    Returns:
      str: String containing torus description

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

    torus = (f"torus\n\t\t{{\n\t\t\t"
            + f"{smaller_dim}, {minor_radius}\n\t\t\t"
            + f"pigment {{ color rgbft "
            + f"<{color[0]}, {color[1]}, {color[2]}, 0, 0> "
            + f"}}\n\t\t\t"
            + "rotate <90, 0, 0>\n\t\t\t"
            + f"translate <{center[0]}, {center[1]}, {z_top}>\n\t\t")

    # Scale dimensions to make elliptical torus
    if ratio == 0.0:
        if smaller_dim == major_radius[0]:
            ratio = major_radius[1] / major_radius[0]
            torus += f"scale <1, {ratio}, 1>\n\t\t\t"
        else:
            ratio = major_radius[0] / major_radius[1]
            torus += f"scale <{ratio}, 1, 1>\n\t\t\t"

    if angle != 0:      # in degrees
        torus += f"rotate <0, 0, {angle}> \n\t\t"

    torus += f"no_shadow\n\t\t}}\n\t"
    return torus


def create_sphere(radius, center, color=[0,0,0]):
    """Create and return a sphere for the accent line stuff.

    Args:
      radius (float): Sphere radius (this is the "line_thickness" 
          variable in the other accent line functions)
      center (list): The x-,y-,z-coordinates of the center
      color (list, optional): Torus color (defaults to black)

    Returns:
      string: povray sphere description

    """
    sphere = (f"sphere\n\t\t{{\n\t\t"
            + f"<{center[0]}, {center[1]}, {center[2]}>, {radius}\n\t\t"
            + f"pigment {{ color rgbft "
            + f"<{color[0]}, {color[1]}, {color[2]}, 0, 0> "
            + f"}}\n\t\t"
            + f"no_shadow\n\t\t}}\n\t")
    return sphere


def add_accent_lines(shape, z_top, center, dims, feature_height, angle=0, 
        line_settings=[[0,0,0], 0.0020]):
    """Generate and return feature accent lines.
    
    Users can optionally add lines to accentuate device features and
    return updated device.

    Args:
      shape (string): geometry of feature, accepts "circle", "ellipse",
          "rectangle", and "polygon"
      z_top (float): z-component of the top of the device, grab from
          device_dims (before updating)
      dims (list): Dimensions for the geometry. Required type depends 
          on ``shape``
          * "circle" requires a float (the radius),
          * "ellipse" and "rectangle" require [halfwidth1, halfwidth2],
          * "polygon" requires [point1, point2, ...]
      center (list): The center of the feature in the xy-plane 
      feature_height (float): Height of the device (required for 
          rectangles and polygons)
      angle (float, optional): Rotation angle of feature in degrees
          (default 0)
      line_settings (list, optional): Option to set the color (as rbg,
          always fully opaque) and line thickness of accent lines 
          (default [[0,0,0], 0.0020])

    Returns:
      string: Accent lines for the feature

    """
    from math import sin, cos, radians, sqrt

    line = "//Accent Lines\n\t"

    # Just doublechecking, because I've screwed this up before
    feature_height = abs(feature_height)

    color = line_settings[0]
    line_thickness = line_settings[1]

    # Must make negative to appear in proper location
    # (Reason: Top of device located at z=0 and builds down.
    # Also, device_dims stores dimensions, not coordinates)
    z_top *= -1.0

    if shape == "circle":
        # dims is the radius
        line_upper = create_torus(
                dims, line_thickness, center, z_top, angle=0, color=color)
        line_lower = create_torus(
                dims, line_thickness, center, (z_top - feature_height), 
                angle=0, color=color)
        line += line_upper
        line += line_lower

    elif shape == "ellipse":
        # dims is the halfwidths
        line_upper = create_torus(
                dims, line_thickness, center, z_top, angle=angle, color=color)
        line_lower = create_torus(
                dims, line_thickness, center, (z_top - feature_height), 
                angle=angle, color=color)
        line += line_upper
        line += line_lower

    elif shape == "rectangle":
        # dims is the halfwidths

        # Define end points for each direction, pre-rotation ([min,max])
        # write_pov() defines end = [top, bottom]
        x_limits = [(-1.0 * dims[0]), (1.0 * dims[0])]
        y_limits = [(-1.0 * dims[1]), (1.0 * dims[1])]
        z_limits = [(z_top - feature_height), z_top]

        # Declare cylinders parallel to X-,Y-,Z-axes, respectively
        # All spawn parallel to the Z-axis because create_cylinder,
        # but are then rotated into place, parallel to the axes
        x_cyl = "#declare Xcyl = "
        x_cyl += create_cylinder([0.0, 0.0], x_limits, line_thickness)
        x_cyl += (f"pigment {{ color rgbft "
                + f"<{color[0]}, {color[1]}, {color[2]}, 0, 0> }}\n\t\t"
                + "rotate <0, 90, 0>\n\t\t"
                + f"no_shadow\n\t\t}}\n\t")

        y_cyl = "#declare Ycyl = "
        y_cyl += create_cylinder([0.0, 0.0], y_limits, line_thickness)
        y_cyl += (f"pigment {{ color rgbft "
                + f"<{color[0]}, {color[1]}, {color[2]}, 0, 0> }}\n\t\t"
                + "rotate <90, 0, 0>\n\t\t"
                + f"no_shadow\n\t\t}}\n\t")

        z_cyl = "#declare Zcyl = "
        z_cyl += create_cylinder([0.0, 0.0], z_limits, line_thickness)
        z_cyl += (f"pigment {{ color rgbft "
                + f"<{color[0]}, {color[1]}, {color[2]}, 0, 0> }}\n\t\t"
                + f"no_shadow\n\t\t}}\n\t")

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


        # Need to add or subtract - not sure which 'cause left-handed - 
        # the center from the vector1 (x-coord) and vector2 (y-coord)


        # Xcyl, Ycyl
        for ii in range(2):
            vector1 = y_limits[ii] * sin(radians(angle))
            vector2 = -1.0 * y_limits[ii] * cos(radians(angle))
            for jj in range(2):
                line += (f"object {{ Xcyl "
                        + f"rotate <0, 0, {angle:.6f}>\n\t\t"
                        + "translate "
                        + f"<{vector1:.6f}, {vector2:.6f}, {z_limits[jj]:.6f}>"
                        + f"}}\n\t")

            vector1 = x_limits[ii] * cos(radians(angle))
            vector2 = x_limits[ii] * sin(radians(angle))
            for jj in range(2):
                line += (f"object {{ Ycyl "
                        + f"rotate <0, 0, {angle:.6f}>\n\t\t"
                        + "translate "
                        + f"<{vector1:.6f}, {vector2:.6f}, {z_limits[jj]:.6f}>"
                        + f"}}\n\t")

        # Zcyl, Corner
        for x in x_limits:
            for y in y_limits:
                vector1 = x * cos(radians(angle)) - y * sin(radians(angle))
                vector2 = y * cos(radians(angle)) + x * sin(radians(angle))
                line += (f"object {{ Zcyl "
                        + "translate "
                        + f"<{vector1:.6f}, {vector2:.6f}, {0:.6f}>"
                        + f"}}\n\t")
                for z in z_limits:
                    line += (f"object {{ Corner "
                            + "translate "
                            + f"<{vector1:.6f}, {vector2:.6f}, {z:.6f}>"
                            + f"}}\n\t")

        print("WARNING: add_accent_lines NOT FULLY TESTED!!!")
        print("NOT guaranteed to work if rectangle not centered at origin!!!")

    elif shape == "polygon":
        # dims is a list of corners, where element = [x_coord, y_coord]

        # Top and bottom z-coords
        z_limits = [(z_top - feature_height), z_top]

        # Create spheres to fill corners to cover rough cylinder ends
        sph = "#declare Corner = "
        sph += create_sphere(line_thickness, [0.0, 0.0, 0.0], color=[0,0,0])

        # Create cylinder along z axis
        # Not used (yet) because I've not yet come up with an algorithm
        # that can intelligently place them only where they make sense.
        z_cyl = "#declare Zcyl = "
        z_cyl += create_cylinder([0.0, 0.0], z_limits, line_thickness)
        z_cyl += (f"pigment {{ color rgbft "
                + f"<{color[0]}, {color[1]}, {color[2]}, 0, 0> "
                + f"}}\n\t\t"
                + f"no_shadow\n\t\t}}\n\t")

        # Declaring shapes
        line = sph
        #line += z_cyl

        # Create cylinders in xy-plane, both at top and bottom of shape.
        # Loop over all vertices defined in dims
        for i in range(len(dims)):

            # Define cylinder-end x-,y-coords
            end1 = dims[i]

            if len(dims) == (i+1):
                end2 = dims[0]
            else:
                end2 = dims[i + 1]

            # Create the accent lines
            for z in z_limits:

                # Add a sphere to the first of the two end points
                line += (f"object {{ Corner "
                        + "translate "
                        + f"<-{end1[0]:.6f}, -{end1[1]:.6f}, {z:.6f}>"
                        + f"}}\n\t")

                # Add cylinders for bigger straight lines
                #
                # Only create cylinders if they'll be longer than the
                # sphere radius, line_thickness, because POV-Ray
                # doesn't like really short cylinders.
                #
                # Only need the x and y coords for cylinder length
                # The z value drops out because it's horizontal
                #
                # Do I eventually want to incorporated the blob 
                # function?
                cyl_length = sqrt((end1[0] - end2[0])**2 
                        + (end1[1] - end2[1])**2)

                # Not using create_cylinder to create cylinders in the
                # xy-plane because that function only spawns cylinders
                # parallel to the z-axis. I'm sick of trying to rotate
                # things in POV-Ray's left-handed coordinate system.
                if cyl_length > line_thickness:
                    line += (f"cylinder \n\t\t{{\n\t\t "
                            + f"<-{end1[0]}, -{end1[1]}, {z:.5f}>, \n\t\t"
                            + f"<-{end2[0]}, -{end2[1]}, {z:.5f}>, \n\t\t")
                    line += f"{line_thickness}\n\t\t"
                    line += (f"pigment {{ color rgbft "
                            + f"<{color[0]}, {color[1]}, {color[2]}, 0, 0>"
                            + f"}}\n\t\t"
                            + f"no_shadow\n\t\t}}\n\t")

#            # Add vertical lines 
#            #
#            # Again, not used because there's not a way to only place
#            # them where it makes sense
#            #
#            # May eventually output this to stdout should the user
#            # want to add them manually
#            line += (f"object {{ Zcyl "
#                    + "translate "
#                    + f"<{vector1:.6f}, {vector2:.6f}, {0:.6f}>"
#                    + f"}}\n\t")

    return line


def update_device_dims(device_dims, new_x, new_y, new_z):
    """Update and return the device dimensions when adding features.
    
    Tracks maximum unit device dimensions to aid in camera placement.
    Also used to track coating thickness in the case of multiple
    coatings.
    
    These dimensions will always be positive, even though the device
    is built with the top of the device at z=0.

    Args:
      device_dims (list): Existing device dimensions
      new_x (float): x-dimensions of the newest layer
      new_y (float): x-dimensions of the newest layer
      new_z (float): Thickness of the newest layer

    Returns:
      list: Updated device dimensions

    """
    device_dims[0] = max(new_x, device_dims[0])
    device_dims[1] = max(new_y, device_dims[1])
    device_dims[2] += new_z
    return device_dims


def write_circle_feature(shapes, k, device_dims, end, 
        finish_dict, feature_color_finish, c, add_lines=False,
        line_settings=[[0, 0, 0], 0.0020]):
    """Creates a circle feature within a layer.
    
    Includes with color and finish specifications.

    Args:
      shapes (dict): The dictionary contains all shape information
      k (int): Counter iterating though features
      device_dims (list): Dimensions of the unit cell
      end (list): Limits on the z-dimensions, as [upper, lower]
      finish_dict (dict): Dictionary containing all relevant finishes
      feature_color_finish (list): List of all device colors and 
          finishes, the counter c grabs the appropriate value
      c (int): Counter iterating though custom_color
      add_lines (bool, optional): Option to add the accent lines to 
          the feature (default False)
      line_settings (list, optional): Option to set the color (as rbg,
          always fully opaque) and line thickness of accent lines 
          (default [[0,0,0], 0.0020])

    Returns:
      str: String with circle feature information

    """
    from util import deep_access

    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
    radius = deep_access(shapes, [str(k), 'shape_vars', 'radius'])

    circle = "// Circular pillar\n\t" \
            + create_cylinder(center, end, radius)

    circle = set_color_and_finish(circle, finish_dict=finish_dict,
            feature_color_finish=feature_color_finish[c])

    c += 1

    # Add lines to the top and bottom of the feature
    if add_lines == True:
        lines = add_accent_lines("circle", device_dims[2], center, 
                radius, (end[1]-end[0]), line_settings=line_settings)
        circle += lines

    device_dims = update_device_dims(device_dims, radius, radius, 0)

    return circle, c, device_dims


def write_ellipse_feature(shapes, k, device_dims, end, 
        finish_dict, feature_color_finish, c, add_lines=False,
        line_settings=[[0, 0, 0], 0.0020]):
    """Create an ellipse feature within a layer.
    
    Includes color and finish specifications.

    Args:
      shapes (dict): The dictionary contains all shape information
      k (int): Counter iterating though features
      device_dims (list): Dimensions of the unit cell
      end (list): Limits on the z-dimensions, as [upper, lower]
      finish_dict (dict): Dictionary containing all relevant finishes
      feature_color_finish (list): List of all device colors and 
          finishes, the counter c grabs the appropriate value
      c (int): Counter iterating though custom_color
      add_lines (bool, optional): Option to add the accent lines to 
          the feature (default False)
      line_settings (list, optional): Option to set the color (as rbg,
          always fully opaque) and line thickness of accent lines 
          (default [[0,0,0], 0.0020])

    Returns:
      str: String with ellipse feature information

    """
    from util import deep_access

    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
    hw = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
    halfwidths = [hw.get("x"), hw.get("y")]
    angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])

    ellipse = "// Ellipse\n\t" \
            + create_ellipse(center, end, halfwidths, angle)

    ellipse = set_color_and_finish(ellipse, finish_dict=finish_dict,
            feature_color_finish=feature_color_finish[c])
            
    # Increments through custom color list
    c += 1

    # Add lines to the top and bottom of the feature
    if add_lines == True:
        lines = add_accent_lines("ellipse", device_dims[2], center, 
                halfwidths, (end[1]-end[0]), angle=angle,
                line_settings=line_settings)
        ellipse += lines

    device_dims = update_device_dims(
            device_dims, halfwidths[0], halfwidths[1], 0)

    return ellipse, c, device_dims


def write_rectangle_feature(shapes, k, device_dims, end, 
        finish_dict, feature_color_finish, c, add_lines=False,
        line_settings=[[0, 0, 0], 0.0020]):
    """Creates a rectangle feature within a layer.
    
    Includes color and finish specifications.

    Args:
      shapes (dict): The dictionary contains all shape information
      k (int): Counter iterating though features
      device_dims (list): Dimensions of the unit cell
      end (list): Limits on the z-dimensions, as [upper, lower]
      finish_dict (dict): Dictionary containing all relevant finishes
      feature_color_finish (list): List of all device colors and 
          finishes, the counter c grabs the appropriate value
      c (int): Counter iterating though custom_color
      add_lines (bool, optional): Option to add the accent lines to 
          the feature (default False)
      line_settings (list, optional): Option to set the color (as rbg,
          always fully opaque) and line thickness of accent lines 
          (default [[0,0,0], 0.0020])

    Returns:
      str: String containing rectangle feature

    """
    from util import deep_access

    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
    hw = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
    halfwidths = [hw.get("x"), hw.get("y")]
    angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])

    rectangle = ("// Rectangle\n\t"
            + create_rectangle(center, end, halfwidths, angle))

    rectangle = set_color_and_finish(rectangle, finish_dict=finish_dict,
            feature_color_finish=feature_color_finish[c])

    # Increments through custom color list
    c += 1

    # Add lines edges of the feature
    if add_lines == True:
        lines = add_accent_lines("rectangle", device_dims[2], center, 
                halfwidths, (end[1]-end[0]), angle=angle,
                line_settings=line_settings)
        rectangle += lines

    device_dims = update_device_dims(
            device_dims, halfwidths[0], halfwidths[1], 0)

    return rectangle, c, device_dims


def write_polygon_feature(shapes, k, device_dims, end, 
        finish_dict, feature_color_finish, c, add_lines=False,
        line_settings=[[0, 0, 0], 0.0020]):
    """Create a polygon feature, with color and finish.
    
    The polygon vertices must be specified in counter-clockwise order
    for S4, but POV-Ray doesn't care about the direction as long as the
    shape is closed.

    Args:
      shapes (dict): The dictionary containing the shape information
      k (int): Counter iterating though features
      device_dims (list): Dimensions of the unit cell
      end (list): Limits on the z-dimensions, as [upper, lower]
      finish_dict (dict): Dictionary containing all relevant finishes
      feature_color_finish (list): List of all device colors and 
          finishes, the counter c grabs the appropriate value
      c (int): Counter iterating though custom_color
      add_lines (bool, optional): Option to add the accent lines to 
          the feature (default False)
      line_settings (list, optional): Option to set the color (as rbg,
          always fully opaque) and line thickness of accent lines 
          (default [[0,0,0], 0.0020])

    Returns:
      str: String with polygon feature information

    """
    from util import deep_access

    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
    angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
    points = deep_access(shapes, [str(k), 'shape_vars', 'vertices'])

    # Need to track max dimension absolute values for device_dims
    x_max = 0
    y_max = 0

    # Grab the vertices out of the points dictionary
    # Must be formatted as a list (not a numpy array), to
    # match what create_polygon expects.
    # Don't worry about closing the array here because
    # create_polygon does that for you automatically
    # Eric and his never-ending dictionaries...
    vertices = []
    for k in range(len(points)):
        vertex = [deep_access(points, [f"{k}", "x"]), 
                deep_access(points, [f"{k}", "y"])]
        vertices.append(vertex)

        x_max = max(abs(x_max), vertex[0])
        y_max = max(abs(y_max), vertex[1])

    polygon = ("// Polygon\n\t"
            + create_polygon(center, end, vertices, device_dims, angle=0))

    polygon = set_color_and_finish(polygon, finish_dict=finish_dict,
            feature_color_finish=feature_color_finish[c])
            
    # Increments through custom color list
    c += 1

    # Add lines edges of the feature
    if add_lines == True:
        lines = add_accent_lines("polygon", device_dims[2], center, 
                vertices, (end[1]-end[0]), angle=angle,
                line_settings=line_settings)
        polygon += lines

    device_dims = update_device_dims(device_dims, x_max, y_max, 0)

    return polygon, c, device_dims


def check_for_false_silos(shapes, layer_type):
    """Remove 'silos' that aren't actually silos.
    
    'False silos' are instances where the layer to be subtracted has a
    dimension of zero. POV-Ray fill crash if given a 'false silo'.
    This function keeps POV-Ray happy by resetting all 'false silos'
    to the fully solid shape.

    Args:
      shapes (dict): The dictionary containing the shape information
      layer_type (str): The type of the layer as a string

    Returns:
      str: Updated string without the false silo

    """
    from util import deep_access

    for iii in range(len(layer_type)-1):
        if layer_type[iii] != "Vacuum" and layer_type[iii+1] == "Vacuum":
            layer_shape = deep_access(shapes, [str(iii+1), 'shape'])

            # Checks shapes containing radii for zero dimensions
            if layer_shape == "circle" and deep_access(
                    shapes, [str(iii+1), 'shape_vars', 'radius']) == 0:
                print("Warning: Ignoring vacuum with dimensions equal to zero")

            # Checks shapes containing halfwidths for zero dimensions         
            elif layer_shape in ["ellipse", "rectangle"] and deep_access(
                    shapes, 
                    [str(iii+1), 'shape_vars', 'halfwidths']) == [0, 0]:
                print("Warning: Ignoring vacuum with dimensions equal to zero")

            # Checks that polygons have at least 3 points
            elif layer_shape == "polygon" and len(deep_access(
                    shapes, [str(iii+1), 'shape_vars', 'vertices'])) < 3:
                print("Warning: Ignoring vacuum with dimensions equal to zero")
                print("WARNING: Polygon false silo test has not been tested!")

            # Is actually a silo
            else:
                layer_type[iii] = "silo"

    return layer_type


def write_silo_feature(shapes, k, layer_type, device_dims, end, 
        finish_dict, feature_color_finish, c, add_lines=False,
        line_settings=[[0, 0, 0], 0.0020]):
    """Create a silo feature, with color and finish.
    
    Creates a silo. Should be able to handle any possible combination
    of features, including multiple holes in a single feature.

    Args:
      shapes(dict): The dictionary containing the shape information
      k(int): Counter iterating though features
      layer_type (str): The type of the layer as a string
      device_dims(list): Dimensions of the unit cell
      end(list): Limits on the z-dimensions, as [upper, lower]
      finish_dict (dict): Dictionary containing all relevant finishes
      feature_color_finish (list): List of all device colors and 
          finishes, the counter c grabs the appropriate value
      c (int): Counter iterating though custom_color
      add_lines (bool, optional): Option to add the accent lines to 
          the feature (default False)
      line_settings (list, optional): Option to set the color (as rbg,
          always fully opaque) and line thickness of accent lines 
          (default [[0,0,0], 0.0020])

    Returns:
      tuple: a string describing the silo, the color counter, and
      updated device_dims

    """
    from util import deep_access
    from copy import deepcopy

    device = "// Silo\n\t" \
            + f"difference \n\t\t{{\n\t\t"

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
        center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
        hw = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
        halfwidths = [hw.get("x"), hw.get("y")]
        angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
        device += create_rectangle(
                center, end, halfwidths, angle, for_silo=True)
        print("WARNING: this function has not been tested in silos!!")

        # Set up for add_lines=True, even if not actually used
        shape = "rectangle"
        dims_outer = deepcopy(halfwidths)

    elif deep_access(shapes, [str(k), 'shape']) == "polygon":
        center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
        angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
        points = deep_access(shapes, [str(k), 'shape_vars', 'vertices'])
        vertices = []
        for k in range(len(points)):
            vertex = [deep_access(points, [f"{k}", "x"]),
                    deep_access(points, [f"{k}", "y"])]
            vertices.append(vertex)
        device += create_polygon(
                center, end, vertices, device_dims, angle, for_silo=True)
        print("WARNING: this function has not been tested in silos!!")

        # Set up for add_lines=True, even if not actually used
        shape = "polygon"
        dims_outer = deepcopy(vertices)

    else:
        print("ERROR: This shape is not supported!!")

    # Create line to the top of the feature, added later
    # Also storing outer radius for later
    if add_lines == True:
        lines = add_accent_lines(shape, device_dims[2], center, 
                dims_outer, (end[1]-end[0]), line_settings=line_settings)

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
            center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
            hw = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
            halfwidths = [hw.get("x"), hw.get("y")]
            angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
            device += create_ellipse(
                    center, end2, halfwidths, angle, for_silo=True)
            print("WARNING: this function has not been tested in silos!!")

            # Set up for add_lines=True, even if not actually used
            shape = "ellipse"
            dims_inner = deepcopy(halfwidths)

        elif deep_access(shapes, [str(j), 'shape']) == "rectangle":
            center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
            hw = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
            halfwidths = [hw.get("x"), hw.get("y")]
            angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
            device += create_rectangle(
                    center, end2, halfwidths, angle, for_silo=True)
            print("WARNING: this function has not been tested in silos!!")

            # Set up for add_lines=True, even if not actually used
            shape = "rectangle"
            dims_inner = deepcopy(halfwidths)

        elif deep_access(shapes, [str(j), 'shape']) == "polygon":
            center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
            angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
            points = deep_access(shapes, [str(k), 'shape_vars', 'vertices'])
            vertices = []
            for k in range(len(points)):
                vertex = [deep_access(points, [f"{k}", "x"]),
                        deep_access(points, [f"{k}", "y"])]
                vertices.append(vertex)
            device += create_polygon(
                    center, end, vertices, device_dims, angle, for_silo=True)

            print("WARNING: this function has not been tested in silos!!")

            # Set up for add_lines=True, even if not actually used
            shape = "polygon"
            dims_inner = deepcopy(vertices)

        else:
            print("ERROR: This shape is not supported!!")

        # Create inner lines and append to the silo master list
        if add_lines == True:
            lines_inner = add_accent_lines(shape, device_dims[2], center, 
                    dims_inner, (end[1]-end[0]), line_settings=line_settings)
            lines += lines_inner

        j += 1

    device = set_color_and_finish(device, finish_dict=finish_dict,
            feature_color_finish=feature_color_finish[c])

    # Increments through custom color list
    c += 1

    # Add all silo lines
    if add_lines == True:
        device += lines

    device_dims = update_device_dims(
            device_dims, halfwidths[0], halfwidths[1], 0)

    return device, c, device_dims


def create_device_layer(shapes, device_dims, end, thickness,
        finish_dict, feature_color_finish, c, add_lines=False,
        line_settings=[[0, 0, 0], 0.0020]):
    """Generate a single layer of a device.
    
    Called by create_device, which creates the full unit cell. Adds a
    color and finish to each feature as it's created.

    Args:
      shapes (dict): The dictionary containing the shape information
      k (int): Counter iterating though features
      device_dims (list): Dimensions of the unit cell
      end (list): Limits on the z-dimensions, as [upper, lower]
      thickness (float): thickness of the layer
      finish_dict (dict): Dictionary containing all relevant finishes
      feature_color_finish (list): List of all device colors and 
          finishes, the counter c grabs the appropriate value
      c (int): Counter iterating though custom_color, resets to 0 when
          equal to ``len(feature_color_finish)`` to prevent overflow
          errors and force the code to cycle through the color list
          again
      add_lines (bool, optional): Option to add the accent lines to 
          the feature (default False)
      line_settings (list, optional): Option to set the color (as rbg,
          always fully opaque) and line thickness of accent lines 
          (default [[0,0,0], 0.0020])

    Returns:
      tuple: a string describing the silo, the color counter, and
      updated device_dims

    """
    from util import deep_access

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

        if c == len(feature_color_finish):
            c = 0

        if layer_type[k] == "circle":
            feature, c, device_dims = write_circle_feature(shapes, k, 
                    device_dims, end, finish_dict, feature_color_finish, 
                    c, add_lines, line_settings)
            device_layer += feature

        elif layer_type[k] == "silo":
            feature, c, device_dims = write_silo_feature(shapes, k,
                    layer_type, device_dims, end, finish_dict,
                    feature_color_finish, c, add_lines, line_settings)
            device_layer += feature

        elif layer_type[k] == "ellipse":
            feature, c, device_dims = write_ellipse_feature(shapes, k, 
                    device_dims, end,  finish_dict, feature_color_finish, 
                    c, add_lines, line_settings)
            device_layer += feature

        elif layer_type[k] == "rectangle":
            feature, c, device_dims = write_rectangle_feature(shapes, k, 
                    device_dims, end, finish_dict, feature_color_finish, 
                    c, add_lines, line_settings)
            device_layer += feature

        elif layer_type[k] == "polygon":
            feature, c, device_dims = write_polygon_feature(shapes, k, 
                    device_dims, end, finish_dict, feature_color_finish,
                    c, add_lines, line_settings)
            device_layer += feature

        elif layer_type[k] == "Vacuum":
            k = k

        else:
            print("\nWARNING: Invalid or unsupported layer specified.\n")

    # End of device layer (update thickness and close union
    device_dims = update_device_dims(device_dims, 0, 0, thickness)
    device_layer += f"}}\n\t"

    return device_layer, c, device_dims


def create_device(device_dict, 
    feature_color_finish,
    num_UC_x=2,
    num_UC_y=2,
    coating_layers=[], 
    coating_color_dict={"translucent":[1, 0, 0, 0, 0]}, 
    coating_ior_dict={"translucent":1.0}, 
    custom_finish="", 
    add_lines=False,
    line_color=[0, 0, 0],
    line_thickness=0.0020):
    """Generates a string containing the device information.
    
    The required input information is
    * device_dict (the dictionary entry from the json file)
    * feature_color_finish (list of feature colors and finishes)

    The color and finish of the device can be specified by the user
    via ``feature_color_finish``. The substrate will always be a 
    dull, dark grey; this cannot be modified by the user, except 
    directly in the .pov file.
    
    Some assumptions:
    * All shapes describing holes in silos are the vacuum layers
      immediately following the shape layer
    * xy-plane is centered at 0
    
    Returns a tuple containing
    * a string containing the device information (device)
    * the device dimensions (device_dims)
    * the coating dimensions (coating_dims)

    Args:
      device_dict (dict): Dictionary entry from a json file
      feature_color_finish (list): List of all device colors and 
          finishes, the counter c grabs the appropriate value
      num_UC_x (int, optional): Number of unit cells in the y direction
          (default 2)
      num_UC_y (int, optional): Number of unit cells in the y direction
          (default 2)
      coating_color_dict (dict,optional): Dictionary containing color
          definitions as RGBFT for each coating material (Default value
          = {"background":[1, 0, 0, 0, 0]})
      coating_ior_dict (dict,optional): Dictionary containing index of
          refraction values for each coating material (Default value = 
          {"background":1.0})
      coating_layers (list, optional): List containing material and
          thickness of each layer, starting with the bottom layer and
          working up (Default value = [])
      coating_color_dict (dict: dict): Dictionary of color def-
          initions for all coating layers present
      coating_ior_dict (dict: dict): Dictionary containing ior 
          definitions for all coating layers present
      custom_finish (list): User-defined custom finishes. Accepts a
          list of entries as ["key", "finish"]. (Please refer to the
          ``set_color_and_finish`` function and POV-Ray's documentation
          for custom finish string formatting and possible values
      add_lines (bool, optional): Add accent lines to highlight shape
          edges (default False)
      line_color(list, optional): Option to set accent line color as
          rbg, always fully opaque (default [0,0,0])
      line_thickness(float, optional): Option to set accent line 
          thickness (default 0.0020)

    Returns:
      tuple: a string describing the device, updated device dimensions,
      and updated coating dimensions

    """
    from os import system
    from copy import deepcopy
    from util import deep_access
    from util_pov import guess_camera, write_header_and_camera, render_pov

    # Combine accent line color and thickness into a single variable
    # to simplify variable passing
    line_settings=[line_color, line_thickness]

    # Starting the rewriting of color and finish functionality
    finish_dict = create_finish_dict(custom_finish=custom_finish, 
                       coating_ior_dict=coating_ior_dict)

    number_of_layers = deep_access(device_dict, ['statepoint', 'num_layers'])

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
    device += f"merge\n\t{{\n\t"

    # Create all layers
    for i in range(number_of_layers):

        shape_type = deep_access(device_dict, 
                ['statepoint', 'dev_layers', str(i)]).get('shapes')
        if shape_type is not None:
            shapes = deep_access(device_dict, 
                    ['statepoint', 'dev_layers', str(i), 'shapes'])
            background = deep_access(device_dict, 
                    ['statepoint', 'dev_layers', str(i), 'background'])
            thickness = deep_access(device_dict, 
                    ['statepoint', 'dev_layers', str(i), 'thickness'])
            # end = [top, bottom]
            end = [float(-1.0*device_dims[2]), 
                    float(-1.0*device_dims[2] - thickness)]

            device += f"union\n\t{{\n\t"

            # Check for background material
            bg_slab = ""
            #if background != "Vacuum":
            if background in coating_color_dict:
                # Forcing elimination of internal boundaries
                # (They appear if you use lattice_vecs 
                # instead of temp_vecs)
                temp_vecs = deepcopy(lattice_vecs)
                for k in range(2):
                    for l in range(2):
                        temp_vecs[k][l] += 0.0002

                # Make sure that coating color is rgbft.
                #
                # Override filter and transmit values to match the
                # "translucent" finish settings if they are set to 0.
                # This way the user can still specify custom filter
                # and transmit values, but if they truly want an opaque
                # coating, they can use something like 0.0000001.
                coating_color = coating_color_dict[coating_layers[j][0]]
                if len(coating_color) < 5:
                    coating_color.append(0)
                if coating_color[3] == 0:
                    coating_color[3] = 0.50
                if coating_color[4] == 0:
                    coating_color[4] = 0.02
    
                coating_finish = coating_layers[j][0]

                device += "// Layer background\n\t"
                bg_slab, halfwidth = add_slab(temp_vecs, thickness, 
                        device_dims, layer_type="background")
                bg_slab = set_color_and_finish(bg_slab, 
                        finish_dict=finish_dict,
                        feature_color_finish=[coating_color, coating_finish])

                device += bg_slab

                # Prevent end caps from being overwritten by background layers
                end[0] -= 0.00010
                end[1] -= 0.00010

            # Create all features within a layer
            ####### Need to pass finish_dict !! set_color_and_finish
            layer, c, device_dims = create_device_layer(shapes, device_dims, 
                    end, thickness, finish_dict, feature_color_finish, c, 
                    add_lines, line_settings)
            device += layer

    # End unit cell merge
    device += f"}}\n\n"

    #### ---- REPLICATE UNIT CELL ---- ####

    # Shift translation so that the original device is roughly in the center
    device += f"merge\n\t{{ \n\t"

    adj_x = int(0.5 * (num_UC_x - (1 + (num_UC_x - 1) % 2)))
    adj_y = int(0.5 * (num_UC_y - (1 + (num_UC_y - 1) % 2)))
    # Explanation: 
    # Subtracts 1 because one row stays at origin
    # Uses modulo to subtract again if odd number
    # Sends half of the remaining rows backward

    for i in range(num_UC_x):
        for j in range(num_UC_y):
            translate_x = ((i-adj_x)*lattice_vecs[0][0]
                           - (j-adj_y)*lattice_vecs[1][0])
            translate_y = ((j-adj_y)*lattice_vecs[1][1]
                           - (i-adj_x)*lattice_vecs[0][1]) 
            device += (f"object {{ UnitCell translate "
                    + f"<{translate_x}, {translate_y}, 0> }}\n\t")

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
            device += "// Coating layer {j+1}\n\t"
            coating, halfwidth = add_slab(temp_vecs, coating_layers[j][1], 
                    coating_dims, layer_type="coating")

            # Make sure that coating color is rgbft.
            #
            # Override filter and transmit values to match the
            # "translucent" finish settings if they are set to 0.
            # This way the user can still specify custom filter and
            # transmit values, but if they truly want an opaque 
            # coating, they can use something like 0.0000001.
            coating_color = coating_color_dict[coating_layers[j][0]]
            while len(coating_color) < 5:
                coating_color.append(0)
            if coating_color[3] == 0:
                coating_color[3] = 0.50
            if coating_color[4] == 0:
                coating_color[4] = 0.02

            coating_finish = coating_layers[j][0]

            coating = set_color_and_finish(coating, finish_dict=finish_dict,
                        feature_color_finish=[coating_color, coating_finish])
            device += coating

            coating_dims = update_device_dims(
                    coating_dims, 0, 0, coating_layers[j][1])

    # End device and coating merge
    device += f"}}\n\n"

    # Substrate
    device += "// Substrate\n\t"
    thickness_sub = max(1, deep_access(
        device_dict, ['statepoint', 'sub_layer', 'thickness']))

    substrate, halfwidth = add_slab(
            temp_vecs, thickness_sub, substrate_dims, layer_type="substrate")
    device += substrate

    device = set_color_and_finish(device, finish_dict=finish_dict,
            feature_color_finish=[[0.15, 0.15, 0.15, 0, 0], "dull"])

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
        n, 
        cut_at=[[0.5, 1], [0.5, 1], [0, 1]],
        use_slice_UC=True, 
        subtract_box=True):
    """Generate a device string for use with isosurfaces.
    
    This function is meant only for use with isosurfaces because the
    isosurface center and scaling is different than normal devices.
    The device color and finish selection is hard coded in, as the
    unit cell is not the focus of the rendering with isosurfaces.
    This function does not include the ability to replicate the unit
    cell or the abiility to add accent lines. It does, however,
    automatically add a substrate.

    The unit cell and substrate color and finish are hard coded in
    this function and can only be changed directly in the .pov file.
    Both use the "dull" finish, and the colors are set as follows:
    * device color: [0.25, 0.25, 0.25, 0, 0]
    * substrate color: [0.025, 0.025, 0.025, 0, 0]
    
    The required input information is
    * the isosurface mesh
    * the device dictionary
    * the isosurface dimensions

    Args:
      mesh (str): the mesh object describing the isosurface
      device_dict (dict): Dictionary entry from a json file
      n (list): Dimensions of the numpy field array as [nx, ny, nz],
          used as the isosurface dimensions
      cut_at (list): Specify the section to remove, as a fraction of
          the unit cell, defaults to removing the quadrant nearest the
          camera if used with the automatic camera guess function
      use_slice_UC(bool, optional): Gives you the option to take a
          slice out of the unit cell to help visualize the field
          (default True)
      subtract_box(bool, optional): Controls whether POV-Ray uses a
          difference object (True, default) or an intersection (False)

    Returns:
      str: Unit cell string specifically for use with isosurfaces

    """
    from util import deep_access
    from util_iso import slice_isosurface
    from util_shapes import create_device_layer

    # Create the finish dictionary only using "dull"
    finish_dict = {'dull': ''}

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
    device += f"merge {{\n\t"

    # Create all layers
    feature_color_finish=[[[0.25, 0.25, 0.25, 0, 0], "dull"]]

    for i in range(number_of_layers):
        if deep_access(device_dict, 
                ['statepoint', 'dev_layers', 
                    str(i)]).get('shapes') is not None:
            shapes = deep_access(device_dict, 
                    ['statepoint', 'dev_layers', str(i), 'shapes'])
            background = deep_access(device_dict, 
                    ['statepoint', 'dev_layers', str(i), 'background'])
            thickness = deep_access(device_dict, 
                    ['statepoint', 'dev_layers', str(i), 'thickness'])
            # end = [top, bottom]
            end = [float(-1.0 * device_dims[2]), 
                    float(-1.0 * device_dims[2] - thickness)]

            device += f"union\n\t{{\n\t"

            # Create all features within a layer
            layer, c, device_dims = create_device_layer(shapes, device_dims, 
                    end, thickness, finish_dict, feature_color_finish, c, 
                    add_lines=False)
            device += layer

    # End unit cell merge
    device += f"}}\n\n"

    # Scale unit cell up to match field dimensions
    scaling_factor = n[0] / lattice_vecs[0][0]

    translate_x = 0.5 * (device_dims[0] + n[0])
    translate_y = 0.5 * (device_dims[1] + n[1])
    translate_z = n[2] - device_dims[2]

    device += f"object {{ UnitCell "
    device += "\n\tscale <{0}, {0}, {0}> ".format(scaling_factor)
    device += f"\n\ttranslate <{translate_x}, {translate_y}, {translate_z}> "
    device += f"\n\t}}\n\n"

    # Can also subtract out pieces of the unit cell, 
    if use_slice_UC == True:
        device = slice_isosurface(device, n, cut_at=cut_at, 
                                  subtract_box = subtract_box)

    # Add substrate
    feature_color_finish=[[[0.025, 0.025, 0.025, 0, 0], "dull"]]

    lattice_x = lattice_vecs[0][0] + lattice_vecs[1][0]
    lattice_y = lattice_vecs[1][0] + lattice_vecs[1][1]
    for i in range(2):
        if lattice_vecs[i][0] != 0:
            lattice_vecs[i][0] = n[0] * lattice_x / lattice_vecs[i][0]
        if lattice_vecs[i][1] != 0:
            lattice_vecs[i][1] = n[1] * lattice_y / lattice_vecs[i][1]

    (substrate, garbage) = add_slab(lattice_vecs, thickness=n[2]/3.5,
            device_dims=n, layer_type="isosurface")

    substrate = set_color_and_finish(substrate, finish_dict=finish_dict,
            feature_color_finish=[[0.025, 0.025, 0.025, 0, 0], "dull"])

    # Append unit cell to mesh object
    mesh += device
    mesh += substrate 

    return mesh


def create_finish_dict(custom_finish=[], coating_ior_dict=None):
    """Create dictionary for device finishes.
    
    Available default finishes: "Si", "silicon", "SiO2", "translucent",
        "glass", "bright_metal", "dull_metal", "irid", "billiard", and
        "dull"

    The "translucent" finish will always have ior=1. 

    If coating_ior_dict exists, the returned dictionary will also
    contain auto-generated finishes with the same name as the coatings.

    Users may specify their own custom finish with the custom finish
    variable.

    If the users ever attempts to call a finish not in this dictionary,
    the feature will use the "dull" finish by default.

    Args:
      coating_ior_dict (dict, optional): Dictionary containing the
          coating name and index of refraction for coatings. 
          (Default value = None)
      custom_finish (list, optional): User-defined custom finish. List
          entries must be in the form ["key", "finish_string"]
          (Default value = [])

    Returns:
      dict: All possible finishes for the device

    """
    # Create dictionary of finishes
    finish_keys = []
    finish_strings = []

    # Silicon
    finish = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "diffuse 0.2 \n\t\t\t"
                + "brilliance 5 \n\t\t\t"
                + "phong 1 \n\t\t\t"
                + "phong_size 250 \n\t\t\t"
                + "roughness 0.01 \n\t\t\t"
                + "reflection <0.10, 0.10, 0.5> metallic \n\t\t\t"
                + " metallic \n\t\t\t"
                + f"}}\n\t\t"
                + f"interior {{ ior 4.24 }}\n\t\t")
                # IOR taken from blender
    finish_keys.append("Si")
    finish_keys.append("silicon")
    finish_strings.append(finish)
    finish_strings.append(finish)
    
    # SiO2
    finish = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "specular 0.6 \n\t\t\t"
                + "brilliance 5 \n\t\t\t"
                + "roughness 0.001 \n\t\t\t"
                + f"reflection {{ 0.0, 1.0 fresnel on }}\n\t\t\t"
                + f"}}\n\t\t"
                + f"interior {{ ior 1.45 }}\n\t\t")
    finish_keys.append("SiO2")
    finish_strings.append(finish)

    # Translucent and coatings base string, no IOR
    finish_temp = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "emission 0.10 \n\t\t\t"
                + "diffuse 0.85 \n\t\t\t"
                + "specular 0.4 \n\t\t\t"
                + "brilliance 4 \n\t\t\t"
                + f"reflection {{ 0.5 fresnel on }}\n\t\t\t"
                + f"}}\n\t\t")

    # Plain old translucent (IOR=1)
    finish = (finish_temp 
            + f"interior {{ ior 1.0 }}\n\t\t")
    finish_keys.append("translucent")
    finish_strings.append(finish)

    # Coating-specific translucent (specified IORs)
    # Grabs coating names from coating_ior_dict
    if coating_ior_dict is not None:
        coating_list = list(coating_ior_dict.keys())
        for i in range(len(coating_list)):
            ior = coating_ior_dict[coating_list[i]]
            finish = (finish_temp
                      + f"interior {{ ior {ior} }}\n\t\t")
            finish_keys.append(coating_list[i])
            finish_strings.append(finish)

    # Glass
    finish = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "phong 0.8 \n\t\t\t"
                + "phong_size 100 \n\t\t\t"
                + "brilliance 5 \n\t\t\t"
                + f"reflection {{ 0.2, 1.0 fresnel on }}\n\t\t\t"
                + f"}}\n\t\t"
                + f"interior {{ ior 1.5 }}\n\t\t")
    finish_keys.append("glass")
    finish_strings.append(finish)

    # Dull metal
    finish = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "emission 0.1 \n\t\t\t"
                + "diffuse 0.1 \n\t\t\t"
                + "specular 1.0 \n\t\t\t"
                + "roughness 0.001 \n\t\t\t"
                + "reflection 0.5 metallic \n\t\t\t"
                + " metallic \n\t\t\t"
                + f"}}\n\t\t")
    finish_keys.append("dull_metal")
    finish_strings.append(finish)

    # Bright metal
    finish = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "emission 0.2 \n\t\t\t"
                + "diffuse 0.3 \n\t\t\t"
                + "specular 0.8 \n\t\t\t"
                + "roughness 0.01 \n\t\t\t"
                + "reflection 0.5 metallic \n\t\t\t"
                + " metallic \n\t\t\t"
                + f"}}\n\t\t")
    finish_keys.append("bright_metal")
    finish_strings.append(finish)

    # Irid
    finish = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "phong 0.5 \n\t\t\t"
                + f"reflection {{ 0.2 metallic }}\n\t\t\t"
                + "diffuse 0.3 \n\t\t\t"
                + f"irid {{ 0.75 thickness 0.5 "
                + f"turbulence 0.5 }}\n\t\t\t"
                + f"}}\n\t\t"
                + f"interior {{ ior 1.5 }}\n\t\t")
    finish_keys.append("irid")
    finish_strings.append(finish)

    # Billiard
    finish = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "ambient 0.3 \n\t\t\t"
                + "diffuse 0.8 \n\t\t\t"
                + "specular 0.2 \n\t\t\t"
                + "roughness 0.005 \n\t\t\t"
                + "metallic 0.5 \n\t\t\t"
                + f"}}\n\t\t")
    finish_keys.append("billiard")
    finish_strings.append(finish)

    # Dull
    finish_keys.append("dull")
    finish_strings.append("")

    # Add custom finishes
    if custom_finish != []:
        for i in range(len(custom_finish)):
            key = custom_finish[i][0]
            assert key.find(" ") != -1,\
                    "Error: you cannot have spaces in finish names"
            finish_keys.append(custom_finish[i][0])
            finish_strings.append(custom_finish[i][1])

    # Create dictionary
    finish_dict = dict(zip(finish_keys, finish_strings))

    return finish_dict


def set_color_and_finish(dev_string, finish_dict = None,
        feature_color_finish=[[0, 0.6667, 0.667, 0, 0], "dull"]):
    """Set object color and finish and return the updated string.

    If finish_dict does not exist or is not passed as an argument,
    this function will generate its own (emergency) version that does
    NOT contain any custom or coating finishes.

    See the ``create_finish_dict()`` documentation for the list of 
    available finishes. If the requested finish is not available, it 
    defaults to "dull".

    The device color and finish is appended to the device string.

    The filter and transmit terms are both 0 by default, with the
    exception of types requiring transparency: "SiO2", "translucent",
    all coating finishes, "glass", and "irid". If you request one of
    those finishes, the code will overwrite your transmit and filter
    values. If you do now want this to happen, you should declare your
    own custom finish. All other finishes, including custom ones, use
    the filter and transmit values specified by the user.

    Args:
      dev_string (str): String describing the device
      finish_dict (dict, optional): Dictionary containing all
          relevant finishes
      feature_color_finish (list, optional): List of all device colors
          and finishes, the counter c grabs the appropriate value

    Returns:
      string: Updated device string containing color and finish settings

    """
    import os

    # Extract color
    color = feature_color_finish[0]
    assert isinstance(color, str) or isinstance(color, list),\
            "Error: wrong type for color, must be string or list"
    if isinstance(color, str):
        print("Using color from the POV-Ray include files.")
        use_colors_inc = True
    else:
        use_colors_inc = False

    # Extract finish
    use_finish = feature_color_finish[1]
    assert isinstance(use_finish, str),"Error: finish type must be a string"
    if use_finish.find(" ") == -1:
        use_finish_inc = False
    else:
        print("Using finish from the POV-Ray include files.")
        use_finish_inc = True

    # Create the finish dictionary if it doesn't already exist.
    # The finish_dict does not include custom finishes or coatings
    # if created here. This is more of an emergency backup plan
    # than anything. I may eventually make it raise an exception
    # instead.
    if finish_dict == None:
        finish_dict = create_finish_dict()

    # Make sure that the selected finish is in finish_dict
    if use_finish not in finish_dict and use_finish_inc == False:
        print("WARNING: Key '{use_finish}'not in the dictionary!")
        print("         Changing finish key to 'dull' and proceeding!")
        use_finish = "dull"

    # Use a color from the include files
    if use_colors_inc:
        dev_string += (f"pigment {{ {color} }}\n\t\t")
    # Use a color NOT from the include files
    else:
        # Make sure that color is in rgbft format (5 entries). Lists
        # that are too short (<3) or too long (>5) should have been
        # caught by the exception above.
        if len(color) < 5:
            while len(color) != 5:
                color.append(0)

        # The filter and transmit values matter for the "SiO2", "glass",
        # "translucent", and "irid" finishes, and this function will
        # override anything specified by the user!
        #
        # All other finishes (including coatings!): filter and transmit
        # are set to 0 by default, but the user may specify other
        # values. The code will never override these values for these
        # finishes.
        #
        # color[3] is filter, color[4] is transmit
        if use_finish in ["SiO2", "translucent", "glass", "irid"]: 
            print("\nWARNING: Overriding the transmit and/or filter values!!")
            if use_finish == "SiO2":
                color[3] = 0.98
            elif use_finish == "translucent":
                color[4] = 0.02
                color[3] = 0.667
            elif use_finish == "glass":
                color[3] = 0.95
            elif use_finish == "irid":
                color[3] = 0.7

        dev_string += (f"pigment {{ color rgbft "
                + f"<{color[0]}, {color[1]}, {color[2]}, {color[3]}, {color[4]}>"
                + f" }}\n\t\t")

    # Add finish from include files
    if use_finish_inc:
        dev_string += (f"finish {{ {use_finish} }}\n\t\t")
    # Add finish NOT from include
    else:
        dev_string += finish_dict[use_finish]

    # Close object
    dev_string += f"}}\n\n\t"

    return dev_string

