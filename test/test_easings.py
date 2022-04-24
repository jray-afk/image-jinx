# not needed in installed version
# run from root project folder
import sys
sys.path.append('src')
# needed in installed version
import jinx

import numpy as np

for x in np.arange(0.0, 1.1, 0.1):
    y = jinx.easings.ease_out_cubic(x)
    print((x, y))



