import glob
import numpy as np
import os
from pathlib import Path
from PIL import Image, ImageSequence
from .jinx import Jinx
from .frame_handler import FrameHandler
from . import easings
from . import utils


class GifMaker(Jinx):

    def __init__(self,
                 images_folder='',  # either load from images
                 from_gif_path='',  # or load from .gif file
                 out_path='',
                 ms_between_frames=300,  # milliseconds
                 total_duration=None,  # milliseconds
                 framerate_easing=easings.ease_out_quint,
                 frame_handler=None,
                 sample_fraction=None  # define a fraction, i.e. 0.25 for which to down-sample
                 ):
        # IO setup
        self.images_folder = images_folder
        self.from_gif_path = from_gif_path
        # get final out path (including any jinx level folder settings)
        self.out_path = self.get_out_path(out_path)

        # set up frame_handler either from images_folder (default) or a supplied frame_handler object
        if frame_handler is None:
            first_img = os.path.join(self.images_folder, os.listdir(self.images_folder)[0])
            file_basename = first_img.split('-')[-1].replace('.png', '')
            frame_handler_out_path = os.path.join(self.images_folder, file_basename)
            self.frame_handler = FrameHandler(out_path=frame_handler_out_path, check_existing=True)
        else:
            self.frame_handler = frame_handler

        # simplest framerate definition: linear time rate between images
        self.ms_between_frames = ms_between_frames
        # or instead of simple framerate definition, choose...
        # complicated framerate definition: give an easing function and jinx will interpolate frames in between to give
        # easing effect! Note that the framerate is still technically linear; images will just be duplicated to make it
        # appear as if they are put there longer if total_duration is defined, assert that framerate_easing must be
        # defined
        if total_duration is not None:
            if not callable(framerate_easing):
                raise Exception("""Error: total_duration is defined, and so an easing function was expected in 
                framerate_easing. A callable easing function was not found.""")
        self.total_duration = total_duration
        self.framerate_easing = framerate_easing

        # internal vars
        self.n_frames = 0

        return

    def gif_to_frames(self):
        """
        Load GifMaker frames from .gif file and save each frame as .png to images_folder using FrameHandler.
        :return:
        """
        # validate
        if self.from_gif_path == '':
            raise Exception("Error: unable to extract frames from .gif. Path to .gif not supplied.")
        if self.images_folder == '':
            raise Exception("Error: unable to extract frames from .gif. Path to images_folder output not supplied.")
        # convert to frames
        im = Image.open(self.from_gif_path)
        for frame in ImageSequence.Iterator(im):
            self.frame_handler.save_frame(frame)
        return

    # def get_images(self):
    #     # get reference to all png within images_folder path. If images_folder
    #     # is blank, defaults to current working directory
    #     pattern = '*.png'
    #     if self.images_folder == '':
    #         imgs = glob.glob(pattern)
    #     else:
    #         imgs = glob.glob(f'{self.images_folder}/{pattern}')
    #     # raise exception if no images found
    #     # if len(imgs) == 0:
    #     #     raise Exception("Error: no images found. ")
    #     return imgs

    def draw(self):
        """
        Future: allow for only drawing a portion of frames at a time, and then have a utility for joining the .gifs
        together so that you can assign different easing functions to each sub-gif. Would maybe be cool with
        FrameHandler.reverse_frames() effect.
        :return:
        """
        # get images from folder config
        # imgs = self.get_images()
        imgs = self.frame_handler.get_sorted_file_paths()
        # print(imgs)
        imgs = [os.path.join(self.frame_handler.get_parent_directory(), img_path) for img_path in imgs]
        # read in image files and put in frames
        frames = []
        for i in imgs:
            new_frame = Image.open(i)
            frames.append(new_frame)
        n_frames = len(frames)
        if n_frames == 0:
            raise Exception("""Error: unable to draw .gif file, no images found. Make sure that images_folder is
            configured correctly. If you are loading frames from .gif file using from_gif_path, make sure to
            call gif_to_frames() before calling draw().""")
        self.n_frames = n_frames
        # print(out_path)
        # if total_duration is defined, use the framerate_easing to fill interpolated frames up to total duration.
        # Note that Image.save() only accepts a set ms between frames as "duration" parameter, so to trick this
        # we need to have a low ms_between_frames value so frames can be duplicated to give easing effect. Dividing up
        # the frames is bounded by target_max_frames.
        if self.total_duration is not None:
            # calculate new easing x framerate to use as flat framerate once gif is generated
            self.ms_between_frames = self.total_duration // n_frames
            # evaluate easing function to get total ms per frame
            elapsed_ms = np.linspace(0, self.total_duration, num=n_frames)
            easing_x_vals = [utils.scale(x, min_val=0, max_val=self.total_duration) for x in elapsed_ms]
            easing_y_vals = [self.framerate_easing(x) for x in easing_x_vals]
            easing_y_deltas = np.diff(easing_y_vals, prepend=0)
            # # calculate what fraction of total ms each frame is based on easing y deltas
            # y_delt_frac_total = [y_delta/self.total_duration for y_delta in easing_y_deltas]
            # calculate estimated integer n duplications based on pct of target_max_frames
            n_frames_per_frame = [int(y_delt_frac * n_frames) for y_delt_frac in easing_y_deltas]
            n_frames_per_frame = [1 if n == 0 else n for n in n_frames_per_frame]
            # print(n_frames_per_frame)
            # n_frames_per_frame = list(map(lambda x: x+1, n_frames_per_frame))
            # finally, use n frames per frame to duplicate the frames!
            frames_temp = frames.copy()
            frames = []
            for i, frame in enumerate(frames_temp):
                # print(str(i), frame)
                n_frames_this_frame = n_frames_per_frame[i]
                for _ in range(n_frames_this_frame):
                    frames.append(frame)
            # update for developer metrics (in case they don't like how big .gif becomes)
            self.n_frames = len(frames)
        # save frames into .gif that loops forever
        frames[0].save(
            self.out_path,
            format='GIF',
            append_images=frames[1:],
            save_all=True,
            duration=self.ms_between_frames,
            loop=0
        )
        return




