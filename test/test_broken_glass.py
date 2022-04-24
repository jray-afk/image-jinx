# not needed in installed version
# run from root project folder
import sys
sys.path.append('src')
# needed in installed version
import jinx
jinx.Jinx.set_out_folder('test/out')

# define the image sorceress
sorc = jinx.Sorceress(
    img_path='test/assets/jinx-test/eye.png',
    out_path='test_broken_glass/test_broken_glass.png'
)

for _ in range(10):
    sorc.broken_glass(
        n_fractures=10,
        bend_chance=0.5,
        max_bend_strength=100,
        max_rand_piece_rotation=10
    )
    sorc.save_frame()

    # Suppress the following for doing this effect within the effect, which produces a fade out effect with more
    # and more fractures. If you don't want this behavior, then make sure to call .reload() to reload original image
    # before applying broken_glass alteration again. (Calling .reload() can allow you to call the effect from scratch
    # many times to get many samples of output images from applying the effect once to choose from.)
    # sorc.reload()


gm = jinx.GifMaker(
    images_folder='test/out/test_broken_glass',
    out_path='test_broken_glass.gif',
    ms_between_frames=100
)
gm.draw()




