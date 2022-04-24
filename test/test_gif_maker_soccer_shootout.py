# not needed in installed version
# run from root project folder
import sys

sys.path.append('src')
# needed in installed version
import jinx

# jinx options if desired
jinx.Jinx.set_out_folder('test/out')

IMAGES_FOLDER = 'test/out/test_screen_grabber_soccer_shootout'


def make_simple_linear_gif():
    gm = jinx.GifMaker(
        images_folder=IMAGES_FOLDER,
        out_path='soccer_shootout_simple_linear.gif',
        ms_between_frames=60
    )
    gm.draw()
    return


def make_simple_easing_gif():
    gm = jinx.GifMaker(
        images_folder=IMAGES_FOLDER,
        out_path='soccer_shootout_simple_easing.gif',
        total_duration=1750,
        framerate_easing=jinx.easings.ease_in_quart
    )
    gm.draw()
    print(f"Final number of frames in .gif: {gm.n_frames}")
    print(f"Final ms between frames in .gif: {gm.ms_between_frames}")
    return


def make_fwd_backward_easing_gif():
    gm = jinx.GifMaker(
        images_folder=IMAGES_FOLDER,
        out_path='soccer_shootout_fwd_backward_easing.gif',
        total_duration=2000,
        framerate_easing=jinx.easings.ease_out_quint
    )

    # first duplicate the frames and reverse the duplicated frames
    # so the loop will go clip forward -> clip reverse
    # only need to call this once, else will keep adding more frames
    # to /out folder!!
    gm.frame_handler.duplicate_frames(reverse=True)

    # now draw the gif
    gm.draw()
    print(f"Final number of frames in .gif: {gm.n_frames}")
    print(f"Final ms between frames in .gif: {gm.ms_between_frames}")
    return


# make_simple_linear_gif()
# make_simple_easing_gif()
# make_fwd_backward_easing_gif()


