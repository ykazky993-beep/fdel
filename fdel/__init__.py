"""
fdel - File Manager CLI Tool
Search, Delete, Move, Rename, Copy files with Safety Protection
"""

from .core import (
    search_files,
    find_empty_dirs,
    find_empty_files,
    delete_item,
    move_item,
    rename_item,
    copy_item,
    undo_last,
    get_safety_level,
    is_protected_path,
    is_dangerous_file
)

from .version import __version__
from .explorer import explore_folder, search_and_action
from .cli import main
from .safety import SAFETY_CONFIG, PROTECTED_PATHS, PROTECTED_FOLDERS
from .archive import create_zip, extract_zip, list_zip_contents
from .stats import get_folder_stats, print_stats, find_by_extension, find_by_pattern

__version__ = __version__
__author__ = "ykazky993-beep"
__license__ = "MIT"

__all__ = [
    'search_files',
    'find_empty_dirs',
    'find_empty_files',
    'delete_item',
    'move_item',
    'rename_item',
    'copy_item',
    'undo_last',
    'get_safety_level',
    'is_protected_path',
    'is_dangerous_file',
    'explore_folder',
    'search_and_action',
    'create_zip',       
    'extract_zip',      
    'list_zip_contents',
    'get_folder_stats',    
    'print_stats',         
    'find_by_extension',   
    'find_by_pattern',
    'main',
    'SAFETY_CONFIG',
    'PROTECTED_PATHS',
    'PROTECTED_FOLDERS'
]