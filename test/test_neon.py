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
    out_path='test_neon.png'
)
width, height = sorc.img.size


# apply neon effect
sorc.neon(offset=50)

# save and show
sorc.save()
# sorc.show()


