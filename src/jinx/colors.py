
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]

GRAY = [128, 128, 128]
LIGHT_GRAY = [211, 211, 211]

RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]

NEON_PINK = [255, 16, 240]
NEON_BLUE = [70, 102, 255]
NEON_PURPLE = [176, 38, 255]
NEON_YELLOW = [255, 240, 31]


def get_alpha(color, alpha=1.0):
    """
    Get alpha version of color, i.e. same color but with alpha channel added.
    :param color:
    :param alpha: alpha value (0 = fully transparent, 1 = fully opaque)
    :return:
    """
    return [*color, alpha]


