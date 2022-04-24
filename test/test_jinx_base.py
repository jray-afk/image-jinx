# not needed in installed version
# run from root project folder
import sys
sys.path.append('src')
# needed in installed version
import jinx


## this should raise exception -- folder 'bad' shouldn't exist
# jinx.Jinx.set_out_folder('bad')

jinx.Jinx.set_out_folder('test/out')

print(jinx.Jinx.out_folder)
print(jinx.Jinx.get_out_folder())


