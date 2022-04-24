import os
import math
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageChops, ImageDraw, ImageFont
import random
from shapely import geometry
from shapely import ops
import warnings
from .frame_handler import FrameHandler
from .jinx import Jinx
from . import axioms
from . import colors
from . import easings
from . import utils


class Sorceress(Jinx):

    def __init__(
            self,
            img_path='',
            img=None,
            out_path=''):
        # handle image paths
        self.img_path = img_path
        self.out_path = self.get_out_path(out_path, ext='png')
        # handle extracting image from path or from Pillow image
        if img and img_path != '':
            raise Exception("Error: can only define image from path or a Pillow image.")
        elif img_path != '':
            self.img = Image.open(self.img_path)
        else:
            self.img = img
        # set up frame handler for saving individual frames
        self.frame_handler = FrameHandler(out_path=self.out_path)
        return

    def reload(self):
        self.img = Image.open(self.img_path)
        return

    def show(self):
        self.img.show()
        return

    def save(self):
        # print(self.out_path)
        self.img.save(self.out_path)
        return

    def save_frame(self, img=None):
        """
        By default, save the img object on this Sorceress instance. Optionally can override with transient image object.
        :param img:
        :return:
        """
        if img is None:
            img = self.img
        self.frame_handler.save_frame(img)
        return

    def get_grayscale(self, mode="L"):
        # change Pillow image mode to Grayscale (L)
        return self.img.convert(mode)

    def get_edges(self, fltr=ImageFilter.FIND_EDGES, contrast=1):
        """
        :param fltr:
        :param contrast: adjusts contrast to help with edge detection. 1 gives original image, <1 decreases contrast, >1 increases contrast
        :return:
        """
        # apply grayscale
        img = self.get_grayscale()
        # img.show()
        # can optionally use a custom kernel
        # fltr = ImageFilter.Kernel((3, 3), (-1, -1, -1, -1, 8, -1, -1, -1, -1), 1, 0)
        img = img.filter(fltr)
        # apply contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)
        # img.show()
        return img

    def alpha_border(self,
                     border_radius=10,  # blurred border radius in pixels
                     gradient_easing=easings.ease_out_linear
                     ):
        """
        Add more alpha closer to the border of an image radially to give blurred border effect.
        :return:
        Ref: https://stackoverflow.com/questions/34654824/feathered-edges-on-image-with-pil
        """
        # get numpy array of img
        img = self.img
        new = np.array(img.convert('RGB'))
        # print(new.shape)

        # radially make edges more transparent
        l_row, l_col, nb_channel = new.shape
        rows, cols = np.mgrid[:l_row, :l_col]
        radius = np.sqrt((rows - l_row / 2) ** 2 + (cols - l_col / 2) ** 2)
        alpha_channel = np.zeros((l_row, l_col))
        r_min, r_max = 1. / 3 * radius.max(), 0.8 * radius.max()
        alpha_channel[radius < r_min] = 1
        alpha_channel[radius > r_max] = 0
        gradient_zone = np.logical_and(radius >= r_min, radius <= r_max)
        alpha_channel[gradient_zone] = gradient_easing((r_max - radius[gradient_zone]) / (r_max - r_min))
        alpha_channel *= 255
        feathered = np.empty((l_row, l_col, nb_channel + 1), dtype=np.uint8)
        feathered[..., :3] = new[:]
        feathered[..., -1] = alpha_channel[:]

        # convert feathered set to the new image
        self.img = utils.array_to_img_rgba(feathered)
        return

    def static(self,
               amount=0.10,  # static spawn chance
               pixel_colors=None,  # assuming even chance between colors
               n_fuzzies=0  # ex: value of 2 means 2 colors interpolated between each given color
               ):
        """
        Make image static-y.
        """
        if pixel_colors is None:
            pixel_colors = [colors.WHITE, colors.BLACK]

        im, width, height, _ = utils.array_from_img(self.img)

        # if n_fuzzies given, interpolate a bunch of colors between given colors
        # to append to color list. Number of interpolated points determined by fuzzy_blending
        if n_fuzzies > 0:
            given_colors = pixel_colors.copy()
            for ix, gc in enumerate(given_colors):
                if ix+1 != len(given_colors):
                    gc_next = given_colors[ix+1]
                    color_rng = np.array(gc_next) - np.array(gc)
                    color_delta = color_rng//n_fuzzies
                    for _ in range(n_fuzzies):
                        fuzzy_color = gc + color_delta
                        fuzzy_color = list(fuzzy_color)
                        pixel_colors.append(fuzzy_color)
        # remove duplicates (list type is unhashable; convert to tuple then back to list)
        pixel_colors = list(set(map(tuple, pixel_colors)))
        pixel_colors = list(map(list, pixel_colors))
        # debug
        # print([p for p in pixel_colors])
        # give each pixel chance of going rogue
        for x in range(width):
            for y in range(height):
                coin_toss = random.uniform(0, 1)
                if coin_toss < amount:
                    im[x][y] = random.choice(pixel_colors)
        # convert back to PIL img and set
        im = utils.array_to_img(im)
        self.img = im
        return

    def wave(self,
             n_chunks=13,
             max_chunk_delta=100,  # in pixels
             axis=1,  # 0 for x, 1 for y
             n_frames=13,
             easing=easings.ease_in_out_normal,
             include_original=True
            ):
        # validate inputs
        if axis not in [0, 1]:
            raise Exception("Error: unable to understand wave axis, was expecting 0 or 1 (for x or y).")

        # width, height = self.img.size
        # print(self.img.size)
        im, width, height, _ = utils.array_from_img(self.img)
        # new = im.copy()

        chunkpoints = np.linspace(0, width, num=n_chunks+1)
        chunkpoints = [int(cp) for cp in chunkpoints]
        chunk_x_min_maxs = []
        for i, cp in enumerate(chunkpoints):
            if i != 0:
                chunk_x_min_maxs.append((chunkpoints[i-1], cp))
        # print(chunk_x_min_maxs)

        # if include_original, save the first frame as unaltered image without wave effect
        if include_original:
            self.save_frame()

        # generate frames
        for frame_n in range(n_frames):
            # start from new array each frame
            new = im.copy()
            # update position of each chunk
            for chunk_n, chunk_x_min_max in enumerate(chunk_x_min_maxs):
                x_left, x_right = chunk_x_min_max
                new_e = easing((frame_n - chunk_n) / n_frames)
                new_e = utils.clamp(new_e, 0, 1)
                chunk_shift_y = int(new_e * max_chunk_delta)
                # print(chunk_n, x_left, x_right, new_e, chunk_shift_y)
                if axis == 1:
                    new[x_left:x_right, :] = np.roll(
                        new[x_left:x_right, :],
                        chunk_shift_y,
                        axis=1
                    )
                elif axis == 0:
                    new[:, x_left:x_right] = np.roll(
                        new[:, x_left:x_right],
                        chunk_shift_y,
                        axis=0
                    )
            img = utils.array_to_img(new)
            self.save_frame(img)
        return

    def cleave(self,
               center_point=(0,0),
               move_chunk=0,
               pixel_shift=100,
               angle=0):
        """
        Linearly cleave (cut) image and shift one of its chunks.
        :param center_point: pixel at which to center the cleave of the image; use this to shift cleave
            line up/down (b value in linear regression)
        :param move_chunk: selects which chunk to move after image is cleaved; 0 for first chunk, 1 for 2nd
        :param pixel_shift: how many pixels to shift selected chunk to move
        :param angle: angle at which to cleave (0 = horizontal, 90 = vertical)
        :return:
        """
        # sanitize angle input to be between 0-360
        # angle = utils.angle_degrees(angle)
        # convert image to numpy array and set up new image array
        im, width, height, _ = utils.array_from_img(self.img)
        new = im.copy()
        # calculate cleave line slope from angle; soh cah toa, where hypotenuse = 1!
        pixel_scalar_x = math.cos(math.radians(angle))
        pixel_scalar_y = math.sin(math.radians(angle))
        m = pixel_scalar_y / pixel_scalar_x
        # print(pixel_scalar_x, pixel_scalar_y, m)

        def cleave_line(c_x):
            """
            graphtoy.com to visualize what's happening: sin(t)/cos(t) * x
            Calculate equation of line given its slope (weknowdis) and 1 point (i.e. the center point,
            we also knowdis)
            :param c_x: x value of cleave line to evaluate (i.e. get cleave line y value from)
            :return:
            """
            return int(m*(c_x - center_point[0]) + center_point[1])

        # # debug drawing the cleave line on image
        # for x in range(width):
        #     y = cleave_line(x)
        #     if (0 < x < width) and (0 < y < height):
        #         new[x][y] = colors.RED

        def shift_pixel(x, y):
            x_new = x + int(pixel_scalar_x * pixel_shift)
            y_new = y + int(pixel_scalar_y * pixel_shift)
            if (0 < x_new < width) and (0 < y_new < height):
                new[x_new][y_new] = im[x][y]
            return

        # iterate through each pixel, shifting it if applicable
        for x in range(width):
            for y in range(height):
                y_c = cleave_line(x)
                # print(y, y_c)
                if (y < y_c) and move_chunk == 0:
                    # if move_chunk == 0, move the first chunk "before" (relatively) the line
                    shift_pixel(x, y)
                elif (y > y_c) and move_chunk == 1:
                    # if move_chunk == 1, move the first chunk "after" (relatively) the line
                    shift_pixel(x, y)

        # finally, convert numpy array back to image and save set to this instance
        new = utils.array_to_img(new)
        self.img = new
        return

    def broken_glass(self,
                     n_fractures=10,
                     bend_chance=0.5,
                     max_bend_strength=100,
                     max_rand_piece_rotation=10  # in degrees
                     ):
        """
        Give effect as if the image is a flat glass piece and was dropped.
        :param n_fractures: number of cuts onto the image per level of recursion.
        :param bend_chance: chance of each fracture having a midpoint from which to bend
        :param max_bend_strength: max number of pixels to shift midpoint of fracture in x and y if the
            fracture is bent
        :param max_rand_piece_rotation: in degrees, the max degrees in either direction to jitter a
            broken piece
        :return:
        """

        im, width, height, _ = utils.array_from_img(self.img)

        img_poly = geometry.Polygon([
            (0, 0),
            (width, 0),
            (width, height),
            (0, height)
        ])

        # debug
        # utils.plot_shapely(img_poly)
        # line_funcs = []
        lines = []
        ext_coords = img_poly.exterior.coords
        warnings.simplefilter('ignore', np.RankWarning)  # ignore RankWarning for simple linear fit
        for i, coords in enumerate(ext_coords):
            if i == 0:
                continue
            prev_coords = ext_coords[i - 1]
            # get LineString from 2 points
            line = geometry.LineString([prev_coords, coords])
            lines.append(line)

        # split the image polygon into several sub-polygons
        polygons = [img_poly]

        def fracture(polys, fracture_n):
            # select random polygon to fracture
            i, poly = random.choice(list(enumerate(polys)))
            # utils.plot_shapely(poly)
            # for i, poly in enumerate(polys):
            # to create each fracture...
            # randomly select 2 lines in the image polygon without choosing same line
            line1_ix, line1 = random.choice(list(enumerate(lines)))
            # print(str(line1_ix))
            line2_choices = lines.copy()
            del line2_choices[line1_ix]
            line2 = random.choice(line2_choices)
            # print(line1, line2)
            # randomly select a point on each line to connect to each other
            line1_rand_pt = line1.interpolate(random.random(), True)
            line2_rand_pt = line2.interpolate(random.random(), True)
            # generate a LineString from these 2 points
            points = [line1_rand_pt, line2_rand_pt]
            cut_line = geometry.LineString(points)
            # if the line should be bent, add a midpoint and jitter it to give bending effect
            bend_chance_eval = random.uniform(0, 1.0)
            if bend_chance_eval < bend_chance:
                # get random progress value from 0 (start of line) to 1 (end of line), where
                # 0.5 represents the perfect half way point. This will place the center point of
                # the bend.
                progress_amount = random.uniform(0, 1.0)
                # get point at this progress %
                mid_point = cut_line.interpolate(progress_amount, normalized=True)
                # print(mid_point)
                # print(mid_point.coords)
                x, y = mid_point.x, mid_point.y
                x += random.uniform(-max_bend_strength, max_bend_strength)
                y += random.uniform(-max_bend_strength, max_bend_strength)
                cut_line = geometry.LineString([
                    cut_line.coords[0],
                    (x, y),
                    cut_line.coords[1]
                ])

            # split the polygon into 2 by the LineString connecting the 2 random points on the edges
            new_polys = ops.split(poly, cut_line)
            # remove the old polygon
            del polys[i]
            # extend the polygons list with the new polygons
            polys.extend(new_polys.geoms)
            # debug
            # print(points)
            # for poly in new_polys.geoms:
            #     utils.plot_shapely(poly)
            # check for exit condition... i.e. if we have already done enough fractures
            if fracture_n >= n_fractures - 1:
                return polys
            # if not enough fractures, recursively call this function again!
            return fracture(polys, fracture_n + 1)

        # call the recursive function, initializing the fracture # at 0
        polygons = fracture(polygons, 0)

        # debug
        # show one shape at a time
        # for poly in polygons:
        #     utils.plot_shapely(poly)
        # show all together
        # utils.plot_shapely(polygons)

        # THE FOLLOWING SECTION IS NOT NEEDED, I was simply reading the x and y-axis scaling wrong on plot_shapely() :')
        # the above plot with all shapes together looks good with the pieces overlapping, but not
        # each piece individually
        # clean up polygons so they each represent a pieces itself, not the leftover blocks from
        # the cuts
        # polygons_temp = polygons.copy()
        # polygons = []
        # # for each polygon...
        # for i, i_poly in enumerate(polygons_temp):
        #     # copy this polygon so we can prepare to trim it
        #     trimmed_poly = i_poly
        #     # for each polygon to subtract from the trimmed polygon...
        #     for j, j_poly in enumerate(polygons_temp):
        #         # if the polygon is the same as the polygon we're trying to trim, don't do anything;
        #         # if we subtract the polygon from itself we get nothing!
        #         if i == j:
        #             continue
        #         # otherwise, if this is any other polygon, we want to subtract it if it intersects
        #         if j_poly.intersects(trimmed_poly):
        #             trimmed_poly = trimmed_poly.difference(j_poly)
        #     # finally, after doing all the trimming against other shapes, append onto final list of
        #     # polygons
        #     polygons.append(trimmed_poly)
        # now debug again--the shapes should now be correct! Be careful with x/y axis scaling as you
        # view the plot of each piece, that may trip you up
        # utils.plot_shapely(polygons)
        # for poly in polygons:
        #     utils.plot_shapely(poly)

        # now that we have the geometry of each glass piece, extract only the pixels that match
        # this geometry from the numpy image pixel array

        # def extract_geometry(args):
        #     """
        #     If this point does not belong in this polygon, make it transparent, otherwise
        #     leave the point its pre-existing color.
        #     :return:
        #     """
        #     x, y, poly = args
        #     pt = geometry.Point((x, y))
        #     if not poly.contains(pt):
        #         return colors.get_alpha(colors.BLACK)
        #     return poly[x][y]

        # add an alpha channel to the numpy array, keeping its other pixel colors, by converting to
        # Pillow image and then back to an array again
        alpha_im = im.copy()
        alpha_im = utils.array_to_img_rgba(alpha_im)
        alpha_im = utils.array_from_img(alpha_im)[0]
        # for each polygon, copy the image, and for any pixels that are not inside the polygon make them transparent
        piece_imgs = []
        for poly in polygons:
            poly_arr = alpha_im.copy()
            for x in range(width):
                for y in range(height):
                    pt = geometry.Point((x, y))
                    if not poly.contains(pt):
                        poly_arr[x][y] = colors.get_alpha(colors.BLACK)
            # poly_arr = np.array(list(map(extract_geometry, [x, y, poly])))
            piece_img = utils.array_to_img_rgba(poly_arr)
            piece_imgs.append(piece_img)

        # TODO: randomly remove small pieces smaller than an area threshold?

        # jitter the rotation of each piece a little
        piece_imgs_tmp = piece_imgs.copy()
        piece_imgs = []
        for piece_img in piece_imgs_tmp:
            rand_rot = random.uniform(-max_rand_piece_rotation, max_rand_piece_rotation)
            piece_img = piece_img.rotate(rand_rot)
            piece_imgs.append(piece_img)

        # now paste all pieces onto final empty alpha, preserving alpha with the paste
        alpha_im = utils.empty_alpha((width, height), return_img=True)
        for piece_img in piece_imgs:
            alpha_im.paste(
                piece_img,
                (0,0),
                piece_img
            )

        # debug
        # alpha_im.show()

        # finally, update the Sorceress instance
        self.img = alpha_im
        return

    def text(self,
             text='TEXT',
             size=12,
             loc=(0, 0),
             font_path='',
             color=colors.WHITE):
        """
        Add text to the image.
        """
        # set default font
        if font_path == '':
            font_path = os.path.join(Jinx.fonts_folder, 'ClearSans-Regular.ttf')
        # print(font_path)
        # sanitize color to tuple
        color = tuple(color)
        # draw the text
        draw = ImageDraw.Draw(self.img)
        font = ImageFont.truetype(font_path, size)
        draw.text(
            loc,
            text,
            color,
            font
        )
        return

    def neon(self,
             neon_colors=None,
             thickness=5,
             offset=200,
             white_fill_thresh=230,
             black_thresh=50,
             blur_radius=1.5):
        """
        Detect edges on image, copy the edges, offset them, change their color
        to give multi-color glow effect to image.
        """
        # Pillow only allows max kernel size of 5, raise error
        if thickness > 5:
            raise Exception("Error: max thickness is 5.")

        # get default neon colors
        if neon_colors is None:
            neon_colors = [colors.NEON_PINK,
                           colors.NEON_BLUE,
                           colors.NEON_PURPLE]
            # shuffle image color order for fun
            random.shuffle(neon_colors)

        # get edges from image
        grayscale = self.get_grayscale()
        edges = grayscale.filter(ImageFilter.FIND_EDGES)
        # edges.show()

        # get numpy pixel array from image
        im, width, height, _ = utils.array_from_img(self.img)
        final_im = np.zeros(im.shape)

        # duplicate edges by however many colors there are and color all the white pixels (defined by threshold
        # val below) that neon color
        neon_imgs = []
        for neon_color in neon_colors:
            neon_img = edges.copy()
            # make neon lines thicker
            neon_img = neon_img.filter(ImageFilter.MaxFilter(size=thickness))
            # add glow by blurring and then re-drawing line
            # neon_img = neon_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            # neon_img = neon_img.filter(ImageFilter.BLUR)
            # offset a bit randomly in any direction
            rand_x = random.uniform(0, 1)
            rand_y = random.uniform(0, 1)
            neon_img = ImageChops.offset(neon_img, int(rand_x*offset), int(rand_y*offset))
            # convert to numpy array
            neon_im, width, height, _ = utils.array_from_img(neon_img)
            # create new blank reference with color channel -- need to do this .shape on original image because it still
            # has color channel
            new_neon_im = np.zeros(im.shape)
            # fill color channel with neon color instead of white from grayscale
            new_neon_im[neon_im > white_fill_thresh] = neon_color
            # convert to image and append this neon image to list of neon images to overlay
            # new_neon_im = utils.array_to_img(new_neon_im)
            neon_imgs.append(new_neon_im)
            # debug
            # new_neon_im.show()
        # combine base image on top of all neon images
        for neon_img in neon_imgs:
            final_im[neon_img > black_thresh] = neon_img[neon_img > black_thresh]
        final_im[im > black_thresh] = im[im > black_thresh]
        # convert np array to img and update img ref
        final_im = utils.array_to_img(final_im)
        self.img = final_im
        # debug
        # final_im.show()
        return

    def rose_petal(self,
                   size=None,
                   n_rings=5,
                   paste_order=0,  # 0 for starting out to in, 1 for in to out
                   ring_radius=50,  # in pixels
                   petal_center_noise=25,  # in pixels; randomly shift points a little from ring
                   n_petals_per_ring=15,
                   rose_center=None,  # center of the rose circle from which all rings will bloom
                   rand_rotation=0,  # in max degrees, amount of randomness in petal rotation around ring
                   expansion_rate=2.0,  # matches the scale of the outer ring compared to original
                   expansion_direction=0,  # 0 for petals on outside bigger, 1 for petals on inside bigger
                   resolution_downscale=0.25,  # will help with run time since we may be pasting so many
                   blur_gradient_easing=easings.ease_out_linear
                   ):
        """
        Add rose petal effect. Take image, paste it a bunch of times as petals in circular rings.
        :param size: final size of the image. Increase this if you are not downscaling the image
        :param n_rings: number of concentric rings for which to draw petals
        :param expansion_rate: if equal to 1, no expansion. If greater than 1, image will be bigger the bigger the ring
            radius. If between 0 and 1, the image will be smaller the bigger the ring radius.
        :param resolution_downscale: factor by which to make image smaller before pasting it all
            over as rose petals
        :param blur_gradient_easing: function at which to control the rate of blur as radius from
            image center increases
        :return:
        """
        # handle inputs
        if size is None:
            size = self.img.size
        # if bg_color is None:
        #     bg_color = colors.WHITE
        # if blur_color is None:
        #     blur_color = colors.WHITE
        # downsize reference image
        # self.img.show()
        ref_img = self.img.copy()
        # print(self.img.size)
        new_size = (ref_img.size[0] * resolution_downscale, ref_img.size[1] * resolution_downscale)
        new_size = list(map(int, new_size))
        # print(new_size)
        # thumbnail operation rescales image
        ref_img.thumbnail(new_size, Image.ANTIALIAS)
        # img.show()
        # blur edges on reference photo by creating new Sorceress from this image and calling
        # .alpha_border! So meta!
        ref_sorc = Sorceress(img=ref_img)
        ref_sorc.alpha_border(gradient_easing=blur_gradient_easing)  # radius=edge_blur_radius
        # ref_sorc.show()
        ref_img = ref_sorc.img
        # ref_img.show()
        # set up final pixel array (add RGBA color dimension to end)
        size = (size[0], size[1], 4)
        # new = np.zeros(size)
        # bg_color.append(0)  # add alpha channel
        # new[:, :] = bg_color
        new = np.empty(size)
        new_img = utils.array_to_img_rgba(new)  # Image.fromarray(new.astype('uint8'), 'RGBA')
        # im, width, height, _ = utils.array_from_img(self.img)

        if rose_center is None:
            rose_center = (new.shape[0]//2, new.shape[1]//2)  # center the circle at the center of the new image
        # print(rose_center)

        # calculate ring radii based on expansion rate. Expansion rate of 1 means the radii increase linearly,
        # <1 means the distance between rings get shorter the farther out, >1 means the distance between
        # rings gets greater the farther out
        # ring_radii = np.linspace(ring_radius, ring_radius * n_rings, n_rings)
        def get_ring_radius(rn):
            max_radius = ring_radius * n_rings
            if expansion_rate == 1:
                return ((max_radius - ring_radius)/n_rings) * rn
            elif expansion_rate < 1:
                return ((ring_radius - ring_radius*n_rings)/(n_rings**2)) * (rn - n_rings)**2 + ring_radius*n_rings
            elif expansion_rate > 1:
                return ((ring_radius*n_rings - ring_radius)/(n_rings**2)) * (rn**2) + ring_radius
            return None
        ring_radii = [get_ring_radius(rn) for rn in range(n_rings)]
        # print(ring_radii)
        # reverse the order of the radii array so the petal copies will be pasted in order of outer-most
        # to inner-most ring
        if paste_order == 0:
            ring_radii = np.flip(ring_radii)
        # get how many radians each petal will sweep
        radians_per_petal = axioms.CIRCLE_TOTAL_RADIANS / n_petals_per_ring
        # paste altered reference photo onto final image many times, once for each petal!
        # paste_coords = []
        for ring_n, ring_radius in enumerate(ring_radii):
            ring_elapsed_radians = 0
            for _ in range(n_petals_per_ring):
                # get true x/y value along ring
                x = ring_radius * math.cos(ring_elapsed_radians) + rose_center[0]
                y = ring_radius * math.sin(ring_elapsed_radians) + rose_center[1]
                # add some noise if desired (no noise if petal_center_noise=0) (thank u for
                # fucking it up c: )
                x += random.uniform(-petal_center_noise, petal_center_noise)
                y += random.uniform(-petal_center_noise, petal_center_noise)
                # finally, convert theoretical x/y values to integer pixel locations
                x = int(x)
                y = int(y)
                # only continue if point within image bounds
                if (0 < x < size[0]) and (0 < y < size[1]):
                    # make a copy of the reference image just for this petal
                    petal_img = ref_img.copy()
                    # resize the petal based on expansion rate
                    if expansion_direction == 0:
                        expansion_multiplier = ((1-expansion_rate)/(n_rings-1)) * (ring_n+1) + expansion_rate
                    else:
                        expansion_multiplier = ((expansion_rate-1)/(n_rings-1)) * (ring_n+1)
                    # print(f"{expansion_rate}, {n_rings}, {ring_n}, {expansion_multiplier}")
                    new_size = (
                        int(ref_img.size[0] * expansion_multiplier),
                        int(ref_img.size[1] * expansion_multiplier)
                    )
                    if expansion_multiplier < 0:
                        new_size = (new_size[0] * -1, new_size[1] * -1)
                        petal_img.thumbnail(new_size, Image.ANTIALIAS)
                    else:
                        petal_img = petal_img.resize(new_size)
                    # print(ref_img.size, new_size)

                    # rotate image a little bit
                    rand_rot = random.uniform(-rand_rotation, rand_rotation)
                    petal_img = petal_img.rotate(rand_rot, Image.NEAREST, expand=1)

                    # print((x, y))
                    # calculate x/y corner positions (we want center of image to be pasted on xy coord)
                    x_tl_corner = x - petal_img.size[0]//2
                    y_tl_corner = y - petal_img.size[1]//2
                    # paste the image here!
                    new_img.paste(
                        petal_img,  # image to paste
                        (x_tl_corner, y_tl_corner),  # location at which to paste image
                        petal_img  # mask used to paste the image--this retains alpha channel
                    )
                    # debug point at which to paste image as red dot!
                    # red_alph = [colors.RED[0], colors.RED[1], colors.RED[2], 1]
                    # new[x][y] = red_alph
                    # instead, paste later so that we can shuffle the list of coords and paste
                    # in a random order?
                    # paste_coords.append((x_tl_corner, y_tl_corner))
                # finally, increment the angle segment to go to next petal
                ring_elapsed_radians += radians_per_petal
                # debug each petal
                # utils.debug_pixel_arr(new)
            # debug each ring
            # utils.debug_pixel_arr(new)
        # # re-organize the corrdinates if random shuffle desired
        #
        # # iterate thru the coordinates
        # new_img.paste(
        #     ref_img,  # image to paste
        #     (x_tl_corner, y_tl_corner),  # location at which to paste image
        #     ref_img  # mask used to paste the image--this retains alpha channel
        # )

        # do paste for very center of rose
        new_img.paste(
            ref_img,  # image to paste
            rose_center,  # location at which to paste image
            ref_img  # mask used to paste the image--this retains alpha channel
        )

        # using debug array
        # img = utils.array_to_img(new)
        # img.show()
        # update this instance's img
        self.img = new_img
        # debug
        # self.img.show()
        return

    def gradient(self):
        """
        Add gradient filter over image.
        """
        return

    def offset(self,
               rect=None,
               ):
        """
        Define sub-region within image to offset.
        :return:
        """
        if rect is None:
            rect = (0, 0, 0, 0)
        return

    def scuff(self):
        """
        Scuff up image.
        :return:
        """
        # self.img = self.get_grayscale()
        # self.img = self.get_edges()
        # self.save()
        # self.show()
        return

    def glitch(self):
        return

    def stripe(self):
        return

    def tree(self):
        """
        An abstract drawing of a tree-like structure, which could be interpreted as tree branches
        or veins or a river delta or whatever.
        :return:
        """
        return

    def snake(self,
              ring_inner_radius=200,
              ring_outer_radius=300,
              ring_center=(0,0),
              n_pieces=3,
              piece_connector_easing=easings.ease_in_out_normal
              ):
        """
        Add snake effect. Make image rotate around in an offset circle, so it loops around
        back into itself.
        :return:
        """

        im, width, height, _ = utils.array_from_img(self.img)
        # print((width, height))

        center_pt = geometry.point.Point(ring_center)
        inner_circle = center_pt.buffer(ring_inner_radius)  # returns polygon object
        outer_circle = center_pt.buffer(ring_outer_radius)  # returns polygon object
        # utils.plot_shapely([inner_circle, outer_circle])
        # print(inner_circle, outer_circle)

        # cut the inner circle out of the outer circle geometry to create donut (snake)
        inner_circle_coords = inner_circle.exterior.coords
        outer_circle_coords = outer_circle.exterior.coords
        snake = geometry.Polygon(shell=outer_circle_coords, holes=[inner_circle_coords])  # exterior, list of holes
        # print(snake)
        # utils.plot_shapely(snake)

        # equally divide the circumference of the rings into n_pieces, i.e. extract every n_coords//n_pieces
        # coordinate from list
        # print((len(inner_circle_coords), len(outer_circle_coords)))
        inner_slice_pts = inner_circle_coords[::len(inner_circle_coords) // n_pieces]
        outer_slice_pts = outer_circle_coords[::len(outer_circle_coords) // n_pieces]
        # print((inner_slice_pts, outer_slice_pts))
        # test_objs = [snake, geometry.Polygon(inner_slice_pts, [outer_slice_pts])]
        # utils.plot_shapely(test_objs)

        slice_pt_pairs = list(zip(inner_slice_pts, outer_slice_pts))
        # print(slice_pt_pairs)
        # for p in slice_pt_pairs:
        #     print(p)
        cut_lines = []
        for pair in slice_pt_pairs:
            cut_line = geometry.LineString(pair)
            cut_lines.append(cut_line)

        # test_objs = [snake, *cut_lines]
        # utils.plot_shapely(test_objs)

        # handle the floor division creating too many cut lines (just pop off however many extra there are)
        n_pieces_diff = len(cut_lines) - n_pieces
        for _ in range(n_pieces_diff):
            cut_lines.pop()

        # test_objs = [snake, *cut_lines]
        # utils.plot_shapely(test_objs)

        # TODO: warp each line depending on the piece_connector_easing

        # can't do ops.split by line because cutting a line into the donut does not produce 2 new polygons since
        # the sides will still touch... so, get pairs of all cut_lines in sequence and turn cut_lines into triangles.
        # 4 cut lines = 4 triangles each at 90 deg angle, 3 cut lines = 3 triangles each at 60 deg angle. So of each
        # triangle is 360 / n triangles
        # debug before we extend the cut lines
        # utils.plot_shapely(cut_lines)
        cut_lines_temp = cut_lines.copy()
        cut_lines = []
        for cut_line in cut_lines_temp:
            # replace first point with center point of circle,
            # replace 2nd point with 2nd point scaled up in size arbitrarily so that the resulting triangles using
            # this edge do not create a cord in the circle when we do the split (the segment produced in the triangle
            # will be outside the circle and so we're only cutting perpendicular to the donut edges)
            safe_expansion_scalar = 3  # this is the arbitrary scalar to scale up the cut line
            cut_line = cut_line.coords
            cut_line = [
                center_pt,
                (cut_line[1][0] * safe_expansion_scalar, cut_line[1][1] * safe_expansion_scalar)
            ]
            cut_line = geometry.LineString(cut_line)
            cut_lines.append(cut_line)
        # debug after extending the cut lines
        # utils.plot_shapely(cut_lines)

        # now create pairs of cut lines to form triangles
        triangles = []
        # duplicate the first cut line and append it at the end (because I'm lazy) so that the last triangle
        # can be formed
        cut_lines.append(cut_lines[0])
        for i, cut_line in enumerate(cut_lines):
            if i == 0:
                continue
            prev_cut_line = cut_lines[i-1]
            # create new line segment connecting the outer points of the 2 cut lines
            # (not inner point which is coords[0]; this is already connected in the previous step--at the circle
            # center!)
            # this 3rd line is just so when we debug plot_shapely we can make sure that this line is not intersecting
            # the donut!
            new_line_seg = geometry.LineString(
                [
                    prev_cut_line.coords[1],
                    cut_line.coords[1]
                ]
            )
            # create triangle geometry from the 3 lines by converting the 3 LineStrings
            # into 1 LineString
            # grabbing its convex hull results in a polygon, but splitting a polygon by a polygon is not supported
            lines = [prev_cut_line, cut_line, new_line_seg]
            all_pts = []
            for line in lines:
                line_pts = [line.coords[0], line.coords[1]]
                for pt in line_pts:
                    if pt not in all_pts:
                        all_pts.append(pt)
            # duplicate first point and add to the end to connect the linestring
            all_pts.append(all_pts[0])
            ls = geometry.LineString(all_pts)
            # triangle = ls.convex_hull
            # triangles.append(triangle)
            # triangles.append(triangle)
            triangles.append(ls)
            # debug just this triangle
            # debug_objs = [ls, snake]
            # utils.plot_shapely(debug_objs)
        # debug triangles!
        # debug_objs = triangles.copy()
        # debug_objs.append(snake)
        # utils.plot_shapely(debug_objs)

        # now cut the donut by the triangular LineStrings
        pieces = []
        for t in triangles:
            result = ops.split(snake, t)
            # only keep the smaller piece resulting from the cut
            piece_cut = result.geoms[0]
            for geom in result.geoms:
                # utils.plot_shapely(geom)
                if geom.area < piece_cut.area:
                    piece_cut = geom
            pieces.append(piece_cut)
        # debug donut cut pieces! yay, it works!
        # utils.plot_shapely(pieces)

        # find the center point of each donut piece
        piece_centers = []
        for piece in pieces:
            piece_centers.append(piece.centroid)
        # debug centroids
        # debug_objs = [*pieces, *piece_centers]
        # utils.plot_shapely(debug_objs)


        return

    def banner(self):
        """
        Shade a background a bit in some spots to give cloth-like effect.
        :return:
        """
        return

    def glare(self):
        """
        Add glossy glare effect. Change light source to allow multiple lights in a ring.
        :return:
        """
        return

    def dilate_contract(self,
                        amount=-1  # positive to dilate, negative to contract
                        ):
        """
        Given a region/filter to identify the region, dilate or contract this region.
        Like the pupil of an eye!
        :return:
        """
        self.img.show()
        edges = self.get_edges(contrast=1)
        edges.show()
        return

    def stereogram(self):
        """
        Give a left and right image, and jinx separate the red and cyan, define the shake amount.
        :return:
        """
        return

    def kuwahara(self):
        return

    def swirl(self):
        return

    def glitch(self):
        return

    def stripe(self):
        return







