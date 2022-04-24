import mss
import time
from PIL import Image
from .frame_handler import FrameHandler
from .jinx import Jinx


class ScreenGrabber(Jinx):

    def __init__(self,
                 out_path='',
                 bounding_box=None):
        if bounding_box is None:
            bounding_box = {'top': 0,
                            'left': 100,
                            'width': 400,
                            'height': 300}
        self.bounding_box = bounding_box
        self.out_path = self.get_out_path(out_path)
        self.frame_handler = FrameHandler(out_path=self.out_path)
        return

    def capture(self, save=True, show=False):
        """
        Capture single frame.
        :return:
        """
        # with mss.mss() as sct:
        #     # Get rid of the first, as it represents the "All in One" monitor:
        #     for num, monitor in enumerate(sct.monitors[1:], 1):
        #         # Get raw pixels from the screen
        #         sct_img = sct.grab(monitor)
        #         # Create the Image
        #         img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        #         # debug
        #         img.show()

        with mss.mss() as sct:
            # convert given bounding box to top left corner coords and bottom right corner coords
            bbox = (
                self.bounding_box['left'],  # left
                self.bounding_box['top'],  # top
                self.bounding_box['left'] + self.bounding_box['width'],  # right
                self.bounding_box['top'] + self.bounding_box['height']  # lower
            )
            # grab the image
            sct_img = sct.grab(bbox)
            # convert to Pillow image
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            # save
            if save:
                self.frame_handler.save_frame(img)
            # debug
            if show:
                img.show()
        return img

    def run(self,
            save=True,
            show=False,
            duration=3  # seconds
            ):
        """
        Capture frames continuously until user interrupts.
        :param save: save all captured images
        :param show: show all captured images
        :return:
        """
        if duration <= 0:
            print("Running screen grabber, press 'ctrl+c' to quit...")
            while True:
                try:
                    self.capture(save=save, show=show)
                except KeyboardInterrupt:
                    print("Stopped ScreenGrabber.")
                    return
        else:
            print(f"Running screen grabber for {duration} seconds (press 'ctrl+c' to quit)...")
            start_time = time.time()
            while True:
                self.capture(save=save, show=show)
                this_time = time.time()
                total_elapsed = this_time - start_time
                print(str(total_elapsed))
                if total_elapsed >= duration:
                    return
        return



