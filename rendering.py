def write_pov(device_dict, pov_name, image_name, 
    height = 800, width = 800, 
    num_UC_x = 5, num_UC_y = 5, 
    camera_style = "perspective", 
    camera_rotate = 60, 
    ortho_angle = 30, 
    camera_loc = [], look_at = [], light_loc = [], 
    up_dir = [0, 0, 1], right_dir = [0, 1, 0], sky = [0, 0, 1.33], 
    shadowless = False, 
    coating_layers = [], 
    coating_color_dict = {"background":[1, 0, 0, 0, 0]}, 
    coating_ior_dict = {"background":1.0}, 
    bg_color = [1.0, 1.0, 1.0], transparent = True, antialias = True, 
    use_default_colors = True, custom_colors = [[0, 0.667, 0.667, 0, 0]], 
    use_finish = "", custom_finish = "", 
    add_lines = True, 
    line_thickness = 0.0025, line_color = [0, 0, 0, 0, 0],
    display = False, render = True, num_threads = 0, 
    open_png = False):

    """ 
    Generates a .pov and optionally render an image from a json file.
    device_dict, pov_name, and image_name are the only required 
    values.
    * device_dict is the dictionary entry from the json file
    * pov_name is the name for the generated .pov file
    * image_name is the name for the image that will be rendered

    By default, the code will generate a .pov file, render an image
    and open it post-render with eog.

    The code will always include (in STDOUT) the command to render
    the image with the selected render options, even if it is only
    creating a .pov file (not rendering).

    The color and finish of the device can be specified by the user 
    via the ``color_and_finish`` function. The substrate will always 
    be a dull, dark grey; this cannot be modified by the user.

    The following camera settings generate the same dimensions, 
    but the second one has more whitespace at top and bottom: 
    height=800, width=4/3.0*height, up_dir=[0,0,1], right_dir=[0,1,0], sky=up_dir
    height=800, width=height, up_dir=[0,0,1.333], right_dir=[0,1,0], sky=up_dir

    Some additional assumptions:
    * All shapes describing holes in silos are the vacuum layers 
      immediately following the shape layer
    * xy-plane is centered at 0

    :param device_dict: Dictionary entry from a json file
    :type device_dict: dict

    :param pov_name: Name of the .pov file
    :type pov_name: str

    :param image_name: Name of the rendered image
    :type image_name: str

    :param height: Image height (default 800)
    :type height: int

    :param width, Image width (default 800)
    :type width: int

    :param num_UC_x: Number of unit cells in the y direction (default 5)
    :type num_UC_x: int 

    :param num_UC_y: Number of unit cells in the y direction (default 5)
    :type num_UC_y: int 

    :param camera_style: Camera style; currently supported options are 
                         "perspective" (default), and "orthographic"; 
                         other POV-Ray camera styles may be tried if 
                         desired, but there is no promise that they will 
                         work as expected
    :type camera_style: str

    :param camera_rotate: Rotates the camera location about the z-axis 
                          (degrees, default 60) 
    :type camera_rotate: int 

    :param ortho_angle: Width of the field of view for the orthographic 
                        camera (degrees, default 30) 
    :type ortho_angle: int

    :param camera_loc: Location of the camera, can be guessed with 
                       ``guess_camera`` (default empty) 
    :type camera_loc: list 

    :param look_at: The point the camera looks at (default [0,0,0]) 
    :type look_at: list

    :param light_loc: The location of the light source, can be guessed with 
                      ``guess_camera`` (default empty)
    :type light_loc: list

    :param shadowless: Use a shadowless light source (default False)
    :type shadowless: bool

    :param up_dir: Tells POV-Ray the relative height of the screen; 
                   controls the aspect ratio together with ``right-dir`` 
                   (default [0, 0, 1.33]) 
    :type up_dir: list

    :param right_dir: Tells POV-Ray the relative width of the screen; 
                       controls the aspect ratio together with ``up_dir`` 
                       (default [0, 1, 0]) 
    :type right_dir: list

    :param sky: Sets the camera orientation, e.g. can hold the camera 
                upside down (default [0, 0, 1.33])
    :type sky: list

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

    :param transparent: Sets background transparency (default True)
    :type transparent: bool

    :param antialias: Turns antialiasing on (default True)
    :type antialias: bool

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

    :param display: Display render progress if ``render=True`` (default False)
    :type display: bool

    :param render: Tells POV-Ray to render the image (default True)
    :type render: bool

    :param num_threads: Tells POV-Ray how many threads to use when rendering,
                        specifying 0 will use all available (default 0)
    :type render: int

    :param open_png: Opens rendered image with eog if the rendering is
                     successful (default False)
    :type open_png: bool
    """

    from os import system
    from copy import deepcopy
    from util import deep_access
    from util_shapes import create_cylinder, create_ellipse, create_rectangle, create_polygon
    from util_shapes import add_slab, create_torus, add_accent_lines, update_device_dims
    from util_shapes import write_circle_feature, write_ellipse_feature
    from util_shapes import write_rectangle_feature, write_polygon_feature
    from util_shapes import check_for_false_silos, write_silo_feature
    from util_shapes import create_device_layer 
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

    #### ---- HEADER AND CAMERA ---- ####
    
    # Cap how far out the camera will go when replicating unit cell
    device_dims = update_device_dims(device_dims, 
            (min(5, num_UC_x) * device_dims[0]), 
            (min(5, num_UC_y) * device_dims[1]), 
            device_dims[2])






    return device, device_dims, coating_dims
