# not needed in installed version
# run from root project folder
import sys
sys.path.append('src')
# needed in installed version
import jinx


# see 'src/jinx/easings.py' for full list of easings available in jinx
# create your own easing function and plot it with plot_easing() to debug it!
jinx.utils.plot_easing(jinx.easings.ease_in_out_expo)



