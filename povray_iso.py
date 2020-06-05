"""Extract/manipulate field data and create isosurfaces.

Functions to extract field data from a numpy array and manipulating
them into a form that scikit-image's meshing tools can handle.

A quick summary of these functions:
  * process_field_array reformats the data into something that
      the renderers (povray, mayavi) can process
  * double_roll adjusts the axes so that things aren't flipped
      when you go to plot them
  * extract_* extract varying information from the numpy array
  * calc_* calculate various things based on the data

These functions are specific to isosurface creation/rendering.

The function for generating the isosurface unit cell is 
isosurface_unit_cell, located in povray_shapes.

A quick summary of these functions:
  * create_mesh2 calls write_mesh2_params
  * write_mesh2_params never directly called by the user
  * slice_isosurface is used to cut chunks out of the isosurface
    and/or the device unit cell
"""
import numpy as np

def create_mesh2(field, cutoffs, colormap="viridis", transmit=0.4, 
        cmap_limits=["a","b"]):
    """Convert any input field to one or more isosurfaces.
    
    Uses the scikit-image marching cubes algorithm to generate the
    isosurface description. Formats output into POV-Ray's mesh2 format
    and tracks the maximum dimensions of the isosurfaces.  Outputs the
    mesh2 string and the overall dimensions.
    
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


#    print(cmap_limits)



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
        # faces :: List of the vertices for each face by index value 
        #          in corners variable
        # normals :: Normal vector for each vertex, indices match 
        #            corners variable
        # values :: Value at each vertex; we don't care about these
        corners, faces, normals, values = marching_cubes_lewiner(
                field, cutoffs[i])

        print(f"Isosurface value: {cutoffs[i]}")
        #print(f"{corners} corners")
        #print(f"{faces} faces")
        print(f"Color: {color}\n")

        # Create mesh
        mesh += f"\n\nmesh2 {{"

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
        face_params = write_mesh2_params("face_indices", faces, 
                values_per_line=3)
        mesh += face_params

        # NORMAL indices
        # Not required because vertices & normals have the same indices
        # POV-Ray will use the values from faces_indices

        mesh += (f"\n\tpigment {{ rgbt <"
                + f"{color[0]:.4f}, {color[1]:.4f}, {color[2]:.4f}, "
                + f"{transmit}> }}")

        mesh += f"\n\t}}"

    # End union
    if len(cutoffs) > 1:
        mesh += f"\n}}\n\n"

    return mesh


def write_mesh2_params(parameter, values, values_per_line=2):
    """Convert isosurface parameters to the POV-Ray mesh2 format.

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

    for j in range(len(values)):
        if j % 2 == 0:
            param_string += "\n\t\t"
        param_string += f"<{values[j][0]:.5f}, {values[j][1]:.5f}, "
        param_string += f"{values[j][2]:.5f}>"
        if j != (len(values) - 1):
            param_string += ", "
    param_string += f"\n\t\t}}"

    return param_string


def slice_isosurface(mesh, n, cut_at=[[0.5, 1], [0.5, 1], [0, 1]],
        subtract_box=False):
    """Slice the isosurface with a user-specified prism. 
    
    By default, it will remove the quadrant nearest the camera if used
    with the default camera guesser. The section to remove in specified
    as fractions of the unit cell.

    The boolean subtract_box switches between POV-Ray's intersect and
    difference functions, allowing you to preserve or extract a chunk.

    Args:
      mesh (str): The mesh2 isosurface string
      n (list): Dimensions of the numpy field array as [nx, ny, nz],
          used as the isosurface dimensions
      cut_at (list): Specify the section to remove, as a fraction of
          the unit cell. (Default value = [[0.5, 1], [0.5, 1], [0, 1]])
      subtract_box (bool, optional): Switch between POV-Ray's intersect
          (if False) and difference (if True) functions; intersect
          preserves anything within the box limits, difference removes
          anythin within the box limits (Default value = False)

    Returns:
      str: The modified mesh string

    """
    # cut_at is used to set the limits
    for i in range(3):
        # Always have in the order [min,max]
        if cut_at[i][0] > cut_at[i][1]:
            cut_at[i][0], cut_at[i][1] = cut_at[i][1], cut_at[i][0]

        assert min(cut_at[i]) >= 0,"Error: min(cut_at[i]) must be >= 0"
        assert max(cut_at[i]) <= 1,"Error: max(cut_at[i]) must be <= 1"

        # Avoid artifacts by slightly overshooting limits
        for j in range(2):
            if cut_at[i][j] == 0:
                cut_at[i][j] -= 0.001
            if cut_at[i][j] == 1:
                cut_at[i][j] += 0.001
        cut_at[i][0] *= n[i]
        cut_at[i][1] *= n[i]

    # Adding points to the prism; it gets closed later.
    # Set up to avoiding rotating or translating, so the coordinates
    # work out a little funny because POV-Ray is left-handed.
    # These values are "y" and "z".
    points = [
            [cut_at[1][0], cut_at[2][0]],
            [cut_at[1][1], cut_at[2][0]],
            [cut_at[1][1], cut_at[2][1]],
            [cut_at[1][0], cut_at[2][1]]
            ]

    # Create the prism
    slice_string = (f"\nprism {{ \n\tlinear_sweep\n\tlinear_spline"
            + f"\n\t{cut_at[0][0]}, {cut_at[0][1]}, {len(points)+1}")

    for i in range(len(points)):
        slice_string += f"\n\t<{points[i][0]:.6f}, {points[i][1]:.6f}>, "
    slice_string += f"\n\t<{points[0][0]:.6f}, {points[0][1]:.6f}>"

    # intersection + inverse is the same as difference
    if subtract_box == True:
        slice_string += "\n\tinverse"

    slice_string += f"\n\t}}"

    # Create the intersection
    mesh = f"intersection {{" + mesh +  slice_string + f"\n}}\n\n\t"

    return mesh


def process_field_array(field_array, center=True):
    """Extract field data and dimensionality from simulation data.
    
    POV-Ray and mayavi can't interpret the simulation's output array.

    Args:
      field_array(np.array): simulation output array indexed by
          [z_idx, y_idx, h_idx, E/H, (x, y, z)]
      center(bool, optional): whether to move the origin to the center
          (default True)

    Returns:
      tuple: Electric or magnetic field numpy array and the array
          dimensionality as integers

    Raises:
      RuntimeError: The input array must be 5D

    """
    if field_array.ndim != 5:
        raise RuntimeError("field_array must be 5D")

    # we need to reverse the direction to ensure that renderers put the
    # "top" of the simulation at the "top" of the visualization.
    field_array = field_array[::-1, :, :, :, :]

    # Swap the z, x axes so that we end up with [x, y, z, ...] and
    # extract the dimensionality
    field_array = field_array.swapaxes(0, 2)
    nx, ny, nz, _, _ = field_array.shape

    if center:
        field_array = double_roll(field_array, nx//2, ny//2)
    return field_array, nx, ny, nz


def double_roll(array, n0, n1):
    """Roll the input array along two axes and return the result.
    
    Required because the order of the axes is flipped between S4 and
    what both POV-Ray and mayavi expect.

    Args:
      array(np.array): array to shift. must be >= 2 dimensional
      n0(int): number of elements to shift along first axis
      n1(int): number of elements to shift along second axis

    Returns:
      np.array: Copy of the input array shifted by n0, n1

    """
    return np.copy(np.roll(np.roll(array, n0, axis=0), n1, axis=1))


def extract_components(field):
    """Extract the components of a field

    Args:
      field(np.array): Electric or magnetic field

    Returns:
      list: Lists the components of the field

    """
    ret_list = list()
    for i in range(3):
        ret_list.append(np.abs(field[:, :, :, i]))
    return ret_list


def extract_e_field(field_array):
    """Extract and return components of the electric field.

    Args:
      field_array(np.array): Electric field

    Returns:
      tuple: Electric field vectors and their x,y,z components
      as np arrays

    """
    # obtain the raw e_field
    e_field = field_array[:, :, :, 0, :]
    # obtain the magnitude of each component
    ex, ey, ez = extract_components(e_field)
    return e_field, ex, ey, ez


def extract_h_field(field_array):
    """Extract and return components of the electric field.

    Args:
      field_array(np.array): Magnetic field

    Returns:
      tuple: Magnetic field vectors and their x,y,z components
      as np arrays

    """
    # obtain the raw e_field
    h_field = field_array[:, :, :, 1, :]
    # obtain the magnitude of each component
    hx, hy, hz = extract_components(h_field)
    return h_field, hx, hy, hz


def extract_real_components(field):
    """Extract the real components of a given field.

    Args:
      field(np.array): Electric or magnetic field

    Returns:
      list: Lists the real components of the field

    """
    ret_list = list()
    for i in range(3):
        ret_list.append(np.real(field[:, :, :, i]))
    return ret_list


def calc_field_mag(field):
    """Calculate the magnitude of a given field.

    Args:
      field(np.array): Electric or magnetic field

    Returns:
      np.array: Field magnitude

    """
    from util import deep_access

    # First, we multiply the field by its complex conjugate.
    # (This effectively squares the values of the vector components.)
    # Second, we take the real component. (Multiplying by the complex
    # conjugate guarantees a real result, it is still type complex.)
    # Third, we sum the vector components (x*x + y*y + z*z).
    # Finally, we take the square root.

    return np.sqrt(np.sum(np.real(np.multiply(field,
                                              np.conj(field))), axis=-1))


def calc_energy_density(e_field, h_field, eps_arr):
    """Calculate the local energy density at every point.

    Args:
      e_field(np.array): Electric field
      h_field(np.array): Magnetic field
      eps_arr(np.array): Array of epsilon values

    Returns:
      np.array: Local energy density

    """
    e_mag = calc_field_mag(e_field)
    h_mag = calc_field_mag(h_field)
    return 0.5 * (np.divide(e_mag, eps_arr) + h_mag)
