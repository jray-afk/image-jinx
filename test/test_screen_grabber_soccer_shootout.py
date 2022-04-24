# not needed in installed version
# run from root project folder
import sys

sys.path.append('src')
# needed in installed version
import jinx

# jinx options if desired
jinx.Jinx.set_out_folder('test/out')
# print(jinx.Jinx.get_out_folder())

# from this video:
# https://www.youtube.com/watch?v=8F9jXYOH2c0

# debug finding bounding box
# while True:
#     jinx.utils.show_mouse_cursor_position()

# capture images
sg = jinx.ScreenGrabber(
    out_path='test_screen_grabber_soccer_shootout/test_screen_grabber_soccer_shootout.png',
    bounding_box={'top': 277, 'left': 87, 'width': 1159-87, 'height': 800-277}
)

# capture one image to debug bounding box
# sg.capture(save=True, show=False)

# wait a couple seconds before recording to get situated
jinx.utils.countdown()

# capture images continuously for 3 seconds (the following are the defaults)
sg.run(save=True, show=False, duration=3)


