"""Create isosurfaces.

These functions are specific to isosurface creation/rendering.
The functions to manipulate data into the proper form are 
located in the util_field file.

The function for generating the isosurface unit cell is 
isosurface_unit_cell, located in util_shapes.

A quick summary of these functions:
  * create_mesh2 calls write_mesh2_params
  * write_mesh2_params never directly called by the user
  * slice_isosurface is used to cut chunks out of the isosurface
    and/or the device unit cell
"""

def create_mesh2(field, cutoffs, colormap="viridis", transmit=0.4, 
        cmap_limits=["a","b"]):
    """Converts any input field to one or more isosurfaces using the
    marching cubes algorithm. Puts output into the povray mesh2
    format and tracks the maximum dimensions of the isosurfaces.
    Outputs the mesh2 string and the overall dimensions.
    
    Minimum required input is
    * the field of interest (field)
    * the isovalues of interest (cutoffs)
    
    #### NOTE ####
    Currently working on allowing user more control over the isosurface
    color cutoffs. Currently the colormap extremes are always set to
    the minimum and maximum values of the field.
    #### NOTE ####

    Args:
      field (numpy array): Field values to turn into isosurface
      cutoffs (list): Isosurface values you want rendered
      colormap (string, optional): Colormap name, defaults to "viridis"
      transmit (float, optional): Isosurface transparency (default 0.4)
      cmap_limits (list, optional): colormap min and max values, 
          defaults to field extrema if element is a character (set as 
          ["a", "b"] by default)

    Returns:
      string: mesh2 object as a string

    """
    import numpy as np
    from skimage.measure import marching_cubes_lewiner
    from os import system
    import pylab
    from math import floor, ceil

    # Check that all cutoffs are contained within the dataset
    # Also can't use the field extrema here, must tweek slightly
    # Otherwise skimage.measure.marching_cubes_lewiner() throws an error
    field_min = np.amin(field)
    field_max = np.amax(field)

    for i in range(len(cutoffs)):
        if cutoffs[i] <= field_min:
            cutoffs[i] = 1.0001 * field_min
        elif cutoffs[i] >= field_max:
            cutoffs[i] = 0.9999 * field_max

    # Sort and remove duplicates
    cutoffs = sorted(set(cutoffs))

    # Hijack colormap for a color scheme
    # Extremes default to max and min cutoffs if the user doesn't specify
    # Also make sure that the desired colormap range includes all cutoffs
    cm = pylab.get_cmap(colormap)

    if isinstance(cmap_limits[0], str):
        cmap_limits[0] = min(cutoffs)
    if isinstance(cmap_limits[1], str):
        cmap_limits[1] = max(cutoffs)




    print(cmap_limits)




    # Create string to store mesh information
    mesh = ""

    # Need to use union if more than one isosurface, esp. if using 
    # povray's intersection or difference functions as an option
    if len(cutoffs) > 1:
        mesh += f"\nunion {{"

    # Loop over cutoffs
    for i in range(len(cutoffs)):

        # Grab color from colormap
        color = cm(i / len(cutoffs))

        #SCIKIT marching cubes function
        # corners :: Coordinates of each vertex, just a list of values
        # faces :: List of the vertices for each face by index value in corners variable
        # normals :: Normal vector for each vertex, indices match corners variable
        # values :: Value at each vertex; we don't care about these
        corners, faces, normals, values = marching_cubes_lewiner(field, cutoffs[i])

        print(f"\nIsosurface value: {cutoffs}")
        print(f"{corners} corners")
        print(f"{faces} faces")



        print(color)


        # Create mesh
        mesh += "\n\nmesh2 {ob:c}".format(ob=123)

        # Add VERTEX vectors
        mesh += "\n\t// Vertex vectors"
        vertex_params = write_mesh2_params("vertex_vectors", corners)
        mesh += vertex_params

        # Add NORMAL vectors
        mesh += "\n\t// Normal vectors"
        normal_params = write_mesh2_params("normal_vectors", normals)
        mesh += normal_params

        # Add FACE indices
        mesh += "\n\t// Face indices"
        face_params = write_mesh2_params("face_indices", faces, values_per_line=3)
        mesh += face_params

        # NORMAL indices
        # // Not required because the vertices and normals have the same indices
        # // POV-Ray will use the values from faces_indices

        mesh += (f"\n\tpigment {{ rgbt <"
                + f"{color[0]:.4f}, {color[1]:.4f}, {color[2]:.4f}, "
                + f"{transmit}> }}")

        mesh += f"\n\t}}"

    # End union
    if len(cutoffs) > 1:
        mesh += f"\n}}"

    return mesh


def write_mesh2_params(parameter, values, values_per_line=2):
    """Takes parameter data and converts it into a string that POV-Ray
    understands.

    Args:
      parameter (string): One of the mesh2 specifications, e.g. 
          "vertex_vectors", "normal_vectors", "face_indices"
      values (list): The values for the parameter variable, each 
          element must be a list with three values
      values_per_line (int, optional): Only place this many values on
          a line for readability, defaults to 2

    Returns:
      string: Parameter data in POV-Ray mesh2 format

    """
    param_string = f"\n\t{parameter} {{"
    param_string += f"\n\t\t{len(values)}"
#    param_string += "\n\t\t{0}".format(len(values))

    for j in range(len(values)):
        if j % 2 == 0:
            param_string += "\n\t\t"
        param_string += f"<{values[j][0]:.5f}, {values[j][1]:.5f}, {values[j][2]:.5f}>"
        if j != (len(values) - 1):
            param_string += ", "
    param_string += f"\n\t\t}}"

    return(param_string)


def slice_isosurface(mesh, corner1, corner2, subtract_box=False):
    """Slice the isosurface with a user-specified rectangular box. 
    
    The boolean subtract_box switches between POV-Ray's intersect and
    difference functions, allowing you to preserve or extract a chunk.

    Args:
      mesh: The mesh2 isosurface string
      corner1: A corner of the box for intersect/difference
      corner2: The corner of the box opposite corner1
      subtract_box: Switch between POV-Ray's intersect (if False) and
          difference (if True) functions; intersect preserves anything
          within the box limits, difference removes anythin within the
          box limits (Default value = False)

    Returns:
      string: The modified mesh string

    """
    # Create the rectangle
    rect_string = (f"\nbox {{\n\t"
            + f"<{corner1[0]}, {corner1[1]}, {corner1[2]}>"
            + f"<{corner2[0]}, {corner2[1]}, {corner2[2]}>")

    # intersection + inverse is the same as difference
    if subtract_box == True:
        rect_string += " inverse"

    rect_string += f"\n\t}}"

    # Create the intersection
    mesh = f"intersection {{" + mesh +  rect_string + f"\n}}"

    return mesh
