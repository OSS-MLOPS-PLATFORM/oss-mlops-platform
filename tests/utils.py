from typing import Union


def parse_bool(val: Union[str, bool]) -> bool:
    """Convert a string representation of truth to True or False.
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1', True):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0', False):
        return False
    else:
        raise ValueError(f"Invalid truth value {val}")
