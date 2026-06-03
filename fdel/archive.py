"""
Archive operations - zip and unzip files/folders
"""

import zipfile
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

from .core import get_safety_level, confirm_operation

def create_zip(source_path: str, output_path: Optional[str] = None, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Create a zip archive from a file or folder
    
    Examples:
        create_zip("~/Documents/file.txt")  # Creates file.txt.zip
        create_zip("~/Documents", "~/backup/docs.zip")  # Specific output
    """
    src = Path(source_path).expanduser()
    
    if not src.exists():
        return False, f"Not found: {src.name}"
    
    # Safety check
    safety_level, reason = get_safety_level(src)
    if safety_level == "critical":
        return False, f"Cannot zip critical system path: {reason}"
    
    # Determine output path
    if output_path:
        dst = Path(output_path).expanduser()
    else:
        dst = src.parent / f"{src.name}.zip"
    
    # Handle naming conflicts
    counter = 1
    original_dst = dst
    while dst.exists():
        if output_path is None:
            dst = src.parent / f"{src.name}_{counter}.zip"
        else:
            stem = original_dst.stem
            dst = original_dst.parent / f"{stem}_{counter}{original_dst.suffix}"
        counter += 1
    
    if dry_run:
        return True, f"[DRY RUN] Would create: {dst.name} from {src.name}"
    
    try:
        with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if src.is_file():
                # For a single file, just add it
                zipf.write(src, src.name)
            else:
                # For a folder: iterate through all files and add them
                # with arcname relative to the source folder (not its parent)
                for file in src.rglob("*"):
                    if file.is_file():
                        # This makes the zip contents start directly with file names
                        # instead of including the source folder name
                        arcname = file.relative_to(src)
                        zipf.write(file, arcname)
        
        return True, f"✅ Created: {dst.name} ({dst.stat().st_size / 1024:.1f} KB)"
    except Exception as e:
        return False, f"❌ Failed to create zip: {e}"


def extract_zip(zip_path: str, output_dir: Optional[str] = None, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Extract a zip archive
    
    Examples:
        extract_zip("~/Downloads/archive.zip")  # Extracts to archive/ folder
        extract_zip("~/Downloads/archive.zip", "~/extracted")  # Specific output
    """
    src = Path(zip_path).expanduser()
    
    if not src.exists():
        return False, f"Not found: {src.name}"
    
    if not src.suffix.lower() == '.zip':
        return False, f"Not a zip file: {src.name}"
    
    # Determine output directory
    if output_dir:
        dst = Path(output_dir).expanduser()
    else:
        dst = src.parent / src.stem
    
    # Check if output already exists
    if dst.exists():
        print(f"⚠️  Output already exists: {dst}")
        confirm = input("Overwrite? (y/n): ").strip().lower()
        if confirm != 'y':
            return False, "Extraction cancelled"
    
    if dry_run:
        return True, f"[DRY RUN] Would extract: {src.name} -> {dst}"
    
    try:
        # Create destination directory
        dst.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(src, 'r') as zipf:
            # Extract all files directly to destination
            zipf.extractall(dst)
        
        return True, f"✅ Extracted: {src.name} -> {dst}/"
    except zipfile.BadZipFile:
        return False, f"❌ Corrupt zip file: {src.name}"
    except Exception as e:
        return False, f"❌ Failed to extract: {e}"

def list_zip_contents(zip_path: str) -> List[dict]:
    """List contents of a zip file without extracting"""
    src = Path(zip_path).expanduser()
    
    if not src.exists():
        return []
    
    if not src.suffix.lower() == '.zip':
        return []
    
    try:
        with zipfile.ZipFile(src, 'r') as zipf:
            contents = []
            for info in zipf.infolist():
                contents.append({
                    'name': info.filename,
                    'size': info.file_size,
                    'compressed': info.compress_size,
                    'date': datetime(*info.date_time).isoformat()
                })
            return contents
    except Exception:
        return []