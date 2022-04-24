import os
from pathlib import Path
import shutil
from .jinx import Jinx


class FrameHandler(Jinx):

    def __init__(self,
                 out_path,
                 ext='.png',
                 check_existing=False,
                 debug=False):
        self.out_path = out_path
        self.frame_n = 0  # frame number of the next frame to save
        self.ext = ext
        self.temp_suffix = '_jinx_TEMP_5aca738d'  # danger, do not use this string in file paths!
        self.debug = debug

        if check_existing:
            self.load_from_existing_folder()
        return

    def get_parent_directory(self):
        if self.debug: print("out_path", self.out_path)
        return Path(self.out_path).parent.absolute()

    def get_relevant_file_paths(self):
        out_dir = self.get_parent_directory()
        file_paths = os.listdir(out_dir)
        if self.debug: print("out_dir", out_dir)
        if self.debug: print("file_paths", file_paths)
        return file_paths

    def get_sorted_file_paths(self, file_paths=None):
        if file_paths is None:
            file_paths = self.get_relevant_file_paths()
        if self.debug: print("sorted file_paths", file_paths)
        frame_indices = {}
        sorted_file_paths = []
        for file_path in file_paths:
            frame_index = self.get_frame_index_from_path(file_path)
            frame_indices[frame_index] = file_path
        sorted_frame_indices = list(sorted(frame_indices))
        for frame_index in sorted_frame_indices:
            sorted_file_paths.append(frame_indices[frame_index])
        return sorted_file_paths

    def load_from_existing_folder(self):
        """
        Check all PNG files in out_path and set frame_n to the max frame n found in images + 1.

        If you re-run something that uses the FrameHandler, i.e. the image Sorceress, it will continue where it left off
        instead of overwriting all frames starting from 0, which may or may not be desired behavior. By default jinx
        does not check existing, it will overwrite images starting from 0.
        :return:
        """
        file_paths = self.get_relevant_file_paths()
        file_paths = filter(lambda p: self.ext in p, file_paths)
        max_n = 0
        for file_path in file_paths:
            frame_n = self.get_frame_index_from_path(file_path)
            if frame_n > max_n:
                max_n = frame_n
        self.frame_n = max_n + 1
        return

    def get_frame_out_path(self, frame_n):
        path = os.path.normpath(self.out_path)
        path_parts = path.split(os.sep)
        filename = path_parts[-1]
        path_parts.pop()
        frame_filename = f"{frame_n}-{filename}"
        path_parts.append(frame_filename)
        frame_out_path = os.path.join(*path_parts)
        if not frame_out_path.endswith(self.ext):
            frame_out_path += self.ext
        return frame_out_path

    def get_frame_temp_path(self, frame_n):
        frame_ideal_path = self.get_frame_out_path(frame_n)
        tmp_path = ''.join(frame_ideal_path.split(self.ext)) + self.temp_suffix + self.ext
        return tmp_path

    def save_frame(self, img):
        """
        Take the image's base out_path and modify it each time save_frame is called:
        assign an integer value to each frame in file name on save.
        i.e.: with out_path=my_image.png, calling save_frame 3 times will generate
        0-my_image.png, 1-my_image.png, and 2-my_image.py.
        :return:
        """
        frame_out_path = self.get_frame_out_path(self.frame_n)
        # print(frame_out_path)
        img.save(frame_out_path)
        # image saved successfully; increment frame #
        self.frame_n += 1
        return

    def get_frame_index_from_path(self, file_path):
        return int(file_path.split('-')[0])

    def swap_frame_index(self, file_path, new_index):
        new_file_name = str(new_index) + '-' + '-'.join(file_path.split('-')[1:])
        return os.path.join(self.get_parent_directory(), new_file_name)

    def recalc_indices(self):
        """
        Run this if you manually add/delete images to rename the images with correct indices. I.e., if you have a gap
        because you deleted image #2:
            0 -> 1 -> 3 -> 4
        Calling this will re-index and rename the images with the following indices:
            0 -> 1 -> 2 -> 3
        This utility just saves you from having to manually rename a bunch of file names in order for the file names to
        jibe with jinx's systems.
        :return:
        """
        # get all files of interest
        # file_paths = self.get_relevant_file_paths()
        # sort them (else they may go 0, 1, 11... instead of 0, 1, 2...
        file_paths = self.get_sorted_file_paths()
        # rename old file names using good indices
        for new_index, old_file_path in enumerate(file_paths):
            full_old_file_path = os.path.join(self.get_parent_directory(), old_file_path)
            full_new_file_path = self.swap_frame_index(
                file_path=full_old_file_path,
                new_index=new_index
            )
            if full_old_file_path != full_new_file_path:
                os.rename(full_old_file_path, full_new_file_path)
        # finally, update frame_n for index of next frame
        self.frame_n = len(file_paths)
        return

    def rename_all_as_tmp(self):
        tmp_paths = []
        for frame_n in range(self.frame_n):
            current_path = self.get_frame_out_path(frame_n)
            tmp_path = self.get_frame_temp_path(frame_n)
            os.rename(current_path, tmp_path)
            tmp_paths.append(tmp_path)
        return tmp_paths

    def rename_all_without_tmp(self):
        for frame_n in range(self.frame_n):
            tmp_path = self.get_frame_temp_path(frame_n)
            new_path = ''.join(tmp_path.split(self.ext)).replace(self.temp_suffix, '') + self.ext
            os.rename(tmp_path, new_path)
        return

    def reverse_frames(self, start_frame_n=0, end_frame_n=None):
        """
        Reverse all frames, i.e. re-index and rename frames. Example renaming of 4 frames from old index -> new index:
            0 -> 3
            1 -> 2
            2 -> 1
            3 -> 0
        :return:
        """
        # handle inputs for default behavior
        if end_frame_n is None:
            end_frame_n = self.frame_n
        # rename all existing images with temp name
        self.rename_all_as_tmp()
        new_indices = list(range(start_frame_n, end_frame_n))
        new_indices.reverse()
        for old_index, new_index in enumerate(new_indices):
            old_path = self.get_frame_temp_path(old_index)
            new_path = self.get_frame_out_path(new_index)
            # print(old_path, new_path)
            os.rename(old_path, new_path)
        return

    def duplicate_frames(self, reverse=True):
        """
        If reverse is False, duplicates all frames with incremented frame number.

        If reverse is True...
        Duplicate all frames and reverse the order of the duplicates, saving them each as the next incremented
        frame_n. This will give an effect such that animating the frames in a loop will go:
            0 -> 1 -> 2 -> 2 -> 1 -> 0
        Instead of:
            0 -> 1 -> 2 -> 0 -> 1 -> 2
        :return:
        """
        frame_ns = list(range(self.frame_n))
        if reverse:
            frame_ns.reverse()
        for frame_n in frame_ns:
            file_path = self.get_frame_out_path(frame_n)
            new_frame_file_path = self.get_frame_out_path(self.frame_n)
            # copy existing frame to duplicate and
            shutil.copyfile(file_path, new_frame_file_path)
            # copy was successful, increment frame number of next frame
            self.frame_n += 1
        return






