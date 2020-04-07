"""Extract and manipulate numpy field data.

Functions to extract field data from a numpy array and manipulating 
them into a form that scikit-image's meshing tools can handle.

A quick summary of these functions:
  * process_field_array reformats the data into something that
      the renderers (povray, mayavi) can process
  * double_roll adjusts the axes so that things aren't flipped
      when you go to plot them
  * extract_* extract varying information from the numpy array
  * calc_* calculate various things based on the data
"""
import numpy as np

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
    # "top" of the simulation at the "top" of the visualization
    field_array = field_array[::-1, :, :, :, :]

    # swap the z, x axes so that we end up with [x, y, z, ...] and
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

