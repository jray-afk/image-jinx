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
    out_path='test_cleave/test_cleave.png'
)
width, height = sorc.img.size
# sorc.show()

# define the pixel x,y to form the break line at
center_point = (width//2, height//2)


# let's make a .gif from this effect where each frame is an angle that rotates in a circle
# (from 0 to 360 degrees at increments of the break line rotating 10 degrees between each frame
# around the center point of the image)
for cleave_angle in np.arange(0, 370, 10):
    # do some manipulations
    sorc.cleave(
        center_point=center_point,

        # move_chunk: 0 moves the first chunk (above the cleave line), 1 moves the 2nd chunk (below the cleave line)
        # note that "above" or "below" is relative to the cleave line itself, which can seem opposite when you
        # pass angles above 180 degrees
        move_chunk=1,

        pixel_shift=100,
        angle=cleave_angle
    )
    # save frame
    sorc.save_frame()
    # reload image (because I don't want each modification to stack in this case)
    sorc.reload()


# turn output into gif
gm = jinx.GifMaker(
    images_folder='test/out/test_cleave',
    out_path='test_cleave.gif',
    ms_between_frames=500
)
gm.draw()


# do single cleave, save and show img
# sorc.cleave(
#     center_point=center_point,
#     pixel_shift=100,
#     angle=30
# )
# sorc.save()
# sorc.show()


