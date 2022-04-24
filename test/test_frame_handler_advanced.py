# not needed in installed version
# run from root project folder
import sys
sys.path.append('src')
# needed in installed version
import jinx

jinx.Jinx.set_out_folder('test/out')

fh = jinx.FrameHandler(
    out_path='test/out/test_frame_handler/test_cleave',
    check_existing=True
)


# call some commands below to see what happens to the file names in the out_path folder

# fh.rename_all_as_tmp()
# fh.rename_all_without_tmp()
# fh.reverse_frames()
# fh.duplicate_frames()
# fh.duplicate_frames(reverse=True)


# manually delete a frame in out_path and see what happens when calling this
# fh.recalc_indices()


def make_gif(gif_name):
    gm = jinx.GifMaker(
        images_folder='test/out/test_frame_handler',
        out_path=gif_name,
        ms_between_frames=30
    )
    gm.draw()


# make a base .gif from out folder files without messing with the FrameHandler yet to see what happens
make_gif('test_frame_handler_advanced-0-base.gif')
print("First .gif complete")

# reverse the frames and make a new gif
fh.reverse_frames()
make_gif('test_frame_handler_advanced-1-reversed.gif')
print("Second .gif complete")

# reverse the frames again back to their original state, then call duplicate with reverse=True in order to have
# the play forward then backward effect
fh.reverse_frames()
fh.duplicate_frames(reverse=True)
make_gif('test_frame_handler_advanced-2-reversed_duplicates.gif')
print("Third .gif complete")


