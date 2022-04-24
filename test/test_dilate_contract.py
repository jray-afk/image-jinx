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
    out_path='test_dilate_contract/test_dilate_contract.png'
)


sorc.dilate_contract()

