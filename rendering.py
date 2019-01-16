def write_pov(device_dict, pov_name, image_name, \
        height = 800, width = 800, \
        num_UC_x = 5, num_UC_y = 5, \
        camera_style = "perspective", \
        camera_rotate = 45, ortho_angle = 30, \
        camera_loc = [], look_at = [0,0,0], light_loc = [], \
        up_dir = [0, 0, 1.33], right_dir = [0, 1, 0], sky = [0, 0, 1.33], \
        shadowless = False, \
        bg_color = [1.0, 1.0, 1.0], transparent = True, antialias = True, \
        display = False, render = True, open_png = True):

    """ Generates a .pov and optionally render an image from a json file.

        Currently only perspective and orthographic styles are supported.
        Full list of povray options : perspective (default)| orthographic | fisheye |
        ultra_wide_angle | omnimax | panoramic | cylinder CylinderType | spherical
        for orthographic you might have to use e.g. "orthographic angle 30"

        The following camera settings generate the same dimensions, 
        but the second one has more whitespace at top and bottom: 
        height=800, width=4/3.0*height, up_dir=[0,0,1], right_dir=[0,1,0]
        height=800, width=height, up_dir=[0,0,1.333], right_dir=[0,1,0]

        Code makes a few assumptions:
        - All shapes describing holes in silos are the vacuum layers
        immediately following the shape layer
        - xy-plane is centered at 0
        - Perspective camera style assumed unless otherwise specified
        - Orthographic camera automatically adds angle 30.
    """

    from os import system
    from util import deep_access
    from util_pov import update_device_dims, guess_camera, color_and_finish
    from util_pov import create_cylinder, create_ellipse, create_rectangle, create_polygon

    fID = open(pov_name,'w')

    color_dict = {"subst": [0.15, 0.15, 0.15], "Si":[0.0, 0.0, 0.0], \
            "SiO2":[0.99, 0.99, 0.96], "fun":[1, 0, 1]}

    device_dims = [0, 0, 0] # maximum dimensions of the final device
                            # Components must be positive; update after adding each layer
    device = ""             # stores the device

    # Lattice vectors
    lattice_dict = deep_access(device_dict, ['statepoint', 'lattice_vecs'])
    lattice_vecs = list()
    for v in ['a', 'b']:
        tmp_vec = list()
        for i in ['x', 'y']:
            tmp_vec.append(deep_access(lattice_dict, [v, i]))
        lattice_vecs.append(tmp_vec)

    # Zero layer
    # currently no need to render anything from this layer
    #background_0L = deep_access(device_dict, ["statepoint", "zero_layer", "background"])
    #thickness_0L = deep_access(device_dict, ["statepoint", "zero_layer", "thickness"])

    # Device layers
    device += "#declare UnitCell = "
    device += "merge\n\t{ob:c}\n\t".format(ob=123)

    for i in range(deep_access(device_dict, ['statepoint', 'num_layers'])):

        if deep_access(device_dict, ['statepoint', 'dev_layers', str(i)]).get('shapes') is not None:
            shapes = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'shapes'])
            thickness = deep_access(device_dict, ['statepoint', 'dev_layers', str(i), 'thickness'])
            end = [(-1.0 * device_dims[2]), (-1.0 * device_dims[2] - thickness)]

            # Determine layer types
            layer_type = []
            has_silo = False
            for ii in range(len(shapes)):
                print(deep_access(shapes, [str(ii)]))
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
                    device = color_and_finish(device, color_dict["fun"], finish = "billiard")

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

                    device = color_and_finish(device, color_dict["fun"], finish = "billiard")

                    device_dims = update_device_dims(device_dims, halfwidths[0], halfwidths[1], 0)

                elif layer_type[k] == "ellipse":
                    material = deep_access(shapes, [str(k), 'material'])
                    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
                    halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
                    angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])

                    device += create_ellipse(center, end, halfwidths, angle)
                    device = color_and_finish(device, color_dict["SiO2"], finish = "glass")

                    device_dims = update_device_dims(device_dims, halfwidths[0], halfwidths[1], 0)

                elif layer_type[k] == "rectangle":
                    material = deep_access(shapes, [str(k), 'material'])
                    center = deep_access(shapes, [str(k), 'shape_vars', 'center'])
                    halfwidths = deep_access(shapes, [str(k), 'shape_vars', 'halfwidths'])
                    angle = deep_access(shapes, [str(k), 'shape_vars', 'angle'])

                    device += create_rectangle(center, end, halfwidths, angle)
                    device = color_and_finish(device, color_dict["fun"], finish = "irid")

                    device_dims = update_device_dims(device_dims, halfwidths[0], halfwidths[1], 0)

                elif layer_type[k] == "polygon":
                    print("WARNING: create_polygon function has not been tested!!")

                elif layer_type[k] == "Vacuum":
                    # Python is too smart; the for loop won't let me intentionally skip a value
                    k = k

                else:
                    print("\nWARNING: Invalid or unsupported layer specified.\n")

            device_dims = update_device_dims(device_dims, 0, 0, thickness)

    # Substrate layer
    thickness_sub = max(1, deep_access(device_dict, ['statepoint', 'sub_layer', 'thickness']))
    background_sub = deep_access(device_dict, ['statepoint', 'sub_layer', 'background'])
    halfwidth = [(0.5 * lattice_vecs[0][0]), (0.5 * lattice_vecs[1][1])]

    end_0 = [(-1.0 * device_dims[2]), (-1.0 * device_dims[2] - thickness_sub)]

    device += "box\n\t\t{ob:c}\n\t\t".format(ob=123) \
            + "<{0}, {1}, {2}>\n\t\t".format((-1.0 * halfwidth[0]), (-1.0 * halfwidth[1]), end_0[0]) \
            + "<{0}, {1}, {2}>\n\t\t".format(halfwidth[0], halfwidth[1], end_0[1]) 

    device = color_and_finish(device, color_dict["subst"], finish = "dull")

    device_dims = update_device_dims(device_dims, halfwidth[0], halfwidth[1], thickness_sub)

    device += "{cb:c}\n\n".format(cb=125)

    # Display a bunch of unit cells
    device += "merge\n\t{ob:c} \n\t".format(ob=123)

    # Shift translation so that the original device is roughly in the center
    adj_x = int(0.5 * (num_UC_x - (1 + (num_UC_x - 1) % 2)))
    adj_y = int(0.5 * (num_UC_y - (1 + (num_UC_y - 1) % 2)))
    # Explanation: subtracts 1 because one row stays at origin
    # uses modulo to subtract again if odd number
    # sends half of the remaining rows backward

    for i in range(num_UC_x):
        for j in range(num_UC_y):
            device += "object {ob:c} UnitCell translate <{0}, {1}, {2}> {cb:c}\n\t".format( \
                    ((i - adj_x) * lattice_vecs[0][0]), ((j - adj_y) * lattice_vecs[1][1]), 0, ob=123, cb=125)

    device += "{cb:c}\n\n".format(cb=125)

    ## HEADER AND CAMERA INFO

    # Cap how far out the camera will go when replicating unit cell
    device_dims = update_device_dims(device_dims, \
            (min(5, num_UC_x) * device_dims[0]), \
            (min(5, num_UC_y) * device_dims[1]), \
            device_dims[2])

    if camera_style == "":
        camera_style = "perspective"
        print("Assumed camera_style : ", camera_style)

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
            + "location <{0}, {1}, {2}>\n\t".format(camera_loc[0], camera_loc[1], camera_loc[2])  \
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
