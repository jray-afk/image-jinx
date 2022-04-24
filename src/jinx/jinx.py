import os
import pathlib
import uuid


class Jinx:
    out_folder = ''
    jinx_folder = pathlib.Path(__file__).absolute().parents[0]
    assets_folder = os.path.join(jinx_folder, 'assets')
    fonts_folder = os.path.join(assets_folder, 'fonts')
    
    @classmethod
    def get_out_folder(cls):
        return cls.out_folder
    
    @classmethod
    def set_out_folder(cls, new_out_folder):
        if not os.path.exists(new_out_folder):
            raise Exception(f"Out folder '{new_out_folder}' doesn't exist.")
        cls.out_folder = new_out_folder
        return cls.out_folder
    
    @staticmethod
    def check_rand_out_path(out_path_check, ext='gif'):
        out_path = out_path_check
        if out_path_check == '':
            out_path = f'{uuid.uuid4()}.{ext}'
        return out_path
    
    @classmethod
    def get_out_path(cls, out_path_check, ext='gif'):
        file_name = cls.check_rand_out_path(out_path_check, ext)
        return os.path.join(cls.get_out_folder(), file_name)


