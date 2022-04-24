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
    out_path='test_alpha_border.png'
)

# apply alpha border to edge of image
# see README.md for more information on what easing functions are
sorc.alpha_border(gradient_easing=jinx.easings.ease_in_quint)

# save image
sorc.save()

