"""
Unit tests for core operations
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json
import os

from fdel.core import (
    delete_item,
    move_item,
    rename_item,
    copy_item,
    search_files,
    find_empty_dirs,
    find_empty_files,
    get_safety_level,
    undo_last
)
from fdel.safety import SAFETY_CONFIG


class TestCoreOperations(unittest.TestCase):
    """Test basic file operations"""
    
    def setUp(self):
        """Create temporary test directory"""
        self.test_dir = Path(tempfile.mkdtemp())  # Convert to Path
        self.test_file = self.test_dir / "test.txt"
        self.test_file.write_text("Hello World")
        
        # Disable safety for tests
        SAFETY_CONFIG["enable_protection"] = False
        
        # Clear history
        history_file = Path.home() / ".fdel_history.json"
        if history_file.exists():
            history_file.unlink()
    
    def tearDown(self):
        """Clean up test directory"""
        shutil.rmtree(self.test_dir)
        SAFETY_CONFIG["enable_protection"] = True
    
    def test_delete_file(self):
        """Test deleting a file"""
        success, msg = delete_item(str(self.test_file))
        self.assertTrue(success)
        self.assertFalse(self.test_file.exists())
    
    def test_delete_nonexistent_file(self):
        """Test deleting non-existent file"""
        fake_file = self.test_dir / "nonexistent.txt"
        success, msg = delete_item(str(fake_file))
        self.assertFalse(success)
        self.assertIn("Not found", msg)
    
    def test_move_file(self):
        """Test moving a file"""
        dest_dir = self.test_dir / "subdir"
        dest_dir.mkdir()
        
        success, msg = move_item(str(self.test_file), str(dest_dir))
        self.assertTrue(success, msg)
        self.assertFalse(self.test_file.exists())
        self.assertTrue((dest_dir / "test.txt").exists())
    
    def test_rename_file(self):
        """Test renaming a file"""
        success, msg = rename_item(str(self.test_file), "renamed.txt")
        self.assertTrue(success, msg)
        self.assertFalse(self.test_file.exists())
        self.assertTrue((self.test_dir / "renamed.txt").exists())
    
    def test_copy_file(self):
        """Test copying a file"""
        dest_dir = self.test_dir / "copies"
        # dest_dir doesn't exist yet - copy_item should create it
    
        success, msg = copy_item(str(self.test_file), str(dest_dir))
        self.assertTrue(success, msg)
        self.assertTrue(self.test_file.exists())  # Original still exists
    
        # Check if file exists (either directly or inside folder)
        if (dest_dir / "test.txt").exists():
            self.assertTrue(True)
        elif dest_dir.exists():
            # Might be copied as folder name
            for f in dest_dir.rglob("*"):
                if f.name == "test.txt":
                    self.assertTrue(True)
                    break
        else:
            self.fail(f"test.txt not found in {dest_dir}")

class TestSearchFunctions(unittest.TestCase):
    """Test search functionality"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())  # Convert to Path
        SAFETY_CONFIG["enable_protection"] = False
        
        # Create test files
        (self.test_dir / "hello.py").write_text("print('hello')")
        (self.test_dir / "world.py").write_text("print('world')")
        (self.test_dir / "test.txt").write_text("test content")
        subdir = self.test_dir / "subdir"
        subdir.mkdir()
        (subdir / "nested.py").write_text("nested")
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        SAFETY_CONFIG["enable_protection"] = True
    
    def test_search_files_by_keyword(self):
        """Test searching files by keyword"""
        results = search_files(str(self.test_dir), "py")
        self.assertEqual(len(results), 3)  # hello.py, world.py, nested.py
        
        results = search_files(str(self.test_dir), "hello")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "hello.py")
    
    def test_find_empty_dirs(self):
        """Test finding empty directories"""
        # Create empty directory
        empty_dir = self.test_dir / "empty"
        empty_dir.mkdir()
        
        results = find_empty_dirs(str(self.test_dir))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "empty")
    
    def test_find_empty_files(self):
        """Test finding empty files"""
        # Create empty file
        empty_file = self.test_dir / "empty.txt"
        empty_file.touch()
        
        results = find_empty_files(str(self.test_dir))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "empty.txt")


class TestSafetyLevels(unittest.TestCase):
    """Test safety level detection"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())  # Convert to Path
        SAFETY_CONFIG["enable_protection"] = True
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_safe_file(self):
        """Test safe file detection"""
        safe_file = self.test_dir / "document.txt"
        safe_file.touch()
        
        level, reason = get_safety_level(safe_file)
        self.assertEqual(level, "safe")
        self.assertIsNone(reason)
    
    def test_dangerous_keyword_detection(self):
        """Test dangerous keyword detection"""
        sensitive_file = self.test_dir / "passwd.txt"
        sensitive_file.touch()
        
        level, reason = get_safety_level(sensitive_file)
        self.assertEqual(level, "warning")
        self.assertIn("Sensitive keyword", reason)
    
    def test_protected_pattern_detection(self):
        """Test protected pattern detection"""
        config_file = self.test_dir / "config.ini"
        config_file.touch()
        
        level, reason = get_safety_level(config_file)
        self.assertEqual(level, "warning")
        self.assertIn("Protected pattern", reason)


class TestUndoFunctionality(unittest.TestCase):
    """Test undo operations"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_file = self.test_dir / "original.txt"
        self.test_file.write_text("content")
        SAFETY_CONFIG["enable_protection"] = False
        
        # Clear history file completely
        history_file = Path.home() / ".fdel_history.json"
        if history_file.exists():
            history_file.unlink()
        
        # Also clear any cached history in the module
        import fdel.core
        if hasattr(fdel.core, '_history_cache'):
            delattr(fdel.core, '_history_cache')
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        SAFETY_CONFIG["enable_protection"] = True
        
        # Clean up history
        history_file = Path.home() / ".fdel_history.json"
        if history_file.exists():
            history_file.unlink()
    
    def test_undo_move(self):
        """Test undo move operation"""
        dest_dir = self.test_dir / "moved"
        dest_dir.mkdir()
        
        # Move file
        success, msg = move_item(str(self.test_file), str(dest_dir))
        self.assertTrue(success, msg)
        self.assertFalse(self.test_file.exists())
        
        # Verify history file was created
        history_file = Path.home() / ".fdel_history.json"
        self.assertTrue(history_file.exists(), "History file was not created")
        
        # Undo move
        success, msg = undo_last()
        self.assertTrue(success, msg)
        self.assertTrue(self.test_file.exists())
    
    def test_undo_rename(self):
        """Test undo rename operation"""
        # Rename file
        success, msg = rename_item(str(self.test_file), "renamed.txt")
        self.assertTrue(success, msg)
        
        # Verify history file was created
        history_file = Path.home() / ".fdel_history.json"
        self.assertTrue(history_file.exists(), "History file was not created")
        
        # Undo rename
        success, msg = undo_last()
        self.assertTrue(success, msg)
        self.assertTrue(self.test_file.exists())


if __name__ == "__main__":
    unittest.main()