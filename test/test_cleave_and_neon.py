# not needed in installed version
# run from root project folder
import sys
sys.path.append('src')
# needed in installed version
import jinx
jinx.Jinx.set_out_folder('test/out')

# misc for this example
import numpy as np

# define the image sorceress
sorc = jinx.Sorceress(
    img_path='test/assets/jinx-test/logo.png',
    out_path='test_cleave_and_neon/test_cleave_and_neon.png'
)
width, height = sorc.img.size


# define # of frames to make--10 degrees per frame
center_point = (width//2, height//2)
for cleave_angle in np.arange(0, 370, 10):
    # do some manipulations
    # apply neon effect
    sorc.neon()
    # cleave the image
    sorc.cleave(
        center_point=center_point,
        move_chunk=0,
        pixel_shift=25,
        angle=cleave_angle
    )
    # save frame
    sorc.save_frame()
    # reload image (because I don't want each modification to stack in this case)
    sorc.reload()


# turn output into gif
gm = jinx.GifMaker(
    images_folder='test/out/test_cleave_and_neon',
    out_path='test_cleave_and_neon.gif',
    ms_between_frames=50
)
gm.draw()


