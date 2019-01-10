#### ---- EXISTING, UNMODIFIED ---- ####

def deep_access(x,keylist):
    """
    Use to access values contained in nested dictionaries
    """
    val = x
    # this effectively unrolls the nest
    for key in keylist:
        val = val[key]
    return val

