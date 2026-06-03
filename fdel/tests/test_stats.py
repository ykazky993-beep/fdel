"""
Unit tests for statistics and find functionality
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from fdel.stats import (
    get_folder_stats,
    find_by_extension,
    find_by_pattern,
    _format_size
)
from fdel.safety import SAFETY_CONFIG


class TestStatsFunctions(unittest.TestCase):
    """Test statistics gathering"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        SAFETY_CONFIG["enable_protection"] = False
        
        # Create diverse test files
        self.file_py = Path(self.test_dir) / "script.py"
        self.file_py.write_text("print('hello')")
        
        self.file_txt = Path(self.test_dir) / "readme.txt"
        self.file_txt.write_text("Documentation" * 100)
        
        self.file_json = Path(self.test_dir) / "config.json"
        self.file_json.write_text('{"key": "value"}')
        
        # Create empty file
        self.empty_file = Path(self.test_dir) / "empty.log"
        self.empty_file.touch()
        
        # Create hidden file
        self.hidden_file = Path(self.test_dir) / ".hidden"
        self.hidden_file.write_text("secret")
        
        # Create subdirectory with files
        self.subdir = Path(self.test_dir) / "subdir"
        self.subdir.mkdir()
        self.nested_file = self.subdir / "nested.py"
        self.nested_file.write_text("nested code")
        
        # Create empty subdirectory
        self.empty_dir = Path(self.test_dir) / "empty_folder"
        self.empty_dir.mkdir()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        SAFETY_CONFIG["enable_protection"] = True
    
    def test_get_folder_stats_counts(self):
        """Test basic count statistics"""
        stats = get_folder_stats(str(self.test_dir))
        
        # We have: script.py, readme.txt, config.json, empty.log, .hidden, nested.py
        self.assertEqual(stats['total_files'], 6)  # 5 + 1 nested
        self.assertEqual(stats['total_folders'], 2)  # subdir, empty_folder
        self.assertEqual(stats['empty_folders'], 1)  # empty_folder
        self.assertEqual(stats['empty_files'], 1)    # empty.log
        self.assertEqual(stats['hidden_files'], 1)   # .hidden
    
    def test_get_folder_stats_size(self):
        """Test file size statistics"""
        stats = get_folder_stats(str(self.test_dir))
        
        # Total size should be > 0
        self.assertGreater(stats['total_size_bytes'], 0)
        self.assertIsInstance(stats['total_size_human'], str)
    
    def test_get_folder_stats_extensions(self):
        """Test extension tracking"""
        stats = get_folder_stats(str(self.test_dir))
        
        self.assertIn('.py', stats['extensions'])
        self.assertIn('.txt', stats['extensions'])
        self.assertIn('.json', stats['extensions'])
        
        # Python files: script.py + nested.py = 2
        self.assertEqual(stats['extensions']['.py'], 2)
    
    def test_get_folder_stats_largest_files(self):
        """Test largest files detection"""
        # Make one file larger
        large_file = Path(self.test_dir) / "large.bin"
        large_file.write_bytes(bytes(1024 * 100))  # 100KB
        
        stats = get_folder_stats(str(self.test_dir))
        
        self.assertGreater(len(stats['largest_files']), 0)
        # Largest file should be large.bin
        self.assertIn("large.bin", stats['largest_files'][0][0])
    
    def test_find_by_extension(self):
        """Test finding files by extension"""
        results = find_by_extension(str(self.test_dir), ".py")
        
        self.assertEqual(len(results), 2)  # script.py + nested.py
        for result in results:
            self.assertEqual(result.suffix, ".py")
    
    def test_find_by_extension_without_dot(self):
        """Test extension search without leading dot"""
        results = find_by_extension(str(self.test_dir), "py")
        
        self.assertEqual(len(results), 2)
    
    def test_find_by_pattern(self):
        """Test pattern matching"""
        results = find_by_pattern(str(self.test_dir), "*.py")
        
        self.assertEqual(len(results), 2)
        
        results = find_by_pattern(str(self.test_dir), "*.txt")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "readme.txt")
    
    def test_find_by_pattern_case_sensitive(self):
        """Test case-sensitive pattern matching"""
        # Create mixed case file
        mixed_case = Path(self.test_dir) / "UPPER.TXT"
        mixed_case.write_text("UPPER")
        
        # Case insensitive (default)
        results = find_by_pattern(str(self.test_dir), "*.txt")
        self.assertIn(mixed_case, results)
        
        # Case sensitive
        results = find_by_pattern(str(self.test_dir), "*.TXT", case_sensitive=True)
        self.assertIn(mixed_case, results)
        
        results = find_by_pattern(str(self.test_dir), "*.txt", case_sensitive=True)
        self.assertNotIn(mixed_case, results)
    
    def test_format_size(self):
        """Test size formatting"""
        self.assertEqual(_format_size(500), "500.0 B")
        self.assertEqual(_format_size(1024), "1.0 KB")
        self.assertEqual(_format_size(1024 * 1024), "1.0 MB")
        self.assertEqual(_format_size(1024 * 1024 * 1024), "1.0 GB")


if __name__ == "__main__":
    unittest.main()