# not needed in installed version
# run from root project folder
import sys
sys.path.append('src')
# needed in installed version
import jinx


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

