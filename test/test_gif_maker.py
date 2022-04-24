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
    images_folder='test/assets/plain',
    out_path='test_gif_maker.gif'
)
gm.draw()