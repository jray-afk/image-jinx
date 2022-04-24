# not needed in installed version
# run from root project folder
import sys
sys.path.append('src')
# needed in installed version
import jinx
jinx.Jinx.set_out_folder('test/out')


sg = jinx.ScreenGrabber(
    out_path='test_screen_grabber/test_screen_grabber.png',
    bounding_box={'top': 0, 'left': 0, 'width': 1200, 'height': 935}
)

# wait a couple seconds before recording to get situated
jinx.utils.countdown()

# capture one image
# sg.capture(save=True, show=True)

# capture images continuously for 3 seconds (the following are the defaults)
sg.run(save=True, show=False, duration=3)

# capture images continuously (duration=0). You must press `ctrl+c` on the console to quit.
# sg.run(save=True, show=False, duration=0)



