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
    out_path='test_static/test_static.png'
)

# apply static effect...

# do just black & white static
sorc.static(
    amount=0.20,
    pixel_colors=[jinx.colors.WHITE, jinx.colors.BLACK]
)
sorc.save_frame()
sorc.reload()

# do black, white, red static
sorc.static(
    amount=0.20,
    pixel_colors=[jinx.colors.WHITE, jinx.colors.BLACK, jinx.colors.RED]
)
sorc.save_frame()
sorc.reload()


# do white, blue, yellow static. Enable fuzzy coloring by interpolating more
# colors between the given colors
sorc.static(
    amount=0.20,
    pixel_colors=[jinx.colors.WHITE, jinx.colors.NEON_BLUE, jinx.colors.NEON_YELLOW],
    n_fuzzies=5  # number of colors interpolated between each sequence set of colors
)
sorc.save_frame()
sorc.reload()

