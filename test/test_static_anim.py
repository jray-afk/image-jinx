# not needed in installed version
# run from root project folder
import sys
sys.path.append('src')
# needed in installed version
import jinx
jinx.Jinx.set_out_folder('test/out')

# define the image sorceress
sorc = jinx.Sorceress(
    img_path='test/assets/jinx-test/logo.png',
    out_path='test_static_anim/test_static_anim.png'
)

# apply static effect...
for i in range(30):
    sorc.static(
        amount=0.20,
        pixel_colors=[jinx.colors.WHITE, jinx.colors.BLACK]
    )
    sorc.save_frame()
    sorc.reload()



# turn output into gif
gm = jinx.GifMaker(
    images_folder='test/out/test_static_anim',
    out_path='PHOTOSENSITIVE WARNING-test_static_anim.gif',
    ms_between_frames=30
)
gm.draw()


