from .core import (
    cari_file, 
    cari_folder_kosong, 
    cari_file_kosong, 
    hapus_file
)
from .explorer import explore_folder, cari_dan_hapus_dari_explore
from .cli import main

__version__ = "2.0.0"
__all__ = [
    'cari_file',
    'cari_folder_kosong', 
    'cari_file_kosong',
    'hapus_file',
    'explore_folder',
    'cari_dan_hapus_dari_explore',
    'main'
]
