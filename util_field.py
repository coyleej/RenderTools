import numpy as np

def process_field_array(field_array, center=True):
    """
    Takes the base array and processes for visualization

    Args:

        field_array: numpy array indexed by
                     [z_idx, y_idx, h_idx, E/H, (x, y, z)]
        center: whether to move the origin to the center (double roll by nx//2,
                ny//2)

    Returns:

        stuff
    """
    # check that the array is appropriately sized
    if field_array.ndim != 5:
        raise RuntimeError("field_array must be 5D")
    # remember that the enemy's gate is down
    # so we need to reverse the direction to ensure that mayavi
    # puts the "top" of the simulation at the "top" of the visualization
    field_array = field_array[::-1, :, :, :, :]
    # then, swap the z, x axes so that we end up with [x, y, z, ...] as
    # required by mayavi
    field_array = field_array.swapaxes(0, 2)
    # extract the dimensionality
    nx, ny, nz, _, _ = field_array.shape
    # now apply the centering if required
    if center:
        field_array = double_roll(field_array, nx//2, ny//2)
    # return values
    return field_array, nx, ny, nz

def double_roll(array, n0, n1):
    """
    Take the input array and roll along two axes

    Args:

        array: array to shift. must be >= 2 dimensional
        n0: number of elements to shift along first axis
        n1: number of elements to shift along second axis

    Returns:

        copy of the input array shifted by n0, n1
    """
    return np.copy(np.roll(np.roll(array, n0, axis=0), n1, axis=1))

def extract_components(field):
    """
    extract the components of a field
    """
    ret_list = list()
    for i in range(3):
        ret_list.append(np.abs(field[:, :, :, i]))
    return ret_list

def extract_e_field(field_array):
    """
    extract and return components of the electric field
    """
    # obtain the raw e_field
    e_field = field_array[:, :, :, 0, :]
    # obtain the magnitude of each component
    ex, ey, ez = extract_components(e_field)
    return e_field, ex, ey, ez

def extract_h_field(field_array):
    """
    extract and return components of the electric field
    """
    # obtain the raw e_field
    h_field = field_array[:, :, :, 1, :]
    # obtain the magnitude of each component
    hx, hy, hz = extract_components(h_field)
    return h_field, hx, hy, hz

def extract_real_components(field):
    """
    extract the real components of a given field
    """
    ret_list = list()
    for i in range(3):
        ret_list.append(np.real(field[:, :, :, i]))
    return ret_list

#def create_grid(Lx, Ly, h1, nx, ny, nz):
#    """
#    create a mesh grid for the system
#    """
#    # create the meshgrid to plot the contours, vectors on
#    # NOTE: this needs to be input in X, Y, Z ordering with "ij" indexing
#    xv, yv, zv = np.meshgrid(np.linspace(-Lx/2, Lx/2, nx),
#                             np.linspace(-Ly/2, Ly/2, ny),
#                             np.linspace(0.0, h1, nz),
#                             sparse=False, indexing="ij")
#    return xv, yv, zv


def calc_field_mag(field):
    """
    Calculate the magnitude of a given field
    """
    # First, we multiply the field by its complex conjugate
    # this will effectively square the values of each of the components
    # of the vector
    # Second, we take the real component. While multiplying by the complex
    # conjugate will guarantee a real result, it is still of type complex
    # Third, we sum the vector components (x*x + y*y + z*z)
    # Finally, we take the square root
    return np.sqrt(np.sum(np.real(np.multiply(field,
                                              np.conj(field))), axis=-1))


def calc_energy_density(e_field, h_field, eps_arr):
    """
    calculate the local energy density at every point
    """
    e_mag = calc_field_mag(e_field)
    h_mag = calc_field_mag(h_field)
    return 0.5 * (np.divide(e_mag, eps_arr) + h_mag)

