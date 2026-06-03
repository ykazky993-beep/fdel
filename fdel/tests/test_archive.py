"""
Unit tests for zip/unzip operations
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from fdel.archive import create_zip, extract_zip, list_zip_contents
from fdel.safety import SAFETY_CONFIG


class TestArchiveOperations(unittest.TestCase):
    """Test zip and unzip functionality"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())  # Convert to Path
        SAFETY_CONFIG["enable_protection"] = False
        
        # Create test files
        self.file1 = self.test_dir / "file1.txt"
        self.file1.write_text("Content 1")
        self.file2 = self.test_dir / "file2.txt"
        self.file2.write_text("Content 2")
        
        self.subdir = self.test_dir / "subdir"
        self.subdir.mkdir()
        self.subfile = self.subdir / "nested.txt"
        self.subfile.write_text("Nested content")
        
        # Clear history
        history_file = Path.home() / ".fdel_history.json"
        if history_file.exists():
            history_file.unlink()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        SAFETY_CONFIG["enable_protection"] = True
    
    def test_create_zip_single_file(self):
        """Test creating zip from single file"""
        zip_path = self.test_dir / "output.zip"
        
        success, msg = create_zip(str(self.file1), str(zip_path))
        
        self.assertTrue(success, msg)
        self.assertTrue(zip_path.exists())
        self.assertTrue(zip_path.stat().st_size > 0)
    
    def test_create_zip_folder(self):
        """Test creating zip from folder"""
        zip_path = self.test_dir / "folder.zip"
        
        success, msg = create_zip(str(self.test_dir), str(zip_path))
        
        self.assertTrue(success, msg)
        self.assertTrue(zip_path.exists())
    
    def test_create_zip_auto_naming(self):
        """Test zip with automatic naming"""
        success, msg = create_zip(str(self.file1))
    
        self.assertTrue(success, msg)
        # Should create file1.txt.zip in same directory (not file1.zip)
        auto_zip = self.test_dir / "file1.txt.zip"
        self.assertTrue(auto_zip.exists())
    
    def test_create_zip_conflict_handling(self):
        """Test zip with name conflict"""
        zip_path = self.test_dir / "duplicate.zip"
        
        # Create first zip
        success1, msg1 = create_zip(str(self.file1), str(zip_path))
        self.assertTrue(success1, msg1)
        
        # Create second zip with same name (should auto-rename)
        success2, msg2 = create_zip(str(self.file2), str(zip_path))
        self.assertTrue(success2, msg2)
        
        # Should create duplicate_1.zip
        renamed_zip = self.test_dir / "duplicate_1.zip"
        self.assertTrue(renamed_zip.exists())
    
    def test_extract_zip(self):
        """Test extracting zip file"""
        # Create zip first
        zip_path = self.test_dir / "archive.zip"
        create_zip(str(self.test_dir), str(zip_path))
    
        # Extract to new folder
        extract_dir = self.test_dir / "extracted"
        success, msg = extract_zip(str(zip_path), str(extract_dir))
    
        self.assertTrue(success, msg)
        self.assertTrue(extract_dir.exists())
        # Check if file exists in extracted folder (may be in subfolder)
        found = False
        for file in extract_dir.rglob("*"):
            if file.name == "file1.txt":
                found = True
                break
        self.assertTrue(found, "file1.txt not found in extracted directory")
    
    def test_extract_zip_auto_naming(self):
        """Test zip extraction with automatic folder naming"""
        # Create zip
        zip_path = self.test_dir / "mydata.zip"
        create_zip(str(self.file1), str(zip_path))
        
        # Extract without specifying output
        success, msg = extract_zip(str(zip_path))
        
        self.assertTrue(success, msg)
        auto_dir = self.test_dir / "mydata"
        self.assertTrue(auto_dir.exists())
        self.assertTrue((auto_dir / "file1.txt").exists())
    
    def test_list_zip_contents(self):
        """Test listing zip contents"""
        # Create zip with multiple files
        zip_path = self.test_dir / "contents.zip"
        create_zip(str(self.test_dir), str(zip_path))
        
        contents = list_zip_contents(str(zip_path))
        
        self.assertGreater(len(contents), 0)
        # Should find our files
        filenames = [c['name'] for c in contents]
        self.assertTrue(any('file1.txt' in f for f in filenames))
    
    def test_extract_nonexistent_zip(self):
        """Test extracting non-existent zip"""
        fake_zip = self.test_dir / "fake.zip"
        
        success, msg = extract_zip(str(fake_zip))
        
        self.assertFalse(success)
        self.assertIn("Not found", msg)
    
    def test_extract_corrupt_zip(self):
        """Test extracting corrupt zip file"""
        corrupt_zip = self.test_dir / "corrupt.zip"
        corrupt_zip.write_text("This is not a zip file")
        
        success, msg = extract_zip(str(corrupt_zip))
        
        self.assertFalse(success)
        self.assertIn("Corrupt", msg)


if __name__ == "__main__":
    unittest.main()