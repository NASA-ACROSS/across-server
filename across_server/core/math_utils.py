import numpy as np


def gc_distance(
    ra1: float | np.ndarray,
    dec1: float | np.ndarray,
    ra2: float | np.ndarray,
    dec2: float | np.ndarray,
) -> np.ndarray:
    """
    Calculates the great circle distance between two coordinates
    or lists of coordinates

    Parameters
    ----------
    ra1: float | np.ndarray
        The RA(s) of the first coordinate(s)
    dec1: float | np.ndarray
        The declination(s) of the first coordinate(s)
    ra2: float | np.ndarray
        The RA(s) of the second coordinate(s)
    dec2: float | np.ndarray
        The declination(s) of the first coordinate(s)

    Returns
    -------
    np.ndarray
        An array of angular separations between the two coordinate
    """
    ra1 = np.radians(ra1)
    dec1 = np.radians(dec1)
    ra2 = np.radians(ra2)
    dec2 = np.radians(dec2)

    return np.degrees(
        2
        * np.arcsin(
            np.sqrt(
                (np.sin((dec1 - dec2) * 0.5)) ** 2
                + np.cos(dec1) * np.cos(dec2) * (np.sin((ra1 - ra2) * 0.5)) ** 2
            )
        )
    )
