# not needed in installed version
# run from root project folder
import sys

sys.path.append('src')
# needed in installed version
import jinx

jinx.Jinx.set_out_folder('test/out')

# define the image Sorceress
sorc = jinx.Sorceress(
    img_path='test/assets/jinx-test/logo.png',
    out_path='test_wave/test_wave.png'
)

# sorc.show()

# do the wave!
sorc.wave(
    n_chunks=13,
    max_chunk_delta=100,  # in pixels
    axis=1,  # 0 for x, 1 for y
    n_frames=13,
    easing=jinx.easings.ease_in_out_normal,
    include_original=False
)


## save output pngs as gif

# linear animation
# gm = jinx.GifMaker(
#     images_folder='test/out/test_wave',
#     out_path='test_wave.gif',
#     ms_between_frames=30
# )

# non-linear animation
gm = jinx.GifMaker(
    images_folder='test/out/test_wave',
    out_path='test_wave.gif',
    total_duration=1000,
    framerate_easing=jinx.easings.ease_out_quint  # default easing
)

# create the .gif from the .pngs
gm.draw()
