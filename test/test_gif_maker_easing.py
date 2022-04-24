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
    images_folder='test/out/test_cleave',
    out_path='test_gif_maker_easing.gif',
    total_duration=2000,
    framerate_easing=jinx.easings.ease_out_quint
)

gm.draw()

print(f"Final number of frames in .gif: {gm.n_frames}")
print(f"Final ms between frames in .gif: {gm.ms_between_frames}")

