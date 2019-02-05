def write_pov(device_dict, pov_name, image_name, \
        height = 800, width = 800, \
        num_UC_x = 5, num_UC_y = 5, \
        camera_style = "perspective", \
        camera_rotate = 60, ortho_angle = 30, \
        camera_loc = [], look_at = [0,0,0], light_loc = [], \
        up_dir = [0, 0, 1.33], right_dir = [0, 1, 0], sky = [0, 0, 1.33], \
        shadowless = False, add_edge_buffer = False, \
        bg_color = [1.0, 1.0, 1.0], transparent = True, antialias = True, \
        use_default_colors = True, custom_colors = [[0, 0.667, 0.667]], \
        use_finish = "", custom_finish = "", \
        display = False, render = True, open_png = True):

    """ Generates a .pov and optionally render an image from a json file.
        device_dict, pov_name, and image_name are the only required 
        values.
        - device_dict is the dictionary entry from the json file
        - pov_name is the name for the generated .pov file
        - image_name is the name for the image that will be rendered

        By default, the code will generate a .pov file, render an image
        and open it post-render with eog.

        The code will always include (in STDOUT) the command to render
        the image with the selected render options, even if it is only
        creating a .pov file (not rendering).

        Rendering options:
        transparent : the background will be transparent
        antialias : can turn antialiasing on or off
        display : will display render progress
        render : call povray to render the image if True
        open_png : will open a successfully rendered image

        Color options: 
        bg_color = background color 

        use_default_colors 
         = True will set the color based on the material.
        Current materials: "Si" | "SiO2" | "subst"
         = False allows for use of a custom color, which
        is specified in custom_color. Currently only one custom color per
        device, and it defaults to #00aaaa (Windows 95 desktop color)

        Included finishes: 
        "material" | "Si" | "SiO2" | "glass" | "dull_metal" | "bright_metal" |
        | "irid" | "billiard" | *"dull" | "custom"
        (* indicates the default)
        Specifying "material" will use the appropriate material ("Si" 
        or "SiO2") finish in order to accomodate multiple material types 
        in a device. The substrate will always have the "dull" finish.

        If using the "custom" finish, the finish details must be specified 
        in the custom_finish variable (see color_and_finish function for 
        examples) or it will default to "dull".

        Substrate color and finish:
        Dull,  dark grey. Ccannot be modified by the user.

        Optional buffer:
        Can add one unit cell thickness to substrate to minimize washout
        from background by setting add_edge_buffer = True

        Camera:
        Currently only perspective and orthographic styles are supported.

        If no camera is specified, it will default to perspective.

        The orthographic camera will automatically assign angle 30; 
        assign other angles by changing ortho_angle.

        If any of the color and light parameters are missing, the code 
        will guess the appropriate values. The distance between the camera 
        ond the central unit cell is determined by the number of unit 
        cells, but capped at the distance calculated for 5 unit cells.

        The directions up, right, and sky determine image scaling and 
        which dimension points in which direction. These can be modified,
        but there's no real need for that.

        The following camera settings generate the same dimensions, 
        but the second one has more whitespace at top and bottom: 
        height=800, width=4/3.0*height, up_dir=[0,0,1], right_dir=[0,1,0], sky=up_dir
        height=800, width=height, up_dir=[0,0,1.333], right_dir=[0,1,0], sky=up_dir

        Some additional assumptions:
        - All shapes describing holes in silos are the vacuum layers
        immediately following the shape layer
        - xy-plane is centered at 0
    """

    from os import system
    from copy import deepcopy
    from util import deep_access
    from util_pov import update_device_dims, guess_camera, color_and_finish
    from util_pov import create_cylinder, create_ellipse, create_rectangle, create_polygon

    fID = open(pov_name,'w')

    default_color_dict = {
            "subst": [0.15, 0.15, 0.15], 
            "Si":[0.2, 0.2, 0.2], 
            "SiO2":[0.99, 0.99, 0.96]
            }

    number_of_layers = deep_access(device_dict, ['statepoint', 'num_layers'])

    # Set up custom color dictionary
    orig_custom_colors = deepcopy(custom_colors)

    # Assumes no more than THREE shapes per layer
    if not use_default_colors:
        while len(custom_colors) < 3 * number_of_layers:
            for i in range(len(orig_custom_colors)):
                custom_colors.append(orig_custom_colors[i])

    c = 0       # Counter for incrementing through colors

    device_dims = [0, 0, 0] # Tracks dimensions of the unit cell
    device = ""             # Will store the device

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
    #background_0L = deep_access(device_dict, ["statepoint", "zero_layer", "background"])
    #thickness_0L = deep_access(device_dict, ["statepoint", "zero_layer", "thickness"])

    # Device layers
    device += "#declare UnitCell = "
    device += "merge\n\t{ob:c}\n\t".format(ob=123)

    #for i in range(deep_access(device_dict, ['statepoint', 'num_layers'])):
    for i in range(number_of_layers):

        if deep_access(device_dict, ['statepoint', 'dev_layers', str(i)]).get('shapes') is not None:
            shapes = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'shapes'])
            thickness = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'thickness'])
            end = [(-1.0 * device_dims[2]), (-1.0 * device_dims[2] - thickness)]
            # end = [top, bottom]

            # Determine layer types
            layer_type = []
            has_silo = False
            for ii in range(len(shapes)):
                if deep_access(shapes, [str(ii), 'material']) in ["Vacuum", "vacuum"]:
                    layer_type.append("Vacuum")
                    has_silo = True
                else:
                    layer_type.append(deep_access(shapes, [str(ii), 'shape']))

            if has_silo == True:
                for iii in range(len(layer_type)-1):
                    if layer_type[iii] != "Vacuum" and layer_type[iii+1] == "Vacuum":
                        layer_type[iii] = "silo"

            # Write device layers
            for k in range(len(layer_type)):

                if layer_type[k] == "circle":
                    material = deep_access(shapes, [str(k), 'material'])
                    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
                    radius = deep_access(shapes, [str(k), 'shape_vars', 'radius'])

                    device += create_cylinder(center, end, radius)

                    device = color_and_finish(device, default_color_dict, material, \
                            use_default_colors, custom_color = custom_colors[c], \
                            use_finish = use_finish, custom_finish = custom_finish)

                    if not use_default_colors:
                        c += 1

                    device_dims = update_device_dims(device_dims, radius, radius, 0)

                elif layer_type[k] == "silo":
                    material = deep_access(shapes, [str(k), 'material'])

                    device += "difference \n\t\t{ob:c}\n\t\t".format(ob=123)

                    # First shape
                    if deep_access(shapes, [str(k), 'shape']) == "circle":
                        center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
                        radius = deep_access(shapes, [str(k), 'shape_vars', 'radius'])
                        halfwidths = [radius, radius]           # to make things work
                        device += create_cylinder(center, end, radius, for_silo=True)
                    elif deep_access(shapes, [str(k), 'shape']) == "ellipse":
                        material = deep_access(shapes, [str(k), 'material'])
                        center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
                        halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
                        angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
                        device += create_ellipse(center, end, halfwidths, angle, for_silo=True)
                        print("WARNING: this function has not been tested in silos!!")
                    elif deep_access(shapes, [str(k), 'shape']) == "rectangle":
                        material = deep_access(shapes, [str(k), 'material'])
                        center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
                        halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
                        angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
                        device += create_rectangle(center, end, halfwidths, angle, for_silo=True)
                        print("WARNING: this function has not been tested in silos!!")
                    elif deep_access(shapes, [str(k), 'shape']) == "polygon":
                        print("WARNING: create_polygon function has not been tested!!")
                    else:
                        print("ERROR: This shape is not supported!!")

                    # Hole(s)
                    # Required for the hole pass to through the ends of the first shape
                    end2 = [(end[0] + 0.001), (end[1] - 0.001)]

                    j = k + 1
                    while j < len(shapes) and layer_type[j] == "Vacuum":
                        if deep_access(shapes, [str(j), 'shape']) == "circle":
                            center = deep_access(shapes, [str(j), 'shape_vars', 'center'])
                            radius = deep_access(shapes, [str(j), 'shape_vars', 'radius'])
                            device += create_cylinder(center, end2, radius, for_silo=True)
                        elif deep_access(shapes, [str(j), 'shape']) == "ellipse":
                            material = deep_access(shapes, [str(k), 'material'])
                            center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
                            halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
                            angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
                            device += create_ellipse(center, end2, halfwidths, angle, for_silo=True)
                            print("WARNING: this function has not been tested in silos!!")
                        elif deep_access(shapes, [str(j), 'shape']) == "rectangle":
                            material = deep_access(shapes, [str(k), 'material'])
                            center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
                            halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
                            angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])
                            device += create_rectangle(center, end2, halfwidths, angle, for_silo=True)
                            print("WARNING: this function has not been tested in silos!!")
                        elif deep_access(shapes, [str(j), 'shape']) == "polygon":
                            print("WARNING: create_polygon function has not been tested!!")
                        else:
                            print("ERROR: This shape is not supported!!")
                        j += 1

                    device = color_and_finish(device, default_color_dict, material, \
                            use_default_colors, custom_color = custom_colors[c], \
                            use_finish = use_finish, custom_finish = custom_finish)

                    if not use_default_colors:
                        c += 1

                    device_dims = update_device_dims(device_dims, halfwidths[0], halfwidths[1], 0)

                elif layer_type[k] == "ellipse":
                    material = deep_access(shapes, [str(k), 'material'])
                    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
                    halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
                    angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])

                    device += create_ellipse(center, end, halfwidths, angle)

                    device = color_and_finish(device, default_color_dict, material, \
                            use_default_colors, custom_color = custom_colors[c], \
                            use_finish = use_finish, custom_finish = custom_finish)

                    if not use_default_colors:
                        c += 1

                    device_dims = update_device_dims(device_dims, halfwidths[0], halfwidths[1], 0)

                elif layer_type[k] == "rectangle":
                    material = deep_access(shapes, [str(k), 'material'])
                    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
                    halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
                    angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])

                    device += create_rectangle(center, end, halfwidths, angle)

                    device = color_and_finish(device, default_color_dict, material, \
                            use_default_colors, custom_color = custom_colors[c], \
                            use_finish = use_finish, custom_finish = custom_finish)

                    if not use_default_colors:
                        c += 1

                    device_dims = update_device_dims(device_dims, halfwidths[0], halfwidths[1], 0)

                elif layer_type[k] == "polygon":
                    print("WARNING: create_polygon function has not been tested!!")

                elif layer_type[k] == "Vacuum":
                    # Python is too smart; it won't let me intentionally skip with k += 1
                    k = k

                else:
                    print("\nWARNING: Invalid or unsupported layer specified.\n")

            device_dims = update_device_dims(device_dims, 0, 0, thickness)

    # Substrate layer
    material = "subst"
    thickness_sub = max(1, deep_access(device_dict, ['statepoint', 'sub_layer', 'thickness']))
    background_sub = deep_access(device_dict, ['statepoint', 'sub_layer', 'background'])
    halfwidth = [(0.5 * lattice_vecs[0][0]), (0.5 * lattice_vecs[1][1])]

    end = [(-1.0 * device_dims[2]), (-1.0 * device_dims[2] - thickness_sub)]

    device += "box\n\t\t{ob:c}\n\t\t".format(ob=123) \
            + "<{0}, {1}, {2}>\n\t\t".format((-1.0 * halfwidth[0]), (-1.0 * halfwidth[1]), end[0]) \
            + "<{0}, {1}, {2}>\n\t\t".format(halfwidth[0], halfwidth[1], end[1]) 

    device = color_and_finish(device, default_color_dict, material, \
            use_default_colors = True, use_finish = "dull")

    device_dims = update_device_dims(device_dims, halfwidth[0], halfwidth[1], thickness_sub)

    device += "{cb:c}\n\n".format(cb=125)

    # Replicate unit cell
    device += "merge\n\t{ob:c} \n\t".format(ob=123)

    # Shift translation so that the original device is roughly in the center
    adj_x = int(0.5 * (num_UC_x - (1 + (num_UC_x - 1) % 2)))
    adj_y = int(0.5 * (num_UC_y - (1 + (num_UC_y - 1) % 2)))
    # Explanation: 
    # Subtracts 1 because one row stays at origin
    # Uses modulo to subtract again if odd number
    # Sends half of the remaining rows backward

    for i in range(num_UC_x):
        for j in range(num_UC_y):
            device += "object {ob:c} UnitCell translate <{0}, {1}, {2}> {cb:c}\n\t".format( \
                    ((i - adj_x) * lattice_vecs[0][0]), ((j - adj_y) * lattice_vecs[1][1]), 0, \
                    ob=123, cb=125)

    device += "{cb:c}\n\n".format(cb=125)

    # Add buffer around the edge to minimize reflection washout
    if add_edge_buffer:
        min_x = -1.0 * (adj_x + 1) * lattice_vecs[0][0]
        max_x = (num_UC_x - adj_x) * lattice_vecs[1][1]
        min_y = -1.0 * (adj_y + 1) * lattice_vecs[0][0]
        max_y = (num_UC_y - adj_y) * lattice_vecs[1][1]
        #end = unchanged from original substrate box
        #end = [(-1.0 * device_dims[2]), (-1.0 * device_dims[2] - 0.001)]

        device += "box\n\t\t{ob:c}\n\t\t".format(ob=123) \
                + "<{0}, {1}, {2}>\n\t\t".format(min_x, min_y, (end[1])) \
                + "<{0}, {1}, {2}>\n\t\t".format(max_x, max_y, (end[0])) 

        device = color_and_finish(device, default_color_dict, material, \
                use_default_colors = True, use_finish = "dull")

    ## HEADER AND CAMERA INFO

    # Cap how far out the camera will go when replicating unit cell
    device_dims = update_device_dims(device_dims, \
            (min(5, num_UC_x) * device_dims[0]), \
            (min(5, num_UC_y) * device_dims[1]), \
            device_dims[2])

    if camera_style == "":
        camera_style = "perspective"

    if camera_style == "orthographic":
        camera_options = "angle {0}".format(str(ortho_angle))
    else:
        camera_options = ""

    if camera_loc == [] or look_at == [] or light_loc == []:
        camera_loc, look_at, light_loc = \
                guess_camera(device_dims, camera_style, angle = camera_rotate, center=[0, 0])

    header = "#version 3.7;\n" 
    header += "global_settings {ob:c} assumed_gamma 1.0 {cb:c}\n\n".format(ob=123, cb=125) 
    header += "background {ob:c} ".format(ob=123) \
            + "color rgb <{0}, {1}, {2}> ".format(bg_color[0], bg_color[1], bg_color[2]) \
            + "{cb:c}\n\n".format(cb=125) \
            + "camera \n\t{ob:c}\n\t".format(ob=123) \
            + "{0} {1} \n\t".format(camera_style, camera_options) \
            + "location <{0}, {1}, {2}>\n\t".format(camera_loc[0], camera_loc[1], camera_loc[2]) \
            + "look_at <{0}, {1}, {2}>\n\t".format(look_at[0], look_at[1], look_at[2]) \
            + "up <{0}, {1}, {2}>\n\t".format(up_dir[0], up_dir[1], up_dir[2]) \
            + "right <{0}, {1}, {2}>\n\t".format(right_dir[0], right_dir[1], right_dir[2]) \
            + "sky <{0}, {1}, {2}>\n\t".format(sky[0], sky[1], sky[2]) \
            + "{cb:c}\n\n".format(cb=125)

    if shadowless:
        header += "light_source \n\t{ob:c} \n\t".format(ob=123) \
                + "<{0}, {1}, {2}> \n\t".format(light_loc[0], light_loc[1], light_loc[2]) \
                + "color rgb <1.0,1.0,1.0> \n\t" \
                + "shadowless \n\t" \
                + "{cb:c}\n\n".format(cb=125)
    else:
        header += "light_source \n\t{ob:c} \n\t".format(ob=123) \
                + "<{0}, {1}, {2}> \n\t".format(light_loc[0], light_loc[1], light_loc[2]) \
                + "color rgb <1.0,1.0,1.0> \n\t" \
                + "{cb:c}\n\n".format(cb=125)

    # WRITE POV FILE
    fID.write(header + device)
    fID.close()

    # RENDER
    command = "povray Input_File_Name={0} Output_File_Name={1} ".format(pov_name, image_name) \
            + "+H{0} +W{1}".format(height, width)

    if display:
        command += " Display=on"
    else:
        command += " Display=off"

    if transparent:
        command += " +ua" 

    if antialias:
        command += " +A"

    if open_png == True:
        command += " && eog {}".format(image_name)

    if render == True:
        system(command)

    div = '----------------------------------------------------'
    print("write_POV: Render with: \n{0}\n{1}\n{0}".format(div,command))

    return
