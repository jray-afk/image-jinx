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
    out_path='test_font.png'
)

sorc.text(
    text='THIS IS MY TEXT!!',
    size=30,
    loc=(100, 100)
)


sorc.show()