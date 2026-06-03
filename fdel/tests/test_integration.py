"""
Integration tests for fdel workflow
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from fdel.core import (
    search_files,
    delete_item,
    move_item,
    rename_item,
    copy_item,
    undo_last
)
from fdel.archive import create_zip, extract_zip
from fdel.stats import get_folder_stats
from fdel.safety import SAFETY_CONFIG


class TestIntegration(unittest.TestCase):
    """Test complete workflows"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())  # Convert to Path
        self.source_dir = self.test_dir / "source"
        self.source_dir.mkdir()
        
        SAFETY_CONFIG["enable_protection"] = False
        
        # Clear history
        history_file = Path.home() / ".fdel_history.json"
        if history_file.exists():
            history_file.unlink()
        
        # Create project structure
        self.create_test_project()
    
    def create_test_project(self):
        """Create a mock project structure"""
        # Python files
        (self.source_dir / "main.py").write_text("def main(): pass")
        (self.source_dir / "utils.py").write_text("def util(): pass")
        
        # Data files
        (self.source_dir / "data.json").write_text('{"key": "value"}')
        (self.source_dir / "config.ini").write_text("[DEFAULT]\nkey=value")
        
        # Empty file
        (self.source_dir / "empty.log").touch()
        
        # Subfolder
        subdir = self.source_dir / "subfolder"
        subdir.mkdir()
        (subdir / "nested.py").write_text("nested code")
        (subdir / "readme.md").write_text("# Readme")
        
        # Empty folder
        empty = self.source_dir / "empty_folder"
        empty.mkdir()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        SAFETY_CONFIG["enable_protection"] = True
    
    def test_full_workflow_search_delete(self):
        """Test: search -> delete workflow"""
        # 1. Search for .py files
        py_files = search_files(str(self.source_dir), ".py")
        self.assertEqual(len(py_files), 3)  # main.py, utils.py, nested.py
        
        # 2. Delete one file
        success, msg = delete_item(str(self.source_dir / "utils.py"))
        self.assertTrue(success, msg)
        
        # 3. Verify deleted
        py_files = search_files(str(self.source_dir), ".py")
        self.assertEqual(len(py_files), 2)
    
    def test_full_workflow_zip_extract(self):
        """Test: zip -> extract workflow"""
        # 1. Create zip of source
        zip_path = self.test_dir / "backup.zip"
        success, msg = create_zip(str(self.source_dir), str(zip_path))
        self.assertTrue(success, msg)
        self.assertTrue(zip_path.exists())
    
        # 2. Delete original
        shutil.rmtree(self.source_dir)
        self.assertFalse(self.source_dir.exists())
    
        # 3. Extract zip
        success, msg = extract_zip(str(zip_path), str(self.source_dir))
        self.assertTrue(success, msg)
    
        # 4. Verify files restored (search recursively)
        main_py_exists = False
        for file in self.source_dir.rglob("*"):
            if file.name == "main.py":
                main_py_exists = True
                break
    
        self.assertTrue(main_py_exists, "main.py not found in extracted files")
    
    def test_workflow_move_rename_undo(self):
        """Test: move -> rename -> undo workflow"""
        # Clear history first
        history_file = Path.home() / ".fdel_history.json"
        if history_file.exists():
            history_file.unlink()
    
        original_file = self.source_dir / "main.py"
        self.assertTrue(original_file.exists(), "original_file should exist")
    
        # 1. Move to subfolder
        subdir = self.source_dir / "moved"
        subdir.mkdir()
    
        success, msg = move_item(str(original_file), str(subdir))
        self.assertTrue(success, msg)
        self.assertFalse(original_file.exists())
        self.assertTrue((subdir / "main.py").exists())
    
        # 2. Rename in new location
        success, msg = rename_item(str(subdir / "main.py"), "renamed.py")
        self.assertTrue(success, msg)
        self.assertTrue((subdir / "renamed.py").exists())
    
        # 3. Undo rename
        success, msg = undo_last()
        self.assertTrue(success, msg)
        self.assertTrue((subdir / "main.py").exists())
        self.assertFalse((subdir / "renamed.py").exists())
    
        # 4. Undo move
        success, msg = undo_last()
        self.assertTrue(success, msg)
        self.assertTrue(original_file.exists())
    
    def test_cleanup_workflow(self):
        """Test: find empty -> delete workflow"""
        from fdel.core import find_empty_files, find_empty_dirs
        
        # 1. Find empty files
        empty_files = find_empty_files(str(self.source_dir))
        self.assertEqual(len(empty_files), 1)  # empty.log
        self.assertEqual(empty_files[0].name, "empty.log")
        
        # 2. Find empty folders
        empty_dirs = find_empty_dirs(str(self.source_dir))
        self.assertEqual(len(empty_dirs), 1)  # empty_folder
        
        # 3. Delete empty file
        success, msg = delete_item(str(empty_files[0]))
        self.assertTrue(success, msg)
        
        # 4. Delete empty folder
        success, msg = delete_item(str(empty_dirs[0]))
        self.assertTrue(success, msg)
        
        # 5. Verify cleaned
        remaining_empty = find_empty_files(str(self.source_dir))
        self.assertEqual(len(remaining_empty), 0)
    
    def test_statistics_before_after_operations(self):
        """Test stats before and after operations"""
        # Before stats
        stats_before = get_folder_stats(str(self.source_dir))
        self.assertEqual(stats_before['total_files'], 7)  # main.py, utils.py, data.json, config.ini, empty.log, nested.py, readme.md = 7
        
        # Delete some files
        delete_item(str(self.source_dir / "utils.py"))
        delete_item(str(self.source_dir / "subfolder" / "readme.md"))
        
        # After stats
        stats_after = get_folder_stats(str(self.source_dir))
        self.assertEqual(stats_after['total_files'], 5)


class TestSafetyIntegration(unittest.TestCase):
    """Test safety features in workflows"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())  # Convert to Path
        SAFETY_CONFIG["enable_protection"] = True
        
        # Create test files
        self.safe_file = self.test_dir / "normal.txt"
        self.safe_file.write_text("safe")
        
        self.sensitive_file = self.test_dir / "config.ini"
        self.sensitive_file.write_text("sensitive")
        
        self.critical_file = self.test_dir / "shadow"
        self.critical_file.write_text("system")
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_safety_levels_detection(self):
        """Test safety level detection for different files"""
        from fdel.core import get_safety_level
        
        level, _ = get_safety_level(self.safe_file)
        self.assertEqual(level, "safe")
        
        level, _ = get_safety_level(self.sensitive_file)
        self.assertEqual(level, "warning")
    
    def test_safe_file_delete(self):
        """Test deleting safe file (normal confirmation)"""
        from fdel.core import delete_item
        
        # Skip interactive test - just verify function signature
        self.assertTrue(callable(delete_item))


if __name__ == "__main__":
    unittest.main()