def write_mesh2_params(parameter, values, values_per_line=2):
    """
    Takes parameter data and converts it into a string that POV-Ray 
    understands.

    :param parameter: One of the mesh2 specifications, e.g.
                      "vertex_vectors", "normal_vectors", "face_indices"
    :type parameter: string

    :param values: The values for the parameter variable, each element
                   must be a list with three values
    :type values: list

    :param values_per_line: Only place this many values on a line for 
                            readability, defaults to 2
    :type values_per_line: int

    :return: Parameter data in POV-Ray mesh2 format
    :rtype: string
    """
    param_string = "\n\t{0} {ob:c}".format(parameter, ob=123)
    param_string += "\n\t\t{0}".format(len(values))

    for j in range(len(values)):
        if j % 2 == 0:
            param_string += "\n\t\t"
        param_string += "<{0:.5f}, {1:.5f}, {2:.5f}>".format(
            values[j][0], values[j][1], values[j][2])
        if j != (len(values) - 1):
            param_string += ", "
    param_string += "\n\t\t{cb:c}".format(cb=125)

    return(param_string)


def create_mesh2(field, cutoffs, colormap = "viridis", transmit = 0.4, cmap_limits = ["a","b"]):
    """
    Converts any input field to one or more isosurfaces using the 
    marching cubes algorithm. Puts output into the povray mesh2
    format and tracks the maximum dimensions of the isosurfaces.
    Outputs the mesh2 string and the overall dimensions.

    :param field: Field values to turn into isosurface
    :type field: numpy array

    :param cutoffs: Isosurface values you want rendered
    :type cutoffs: list

    :param colormap: Colormap name, defaults to "viridis"
    :type colormap: string

    :param transmit: Isosurface transparency, defaults to 0.4
    :type transmit: float

    :param cmap_limits: colormap min and max values, defaults to 
                        field extrema if element is a character 
                        (set as ["a", "b"] by default)
    :type cmap_limits: list

    :return: mesh2 as a string 
    :rtype: string

    """
    import numpy as np
    from numpy.fft import fftn
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
        mesh += "\nunion {ob:c}".format(ob=123)

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

        print("\nIsosurface value: {0}".format(cutoffs[i]))
        print("{0} corners".format(len(corners)))
        print("{0} faces".format(len(faces)))



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

        mesh += "\n\tpigment {ob:c} rgbt <".format(ob=123) \
                + "{0:.4f}, {1:.4f}, {2:.4f}, ".format(color[0], color[1], color[2]) \
                + "{0}> {cb:c}".format(transmit, cb=125)

        mesh += "\n\t{cb:c}".format(cb=125)

    # End union
    if len(cutoffs) > 1:
        mesh += "\n{cb:c}".format(cb=125)

    return mesh


def slice_isosurface(mesh, corner1, corner2, subtract_box = False):
    """
    Slices the isosurface with a user-specified rectangular box. The
    boolean subtract_box switches between POV-Ray's intersect and
    difference functions, allowing you to preserve or extract a chunk.

    :param mesh: The mesh2 isosurface string
    :type parameter: string

    :param corner1: A corner of the box for intersect/difference
    :type parameter: list

    :param corner2: The corner of the box opposite corner1
    :type parameter: list

    :param subtract_box: Switches between POV-Ray's intersect (if False) 
                         and difference (if True) functions; intersect 
                         preserves anything within the box limits, difference
                         removes anythin within the box limits
    :type parameter: boolean

    :return: The modified mesh string
    :rtype: string
    """
    # Create the rectangle
    rect_string = "\nbox {ob:c}".format(ob=123) \
            + "\n\t<{0}, {1}, {2}>, ".format(corner1[0], corner1[1], corner1[2]) \
            + "<{0}, {1}, {2}>".format(corner2[0], corner2[1], corner2[2])

    # intersection + inverse is the same as difference
    if subtract_box == True:
        rect_string += " inverse"

    rect_string += "\n\t{cb:c}".format(cb=125)

    # Create the intersection
    mesh = "intersection {ob:c}".format(ob=123) + mesh
    mesh += rect_string + "\n{cb:c}".format(cb=125)

    return mesh
