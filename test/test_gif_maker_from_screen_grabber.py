# not needed in installed version
# run from root project folder
import sys

sys.path.append('src')
# needed in installed version
import jinx

# jinx options if desired
jinx.Jinx.set_out_folder('test/out')
# print(jinx.Jinx.get_out_folder())

gm = jinx.GifMaker(
    images_folder='test/out/test_screen_grabber',
    out_path='test_gif_maker_from_screen_grabber.gif',
    ms_between_frames=60
)
gm.draw()


