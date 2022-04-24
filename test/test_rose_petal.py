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
    out_path='test_rose_petal/test_rose_petal.png'
)


# view how the image changes with increasing petal center noise
petal_center_noises = [0, 10, 20]
for petal_center_noise in petal_center_noises:
    # ask Sorceress to do the alteration
    sorc.rose_petal(
        n_rings=5,
        ring_radius=50,
        petal_center_noise=petal_center_noise,
        n_petals_per_ring=15,
        rand_rotation=360,
        expansion_rate=2.0,
        blur_gradient_easing=jinx.easings.ease_in_quint
    )
    # save this frame
    sorc.save_frame()
    # reload the original image so the alterations don't stack onto next frame if desired. Suppress this to see the
    # effect within the effect!
    # sorc.reload()




