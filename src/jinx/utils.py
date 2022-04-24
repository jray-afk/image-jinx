import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pyautogui
from shapely import geometry
import time

# lock aspect ratio 1:1 x:y for all plots
plt.axes().set_aspect('equal')


def clamp(val, min_val, max_val):
    if val <= min_val:
        return min_val
    if val >= max_val:
        return max_val
    return val


def array_from_img(im):
    im_arr = np.array(im)
    image_width = im_arr.shape[0]
    image_height = im_arr.shape[1]
    # black & white Pillow images do not have a color channel, remove
    if len(im_arr.shape) < 3:
        image_colors = None
    else:
        image_colors = im_arr.shape[2]
    return im_arr, image_width, image_height, image_colors


def angle_degrees(angle):
    """
    Convert angle (degrees) from any integer to between 0-360 degrees.
    :param angle: angle in degrees
    :return:
    """
    angle = (angle % 360) + 360
    return angle


def array_to_img(arr):
    return Image.fromarray(arr.astype('uint8'), 'RGB')


def array_to_img_rgba(arr):
    return Image.fromarray(arr.astype('uint8'), 'RGBA')


def scale(val, min_val, max_val, scale_min=0, scale_max=1):
    """
    Scale value on the scale min_val to max_val to the new scale scale_min to scale_max.

    Default scale-to range is 0 to 1.

           val               x
    ----------------- = ------------
    max_val - min_val   scale_max - scale_min

    =>   x = (val * (scale_max - scale_min)) / (max_val - min_val)

    """
    return (val * (scale_max - scale_min)) / (max_val - min_val)


def debug_pixel_arr(arr):
    img = array_to_img(arr)
    img.show()
    return


def add_alpha_channel(img):
    # arr.size = (n rows, n cols, color size)
    # => if currently RGB, adding alpha channel is appending extra to color size (RGBA)
    # arr.resize(arr.size[0], arr.size[1], 4)
    if img.mode == "RGB":
        a_channel = Image.new('L', img.size, 255)  # 'L' 8-bit pixels, black and white
        img.putalpha(a_channel)
    return img


def empty_alpha(size, return_img=False):
    """
    Return an empty alpha numpy array or Pillow image object the same size as the input array.
    :param arr:
    :return:
    """
    new = np.empty([size[0], size[1], 4])
    if return_img:
        new = array_to_img_rgba(new)
    return new


def add_color_dimension(arr):
    return


def plot_easing(easing):
    xs = np.linspace(0, 1.0, num=10)
    ys = [easing(x) for x in xs]
    plt.plot(xs, ys)
    plt.show()
    return


def plot_shapely(shapely_objs, show_legend=True, invert_y=True):
    """
    Plot a shapely object, like a polygon or linestring.
    :param shapely_objs: Input list of multiple objects or just give one object
    :return:
    """
    # invert matplotlib's y axis so that increasing y value graphically goes down instead of up
    # (like an image pixel y value)
    if invert_y:
        plt.gca().invert_yaxis()
    # create list if only one object given
    if type(shapely_objs) != list:
        shapely_objs = [shapely_objs]
    # iterate through each polygon
    for i, shapely_obj in enumerate(shapely_objs):
        # check type of this object
        print(type(shapely_obj))
        # fill the polygon's exterior a color other than white
        if hasattr(shapely_obj, 'exterior'):
            plt.fill(*shapely_obj.exterior.xy, label=f"{i}")
        else:
            # if there is no exterior, this must be a linestring
            plt.plot(*shapely_obj.xy, label=f"{i}")
        # fill each hole in the polygon white (couldn't get transparent cut out fill to work)
        if hasattr(shapely_obj, 'interiors'):
            for j, hole_linear_ring in enumerate(shapely_obj.interiors):
                plt.fill(*hole_linear_ring.xy, fc='w', label=f"{i}-{j}")
        # if this is a simple Point, just plot the point
        if isinstance(shapely_obj, geometry.point.Point):
            plt.plot(shapely_obj.x, shapely_obj.y, 'o', label=f"{i}")
    # move legend off to the right side of the plot, away from plot area
    if show_legend:
        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    # show the interactive plot window
    plt.show()
    return

def countdown(from_second=3, to_second=0):
    """
    Display countdown to get in position for ScreenGrabber.
    """
    for s in range(from_second, to_second, -1):
        print(f"{s}...")
        time.sleep(1)
    print("Go!!")
    return

def show_mouse_cursor_position():
    """
    Debug for figuring out ScreenGrabber bounding box.
    """
    pos = pyautogui.position()
    print(pos)
    return


