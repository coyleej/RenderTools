"""Set camera, header, finishes, and call POV-Ray.

A quick summary:
  * guess_camera is never directly called by the user, executes
    automatically if user does not specify some parameters
  * color_and_finish never directly called by the user, but acts
    based on values specified by the user
  * write_header_and_camera is required to generate a functional
    .pov file and must be explicitely called by the user
  * render_pov generates the rendering command and defaults to
    calling povray and rendering the image
"""

def guess_camera(device_dims, coating_dims=[0,0,0], 
        camera_style="perspective", camera_rotate =0, center=[0, 0], 
        isosurface=False):
    """Guess the camera and light locations if this info is missing.
    
    Can look at the device from the side (angle = 0) or at an angle in
    the xy-plane (rotate around z-axis, *DEGREES* from x-axis).  It
    has been optimized to give decent results, though fine-tuning
    afterwards in the .pov file is encouraged.

    Args:
      device_dims (list): Dimensions of the unit cell
      coating_dims (list, optional): Dimensions of the coating layer(s) 
          (Default value = [0,0,0])
      camera_style (string, optional): The desired camera style, 
          currently accepts perspective and orthographic (Default 
          "perspective")
      camera_rotate (float, optional): Rotates the camera around the z-axis 
          (in degrees); 0 will look down the x-axis at the side of the 
          device (Default = 0)
          #### NOTE: Renamed from "angle" to match write_pov!!! ####
      center (list, optional): The center of the device, gets over-
          written if isosurface=True (Default value = [0,0])
      isosurface(boolean, optional): Adjusts camera paramters if you 
          rendering an isosurface.  Required because the origin is in 
          a different location with isosurfaces. Overwrites any values
          assigned to the center variable. (Default = False)

    Returns:
      tuple: Tuple containing the camera position, camera look at
          location, and the light position

    """
    from math import sin, cos, pi

    camera_position = [0, 0, 0]
    light_position = [0, 0, 0]

    deg_to_rads = pi / 180.0
    camera_rotate *= deg_to_rads 

    if camera_style == "perspective":
        x_offset = 1.2
        z_scale = 1.0
    elif camera_style == "orthographic":
        x_offset = 1.2
        z_scale = 1.0
    else:
        x_offset = 1.2
        z_scale = 1.0
        print("WARNING: Camera parameters are not optimized for this style!")

    # Offset for x,y-dimensions
    camera_offset = x_offset * (max(device_dims) + 0.8 * max(coating_dims))
    light_offset = camera_offset * 1.25 

    # Need to scale z-axis settings differently when rendering isosurfaces
    # Related to default origin position:
    # - Pure device render: top at z = 0, centered at x=y=0 by default
    # - Isosurface (and optional unit cell) has bottom at z=0, origin at corner
    if isosurface == False:
        z_lookat = -0.66
    else:
        z_lookat = 0.25
        device_dims[2] *= 1.75
        center = [0.5 * device_dims[0], 0.5 * device_dims[1]]
        camera_offset *= 0.75

    # Guess things
    camera_position[0] = ((camera_offset+device_dims[0]+center[0])
                          * cos(camera_rotate))
    camera_position[1] = ((camera_offset+device_dims[0]+center[1])
                          * sin(camera_rotate))
    camera_position[2] = z_scale * (device_dims[2] + 0.5*coating_dims[2])

    camera_look_at = [center[0], center[1], 
                     (z_lookat*device_dims[2]+0.50*coating_dims[2])]

    light_position[0] = ((device_dims[0]+light_offset)
                         * cos(camera_rotate-12*deg_to_rads))
    light_position[1] = ((device_dims[1]+light_offset)
                         * sin(camera_rotate-12*deg_to_rads))
    light_position[2] = camera_position[2] + light_offset/3.0

    if isosurface == True:
        light_position[0] = max(light_position[0], light_position[1])
        light_position[1] = light_position[0]

    #print("Write_POV estimated camera parameters:")
    #print("camera_position : " , camera_position)
    #print("camera_look_at : ", camera_look_at)

    return camera_position, camera_look_at, light_position


def color_and_finish(dev_string, default_color_dict, material, 
        use_default_colors, custom_color=[0, 0.6667, 0.667, 0, 0], 
        ior=1, use_finish="dull", custom_finish=""):
    """Set object color and finish and return the updated string.
    
    Users may specify their own custom color scheme or use the default,
    which is based on the material type specified in the device file.
    
    Color and finish is appended to the device string.
    
    Do not remove the underscore from filter_, as this differentiates
    it from filter, a function in python.
    
    Available finishes: see ``use_finish``  parameter for details.
    Specifying "material" will use the material finish (currently "Si",
    "SiO2", or "subst") finish in order to accomodate multiple material
    types in a device. The substrate will always have the "dull" finish.
    
    If using the "custom" finish, the finish details must be specified
    in the custom_finish variable or it will default to "dull".
    
    The filter and transmit terms are both 0 by default, with the
    exception of types requiring transparency, e.g. glass. If you
    request one of those finishes, the code will overwrite your
    transmit and filter values. If you do now want this to happen,
    you should declare your own custom finish.

    Args:
      dev_string (str): String describing the device
      default_color_dict (dict): Dictionary containing default finishes
          for the various material types
      use_default_colors (bool): Boolean selects which color set to use.
          True assigns colors based on the material type ("Si", "SiO2",
          and "subst"). False uses the user-assigned custom colors.
      custom_color (list, optional): RGBFT values describe a single 
          color. If you set ``use_default_colors=False`` but forget to
          specify a custom color, it uses #00aaaa (the Windows 95
          default desktop color).

          RGB values must be in the range [0,1]. F and T are filter and
          transmit, respectively. They are optional and both default 
          to 0 for most finishes.
      ior (float, optional): Index of refraction for transparent 
          finish only (Default value = 1)
      use_finish (str, optional): Select the finish that you want. 
          Current options: "material", "Si", "SiO2", "glass", 
          "bright_metal", "dull_metal", "irid", "billiard", "dull", 
          "custom" (Default value = "dull")
      custom_finish (str, optional): User-defined custom finish. Set 
          use_finish=custom to call this option. (Default value = "")
      material: 

    Returns:
      string: Updated device string containing color and finish settings

    """
    # These two values only matter for SiO2, translucent, glass, and irid
    transmit, filter_ = 0, 0

    # Set finish
    if use_finish == "material":
        use_finish = material

    if use_finish == "Si" or use_finish == "silicon":
        extra_finish = (f"finish \n\t\t\t{{ \n\t\t\t"
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

    elif use_finish == "SiO2":
        filter_ = 0.98
        extra_finish = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "specular 0.6 \n\t\t\t"
                + "brilliance 5 \n\t\t\t"
                + "roughness 0.001 \n\t\t\t"
                + f"reflection {{ 0.0, 1.0 fresnel on }}\n\t\t\t"
                + f"}}\n\t\t"
                + f"interior {{ ior 1.45 }}\n\t\t")

    elif use_finish == "translucent":
        transmit = 0.02
        filter_ = 0.50
        extra_finish = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "emission 0.25 \n\t\t\t"
                + "diffuse 0.75 \n\t\t\t"
                + "specular 0.4 \n\t\t\t"
                + "brilliance 4 \n\t\t\t"
                + f"reflection {{ 0.5 fresnel on }}\n\t\t\t"
                + f"}}\n\t\t"
                + f"interior {{ ior {ior} }}\n\t\t")

    elif use_finish == "glass":
        filter_ = 0.95
        extra_finish = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "specular 0.6 \n\t\t\t"
                + "phong 0.8 \n\t\t\t"
                + "brilliance 5 \n\t\t\t"
                + f"reflection {{ 0.2, 1.0 fresnel on }}\n\t\t\t"
                + f"}}\n\t\t"
                + f"interior {{ ior 1.5 }}\n\t\t")

    elif use_finish == "dull_metal":
        extra_finish = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "emission 0.1 \n\t\t\t"
                + "diffuse 0.1 \n\t\t\t"
                + "specular 1.0 \n\t\t\t"
                + "roughness 0.001 \n\t\t\t"
                + "reflection 0.5 metallic \n\t\t\t"
                + " metallic \n\t\t\t"
                + f"}}\n\t\t")

    elif use_finish == "bright_metal":
        extra_finish = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "emission 0.2 \n\t\t\t"
                + "diffuse 0.3 \n\t\t\t"
                + "specular 0.8 \n\t\t\t"
                + "roughness 0.01 \n\t\t\t"
                + "reflection 0.5 metallic \n\t\t\t"
                + " metallic \n\t\t\t"
                + f"}}\n\t\t")

    elif use_finish == "irid":
        filter_ = 0.7
        extra_finish = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "phong 0.5 \n\t\t\t"
                + f"reflection {{ 0.2 metallic }}\n\t\t\t"
                + "diffuse 0.3 \n\t\t\t"
                + f"irid {{ 0.75 thickness 0.5 "
                + f"turbulence 0.5 }}\n\t\t\t"
                + f"}}\n\t\t"
                + f"interior {{ ior 1.5 }}\n\t\t")

    elif use_finish == "billiard":
        extra_finish = (f"finish \n\t\t\t{{ \n\t\t\t"
                + "ambient 0.3 \n\t\t\t"
                + "diffuse 0.8 \n\t\t\t"
                + "specular 0.2 \n\t\t\t"
                + "roughness 0.005 \n\t\t\t"
                + "metallic 0.5 \n\t\t\t"
                + f"}}\n\t\t")

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

    dev_string += (f"pigment {{ color rgbft "
            + f"<{color[0]}, {color[1]}, {color[2]}, {color[3]}, {color[4]}>"
            + f" }}\n\t\t")

    # Add the extra bits describing the finish
    #if use_finish != "dull":
    if extra_finish:
        dev_string += extra_finish 

    dev_string += f"}}\n\n\t"

    return dev_string


def write_header_and_camera(device_dims, coating_dims=[0, 0, 0], 
        camera_style="perspective", camera_rotate=60, camera_options="", 
        ortho_angle = 60, camera_loc=[], look_at=[], light_loc=[], 
        up_dir=[0, 0, 1], right_dir=[0, 1, 0], sky=[0, 0, 1.33], 
        bg_color=[], shadowless=False, isosurface=False):
    """Create a string containing the header and camera information.
    
    The minimum required input is:
    * the device dimensions (device_dims)
    
    Due to how the camera information is guessed (if camera and light
    information is not completely specified, you must be aware of the
    following:
    * if you have a coating, you must specify the coating dimensions
    * if you have an isosurface, you must specify isosurface = True
    
    The following camera settings generate the same dimensions,
    but the second one has more whitespace at top and bottom:
    height=800, width=4/3*height, up_dir=[0,0,1], right_dir=[0,1,0], sky=up_dir
    height=800, width=height, up_dir=[0,0,1.333], right_dir=[0,1,0], sky=up_dir
    
    Assumes that the device xy-plane is centered at 0.

    Args:
      device_dims (list): Device dimensions
      coating_dims (list, optional): Coating dimensions, by it default
          it assume there is no coating (Default value = [0, 0, 0])
      camera_style (str, optional): Camera style; currently supported
          options are "perspective" (default), and "orthographic"; 
          other POV-Ray camera styles may be tried if desired, but 
          there is no promise that they will work as expected
      camera_rotate (float, optional): Rotates the camera location 
          about the z-axis (degrees, default 60)
      ortho_angle (int, optional): Width of the field of view for the 
          orthographic camera (degrees, default 30)
      camera_loc (list, optional): Location of the camera, can be 
          guessed with ``guess_camera`` (default empty)
      look_at (list, optional): The point that the camera looks at 
          (default [0,0,0])
      light_loc (list, optional): The location of the light source, 
          can be guessed with ``guess_camera`` (default empty)
      up_dir (list, optional): Tells POV-Ray the relative height of the
          screen; controls the aspect ratio together with ``right-dir``
          (default [0, 0, 1.33])
      right_dir (list, optional): Tells POV-Ray the relative width of
          the screen; controls the aspect ratio with ``up_dir`` 
          (default [0, 1, 0])
      sky (list, optional): Sets the camera orientation, e.g. can hold
          the camera upside down (default [0, 0, 1.33])
      bg_color (list, optional): Background color as [r, g, b], where
          all elements are values between 0 and 1; defaults to [] (no
          background) to enable transparency.
      shadowless (bool, optional): Use a shadowless light source 
          (default False)
      isosurface (bool, optional): Set this to True when rendering iso-
          surfaces to account for the differing origins between S4 RCWA
          simulations and isosurface creation (default False)
      camera_options (string, optional): Included in the function call
          but yet fully integrated into the rest of the script. It 
          could include the ortho angle for orthographic renderings 
          renderings, or options for other camera styles if necessary
          (Default value = "")

    Returns:
      string: Header information with camera, light, and background settings

    """
    # If camera and light source locations specified but the look_at point is
    # missing, set look_at point and leave other values alone
    # If either camera or light locations are missing, all values are filled
    # in by the guess_camera function (called within write_header_and_camera)
    if look_at == []:
        if camera_loc != [] and light_loc != []:
            # Assumes the device is centered at x=y=0
            look_at = [0, 0, (-0.66 * device_dims[2] + 0.50 * coating_dims[2])]

    # If any of the three are still missing, take a guess at everything
    if camera_loc == [] or look_at == [] or light_loc == []:
        camera_loc, look_at, light_loc = \
                guess_camera(device_dims, coating_dims=coating_dims, 
                camera_style=camera_style, camera_rotate=camera_rotate, 
                center=[0, 0], isosurface=isosurface)

    # Handles camera style and related option(s)
    if camera_style == "":
        camera_style = "perspective"

    if camera_style == "orthographic":
        camera_options = f"angle {ortho_angle}"
    else:
        camera_options = ""

    # Create POV header
    header = "#version 3.7;\n"
    header += f"global_settings {{ assumed_gamma 1.0 }}\n\n"
    
    if bg_color != []:
        header += ("background {{ "
                + f"color rgb <{bg_color[0]}, {bg_color[1]}, {bg_color[2]}> "
                + "}}\n\n")

    header += (f"camera \n\t{{\n\t"
            + f"{camera_style} {camera_options} \n\t"
            + f"location <{camera_loc[0]}, {camera_loc[1]}, {camera_loc[2]}>\n\t"
            + f"look_at <{look_at[0]}, {look_at[1]}, {look_at[2]}>\n\t"
            + f"up <{up_dir[0]}, {up_dir[1]}, {up_dir[2]}>\n\t"
            + f"right <{right_dir[0]}, {right_dir[1]}, {right_dir[2]}>\n\t"
            + f"sky <{sky[0]}, {sky[1]}, {sky[2]}>\n\t}}\n\n")

    header += ("light_source \n\t"
            + f"{{\n\t<{light_loc[0]}, {light_loc[1]}, {light_loc[2]}> \n\t"
            + "color rgb <1.0,1.0,1.0> \n\t")

    if shadowless:
        header += "shadowless \n\t"

    header += f"}}\n\n"

    return header


def render_pov(pov_name, image_name, height, width,
        display=False, transparent=True, antialias=True,
        num_threads=0, open_png=True, render=True, 
        render_quality=9):
    """Generate the render command and feed the pov file into POV-Ray.
    
    By default it will render an image open the image post-render with
    eog, and print the render command to the terminal.
    
    The minimum required input is:
    * the name for the generated .pov file (pov_name)
    * the name for the image that will be rendered (image_name)
    * image height
    * image width
    
    The code will always include (in STDOUT) the command to render
    the image with the selected render options, even if it is only
    creating a .pov file (not rendering).

    Args:
      pov_name (str): Name of the .pov file
      image_name (str): Name of the rendered image
      height (int): Image height (default 800)
      width (int): Image width (default 800)
      display (bool, optional): Display render progress on the screen, 
          only relevant if ``render=True`` (default False)
      transparent (bool, optional): Sets background transparency 
          (default True)
      antialias (bool, optional): Turns antialiasing on (default True)
      num_threads (int, optional): Tells POV-Ray how many threads to
          use when rendering, specifying 0 will use all available 
          (default 0)
      open_png (bool, optional): Opens rendered image with eog if the
          rendering is successful (default False)
      render (bool, optional): Tells POV-Ray to render the image 
          (default True)
      render_quality (int, optional): Allows user to turn off shading,
          textures, fancy lighting, etc. to speed up rendering,
          especially for testing settings; must be an integer in the
          range from 0 and 11 (default 9, POV-Ray's default)

    Returns:

    """
    from os import system

    command = (f"povray Input_File_Name={pov_name} "
            + f"Output_File_Name={image_name} "
            + f"+H{height} +W{width}")

    if display:
        command += " Display=on"
    else:
        command += " Display=off"

    if transparent:
        command += " +ua"

    if antialias:
        command += " +A"

    if num_threads != 0:
        command += f" +WT{num_threads}"

    if render_quality != 9:
        if render_quality not in range(0,12):
            render_quality = 9
        command += f" +Q{render_quality}"

        # POV-Ray image quality options:
        # 0, 1      Just show quick colors. Use full ambient lighting only. 
        # 2, 3      Show specified diffuse and ambient light.
        # 4         Render shadows, but no extended lights.
        # 5         Render shadows, including extended lights.
        # 6, 7      Compute texture patterns, compute photons
        # 8         Compute reflected, refracted, and transmitted rays.
        # 9, 10, 11 Compute media and radiosity
        # The default is 9 if not specified. Quick colors used at 5 or below.

    if open_png == True:
        command += " && eog {0}".format(image_name)

    if render == True:
        system(command)

    div = '----------------------------------------------------'

    print("For additional rendering options, see POV-Ray's documentation,")
    print("particularly the file output and tracing options:")
    print("http://wiki.povray.org/content/Reference:File_Output_Options")
    print("http://wiki.povray.org/content/Reference:Tracing_Options")

    print(f"write_POV: Render with: \n{div}\n{command}\n{div}")

    return

