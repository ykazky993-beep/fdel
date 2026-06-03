# test_zip_extract.py
from pathlib import Path
from fdel.archive import create_zip, extract_zip
import tempfile
import shutil

with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)
    
    # Create source
    src = tmp / "source"
    src.mkdir()
    (src / "test.txt").write_text("hello")
    
    # Create zip
    zip_path = tmp / "test.zip"
    success, msg = create_zip(str(src), str(zip_path))
    print(f"Create zip: {msg}")
    
    # Delete source
    shutil.rmtree(src)
    
    # Extract
    success, msg = extract_zip(str(zip_path), str(src))
    print(f"Extract: {msg}")
    
    # Check
    if (src / "test.txt").exists():
        print("✅ SUCCESS: File extracted correctly")
    else:
        print("❌ FAIL: File not found")
        print(f"Contents of {src}: {list(src.rglob('*')) if src.exists() else 'folder not exists'}")