"""Set camera, header, finishes, and call POV-Ray.

A quick summary:
  * guess_camera is never directly called by the user, executes
    automatically if user does not specify some parameters
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
      camera_rotate (float, optional): Rotates the camera around the 
          z-axis (in degrees); 0 will look down the x-axis at the side
          of the device (Default = 0)
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

    # Need to scale z-axis settings differently with isosurfaces
    # Related to default origin position:
    # - Pure device render: top at z = 0, centered at x=y=0 by default
    # - Isosurface (and opt. unit cell) bottom at z=0, origin at corner
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


def write_header_and_camera(device_dims, coating_dims=[0, 0, 0], 
        camera_style="perspective", camera_rotate=60,
        viewing_angle = 0, camera_loc=[], look_at=[], light_loc=[], 
        up_dir=[0, 0, 1], right_dir=[0, -1, 0], sky=[0, 0, 1.33], 
        bg_color=[], shadowless=False, isosurface=False, 
        use_include_files=False, include_files=["colors.inc",
        "finish.inc", "glass.inc", "metals.inc"]):
    """Create a string containing the header and camera information.
    
    The minimum required input is:
    * the device dimensions (device_dims)
    
    Due to how the camera information is guessed (if camera and light
    information is not completely specified, you must be aware of the
    following:
    * if you have a coating, you must specify the coating dimensions
    * if you have an isosurface, you must specify isosurface = True
    
    The following camera settings generate the same dimensions,
    but the second one has more space at top and bottom:
    height=800, width=4/3*height, up_dir=[0,0,1], right_dir=[0,1,0],
            sky=up_dir
    height=800, width=height, up_dir=[0,0,1.333], right_dir=[0,1,0],
            sky=up_dir
    
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
      viewing_angle (int, optional): Width of the field of view of the 
          camera; the orthographic camera will reset this to 60 if the
          user doesn't specify anything, while any other camera 
          (including the default perspective camera) omits the angle
          keyword if it is set to 0 (degrees, default 0)
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
      use_include_files (bool, optional): Adds #include declarations.
          If set to True and the user does not specify anything in the
          include_files argument, it defaults to adding colors.inc,
          finish.inc, glass.inc, and metals.inc. If the user specifies
          anything in the include_files variable, use_include_files is
          automatically set to True and those include files will be 
          added. (default False)
      include_files (list, optional): The list of include files the
          user wishes to add to the header. Specifying anything other
          than the default will automatically set use_include_files
          to True. (Default
          ["colors.inc", "finish.inc", "glass.inc", "metals.inc"])

    Returns:
      string: Header information with camera, light, and background 
          settings

    """
    # If camera and light source locations specified but the look_at 
    # point is missing, set look_at point and leave other values alone.
    # If either camera or light locations are missing, all values are
    # filled in by the guess_camera function (called within 
    # write_header_and_camera)
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

    camera_options = ""
    if camera_style == "orthographic":
        if viewing_angle == 0:
            viewing_angle = 60
        camera_options += f"angle {viewing_angle}\n\t"
    else:
        if viewing_angle != 0:
            camera_options += f"angle {viewing_angle}\n\t"

    # Create POV header
    header = "#version 3.7;\n"
    header += f"global_settings {{ assumed_gamma 1.0 }}\n\n"

    if include_files != [
            "colors.inc", "finish.inc", "glass.inc", "metals.inc"]:
        use_include_files = True

    if use_include_files == True:
        for i in range(len(include_files)):
            header += f'#include "{include_files[i]}"\n'
        header += "\n"

    if bg_color != []:
        header += ("background {{ "
                + f"color rgb <{bg_color[0]}, {bg_color[1]}, {bg_color[2]}> "
                + "}}\n\n")

    header += (f"camera \n\t{{\n\t"
            + f"{camera_style} \n\t{camera_options}"
            + "location "
            + f"<{camera_loc[0]}, {camera_loc[1]}, {camera_loc[2]}>\n\t"
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


def write_pov_file(pov_name, pov_string):
    """Writes a .pov file using the input string.

    Must contain the header, camera information, and device description
    for the file to render successfully. This function does NOT check
    that the header and device/isosurface information is included, but
    it does use grep and sed to make sure that the #include directives
    are present if the user appears to be calling information from the
    include files. Everything is written to the file pov_name.

    Args:
      pov_name (string): Name to give the .pov file
      pov_string (string): String describing the header, camera
          information, and the device string

    Returns:

    """
    import os

    fileID = open(pov_name, "w")
    fileID.write(pov_string)
    fileID.close()

    using_include_file = False

    # Anything from the include files is "keyword { OneWord }"
    finish_inc = f"grep 'finish {{[A-Za-z ][A-Za-z ]*}}' {pov_name}"
    stream = os.popen(finish_inc)
    if stream.read() != "":
        using_include_file = True

    pigment_inc = f"grep 'pigment {{[A-Za-z ][A-Za-z ]*}}' {pov_name}"
    stream = os.popen(pigment_inc)
    if stream.read() != "":
        using_include_file = True

    if using_include_file == True:
        include = f"grep '^#include' {pov_name}"
        stream = os.popen(include)
        if stream.read() == "":
            print("WARNING: You appear to be using values from include files")
            print("         without importing the files with #include.")
            print("         Fixing this for you...")

            pov_name = "shiny_batman.pov"                                                  
            sed_string = ("sed -i '/camera/ i\#include \"colors.inc\"\\\n"                 
                       +  "#include \"finish.inc\"\\\n"                                    
                       +  "#include \"glass.inc\"\\\n"                                     
                       + f"#include \"metals.inc\"\\\n' {pov_name}")                       
            print(sed_string)                                                              
            os.system(sed_string) 
    return


def render_pov(pov_name, image_name, height=800, width=800,
        display=False, transparent=True, antialias=True,
        num_threads=0, open_image=True, render=True, 
        render_quality=9):
    """Generate the render command and feed the pov file into POV-Ray.
    
    By default it will render an image, open the image post-render with
    eog, and print the render command to the terminal.
    
    The output file format is determined from the file extension given
    in image_name. If the specified format is not supported by POV-Ray,
    or the file format was omitted, the code specifies the png format.

    The minimum required input is:
    * the name for the generated .pov file (pov_name)
    * the name for the image that will be rendered (image_name)
    
    The code will always include (in STDOUT) the command to render
    the image with the selected render options, even if it is only
    creating a .pov file (not rendering).

    POV-Ray image quality options:
    0, 1      Just show quick colors. Full ambient lighting only. 
    2, 3      Show specified diffuse and ambient light.
    4         Render shadows, but no extended lights.
    5         Render shadows, including extended lights.
    6, 7      Compute texture patterns, compute photons
    8         Compute reflected, refracted, and transmitted rays.
    9, 10, 11 Compute media and radiosity
    The default is 9. Quick colors used at 5 or below.

    Args:
      pov_name (str): Name of the .pov file
      image_name (str): Name of the rendered image
      height (int, optional): Image height (default 800)
      width (int, optional): Image width (default 800)
      display (bool, optional): Display render progress on the screen, 
          only relevant if ``render=True`` (default False)
      transparent (bool, optional): Sets background transparency 
          (default True)
      antialias (bool, optional): Turns antialiasing on (default True)
      num_threads (int, optional): Tells POV-Ray how many threads to
          use when rendering, specifying 0 will use all available 
          (default 0)
      open_image (bool, optional): Opens rendered image with eog if the
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
    import re

    # Determine the file type
    file_type_dict = {
            ".png$":"N", 
            ".bmp$":"B", 
            ".rle$":"C",
            ".exr$":"E",
            ".hdr$":"H",
            ".jp[e]*g$":"J", 
            ".ppm$":"P",
            ".t[ar]*ga$":"T"
            }
    file_type_list = list(file_type_dict)
    found = False
    i = 0
    while found == False:
        pattern = re.compile(file_type_list[i])
        if pattern.search(image_name):
            use_type = file_type_dict[file_type_list[i]]
            found = True
        else:
            i += 1
            if i == len(file_type_dict):
                print("Warning: Image file format not supported! Using .png!")
                image_name += ".png"
                use_type = "N"
                found = True

    # Create .ini file with render settings
    ini_string = ("; POV-Ray version 3.7 INI file\n"
               + f"; MANTIS auto-generated INI for {pov_name}\n\n"
               + f"+I{pov_name}\n+O{image_name}\n"
               + f"+H{height}\n+W{width}\n")

    if display:
        ini_string += "+D\n"
    else:
        ini_string += "-D\n"

    if transparent:
        ini_string += "+UA\n"

    if antialias:
        ini_string += "+A\n"

    if num_threads != 0:
        ini_string += f"+WT{num_threads}\n"

    if use_type != "N":
        ini_string += f"+F{use_type}\n"

    if render_quality != 9:
        if render_quality not in range(0,12):
            render_quality = 9
        ini_string += f"+Q{render_quality}\n"

    ini_name = pov_name.replace(".pov",".ini")
    fileID = open(ini_name, "w")
    fileID.write(ini_string)
    fileID.close()

    # Create render command
#    command = f"povray {ini_name.replace('.ini','')}"
    command = f"povray {ini_name}"
    if open_image:
        command += " && eog {0}".format(image_name)
    if render == True:
        system(command)

    div = '----------------------------------------------------'
    print("For additional rendering options, see POV-Ray's documentation,")
    print("particularly the file output and tracing options:")
    print("http://wiki.povray.org/content/Reference:File_Output_Options")
    print("http://wiki.povray.org/content/Reference:Tracing_Options")
    print(f"Render with \n{div}\n{command}\n{div}")

    return

