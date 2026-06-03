"""
Core file operations with safety layer
"""

from pathlib import Path
import os
import shutil
import json
from difflib import get_close_matches
from datetime import datetime
from typing import List, Tuple, Optional, Any
from fnmatch import fnmatch

from .safety import (
    SAFETY_CONFIG,
    PROTECTED_PATHS,
    PROTECTED_FOLDERS,
    PROTECTED_FILE_PATTERNS,
    DANGEROUS_KEYWORDS,
    SAFE_EXTENSIONS,
    get_user_critical_confirm,
    get_user_warning_confirm,
    is_safe_extension
)

HISTORY_FILE = Path.home() / ".fdel_history.json"

# ============ SAFETY CORE FUNCTIONS ============

def is_protected_path(path: Path) -> Tuple[bool, Optional[str]]:
    """
    Check if path is in protected system locations
    Returns: (is_protected, reason)
    """
    if not SAFETY_CONFIG["enable_protection"]:
        return False, None
    
    try:
        resolved = Path(path).expanduser().resolve()
        
        # Check against protected paths list
        for protected in PROTECTED_PATHS:
            if not protected.exists():
                continue
            try:
                if resolved == protected:
                    return True, f"System root path: {protected}"
                if resolved.is_relative_to(protected):
                    return True, f"System directory: {protected}"
            except (ValueError, OSError):
                continue
        
        # Check if path contains protected folder names
        for part in resolved.parts:
            if part.lower() in PROTECTED_FOLDERS:
                return True, f"Protected folder name: '{part}'"
        
        return False, None
    except Exception:
        return False, None

def is_dangerous_file(filename: str) -> Tuple[bool, Optional[str]]:
    """
    Check if filename matches dangerous patterns
    Returns: (is_dangerous, reason)
    """
    if not SAFETY_CONFIG["enable_protection"]:
        return False, None
    
    filename_lower = filename.lower()
    
    # Check dangerous keywords
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in filename_lower:
            return True, f"Sensitive keyword: '{keyword}'"
    
    # Check patterns
    for pattern in PROTECTED_FILE_PATTERNS:
        if fnmatch(filename_lower, pattern):
            return True, f"Protected pattern: '{pattern}'"
    
    return False, None

def get_safety_level(item_path: Path) -> Tuple[str, Optional[str]]:
    """
    Get safety level: 'critical', 'warning', or 'safe'
    Returns: (level, reason)
    """
    path = Path(item_path).expanduser()
    
    # Check protected system paths
    is_protected, reason = is_protected_path(path)
    if is_protected:
        return "critical", reason
    
    # Check dangerous file patterns
    is_dangerous, reason = is_dangerous_file(path.name)
    if is_dangerous:
        return "warning", reason
    
    # Check if it's user home directory
    home = Path.home()
    if SAFETY_CONFIG["warn_for_home_directory"]:
        try:
            if path == home:
                return "warning", "Your entire home directory"
            if path.is_relative_to(home):
                pass  # Inside home is safe
        except ValueError:
            pass
    
    return "safe", None

def confirm_operation(item_path: Path, operation: str) -> bool:
    """
    Get confirmation based on safety level
    Returns: True if confirmed, False if cancelled
    """
    safety_level, reason = get_safety_level(item_path)
    
    if safety_level == "critical":
        if not SAFETY_CONFIG["require_typing_for_critical"]:
            return False
        print(f"\n🔴 CRITICAL: {operation.upper()} on {item_path}")
        print(f"   Reason: {reason}")
        return get_user_critical_confirm()
    
    elif safety_level == "warning":
        print(f"\n🟡 WARNING: {operation.upper()} on {item_path}")
        print(f"   Reason: {reason}")
        return get_user_warning_confirm(reason)
    
    else:  # safe
        return True

# ============ HISTORY FUNCTIONS ============

import json
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional, List, Any

HISTORY_FILE = Path.home() / ".fdel_history.json"

def _save_history(src: Path, dst: Optional[Path], action: str) -> None:
    """Save action history for undo"""
    try:
        history = []
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
        
        history.append({
            "src": str(src),
            "dst": str(dst) if dst else None,
            "action": action,
            "time": datetime.now().isoformat()
        })
        
        # Keep last 50 actions
        if len(history) > 50:
            history = history[-50:]
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        
        print(f"DEBUG: Saved to history - action: {action}, src: {src}")  # Debug line - remove later
    except Exception as e:
        print(f"DEBUG: Failed to save history: {e}")  # Debug line - remove later


def undo_last(dry_run: bool = False) -> Tuple[bool, str]:
    """Undo last action (delete, move, rename, copy)"""
    if not HISTORY_FILE.exists():
        return False, "No history found"
    
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    except (json.JSONDecodeError, IOError):
        return False, "History file corrupted"
    
    if not history:
        return False, "History is empty"
    
    last = history[-1]
    action = last["action"]
    src = Path(last["src"])
    dst = Path(last["dst"]) if last["dst"] else None
    
    # Safety check for undo
    if dst and dst.exists():
        safety_level, reason = get_safety_level(dst)
        if safety_level == "critical":
            return False, f"Cannot undo in system directory: {reason}"
    
    if action == "delete":
        return False, "Cannot undo deletion (permanent)"
    
    elif action == "move" and dst and dst.exists():
        if dry_run:
            return True, f"[DRY RUN] Would undo move: {dst} -> {src}"
        shutil.move(str(dst), str(src))
        history.pop()
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        return True, f"↩️ Undo move: {dst.name} -> {src.parent}"
    
    elif action == "rename" and dst and dst.exists():
        if dry_run:
            return True, f"[DRY RUN] Would undo rename: {dst} -> {src}"
        shutil.move(str(dst), str(src))
        history.pop()
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        return True, f"↩️ Undo rename: {dst.name} -> {src.name}"
    
    elif action == "copy" and dst and dst.exists():
        if dry_run:
            return True, f"[DRY RUN] Would delete copied: {dst}"
        if dst.is_file():
            dst.unlink()
        else:
            shutil.rmtree(dst)
        history.pop()
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        return True, f"↩️ Removed copied: {dst.name}"
    
    return False, f"Cannot undo {action}"

# ============ CORE OPERATIONS ============

def search_files(start_path: str, keyword: str, max_results: int = 50) -> List[Path]:
    """Search files with name matching keyword (fuzzy)"""
    results = []
    start = Path(start_path).expanduser()
    
    if not start.exists():
        raise FileNotFoundError(f"Path not found: {start_path}")
    
    # Safety check on search path
    safety_level, reason = get_safety_level(start)
    if safety_level == "critical":
        raise PermissionError(f"Cannot search in system directory: {reason}")
    
    for file in start.rglob("*"):
        if file.is_file() and keyword.lower() in file.name.lower():
            results.append(file)
            if len(results) >= max_results:
                break
    
    # Sort by closest match
    if results:
        names = [f.name for f in results]
        closest = get_close_matches(keyword, names, n=len(results), cutoff=0.3)
        results.sort(key=lambda x: closest.index(x.name) if x.name in closest else 999)
    
    return results

def find_empty_dirs(start_path: str) -> List[Path]:
    """Find all empty directories"""
    start = Path(start_path).expanduser()
    
    if not start.exists():
        raise FileNotFoundError(f"Path not found: {start_path}")
    
    # Safety check
    safety_level, reason = get_safety_level(start)
    if safety_level == "critical":
        raise PermissionError(f"Cannot scan system directory: {reason}")
    
    empty = []
    
    for folder in start.rglob("*"):
        if folder.is_dir():
            try:
                contents = list(folder.iterdir())
                if not contents:
                    empty.append(folder)
            except PermissionError:
                continue
    
    return empty

def find_empty_files(start_path: str) -> List[Path]:
    """Find all zero-byte files"""
    start = Path(start_path).expanduser()
    
    if not start.exists():
        raise FileNotFoundError(f"Path not found: {start_path}")
    
    # Safety check
    safety_level, reason = get_safety_level(start)
    if safety_level == "critical":
        raise PermissionError(f"Cannot scan system directory: {reason}")
    
    empty = []
    
    for file in start.rglob("*"):
        if file.is_file():
            try:
                if file.stat().st_size == 0:
                    empty.append(file)
            except (PermissionError, OSError):
                continue
    
    return empty

def delete_item(item_path: str, dry_run: bool = False) -> Tuple[bool, str]:
    """Delete file or folder with safety checks"""
    path = Path(item_path).expanduser()
    
    if not path.exists():
        return False, f"Not found: {path.name}"
    
    # Safety check
    if not confirm_operation(path, "delete"):
        return False, f"Cancelled: {path.name}"
    
    # Batch protection: don't allow deleting protected in batch
    safety_level, _ = get_safety_level(path)
    if safety_level == "critical" and SAFETY_CONFIG["batch_ops_skip_critical"]:
        return False, f"Cannot delete critical system file in batch: {path.name}"
    
    if dry_run:
        return True, f"[DRY RUN] Would delete: {path.name}"
    
    try:
        if path.is_file():
            os.remove(path)
            _save_history(path, None, "delete")
            return True, f"Deleted: {path.name}"
        elif path.is_dir():
            shutil.rmtree(path)
            _save_history(path, None, "delete")
            return True, f"Deleted folder: {path.name}"
    except PermissionError:
        return False, f"Permission denied: {path.name}"
    except Exception as e:
        return False, f"Failed to delete {path.name}: {e}"

def move_item(source: str, destination: str, dry_run: bool = False) -> Tuple[bool, str]:
    """Move file/folder to new location with safety checks"""
    src = Path(source).expanduser()
    dst = Path(destination).expanduser()
    
    if not src.exists():
        return False, f"Not found: {src.name}"
    
    # Safety check on source
    safety_level, reason = get_safety_level(src)
    if safety_level == "critical":
        return False, f"Cannot move critical system path: {reason}"
    
    if safety_level == "warning":
        if not get_user_warning_confirm(reason):
            return False, f"Cancelled: {src.name}"
    
    # If destination is a folder, move inside it
    if dst.is_dir():
        dst = dst / src.name
    
    # Create parent folder if needed
    dst.parent.mkdir(parents=True, exist_ok=True)
    
    if dry_run:
        return True, f"[DRY RUN] Would move: {src} -> {dst}"
    
    try:
        shutil.move(str(src), str(dst))
        # IMPORTANT: Save to history AFTER successful move
        _save_history(src, dst, "move")
        return True, f"✅ Moved: {src.name} -> {dst.parent}/{dst.name}"
    except Exception as e:
        return False, f"❌ Failed to move: {e}"


def rename_item(item_path: str, new_name: str, dry_run: bool = False) -> Tuple[bool, str]:
    """Rename file or folder with safety checks"""
    src = Path(item_path).expanduser()
    
    if not src.exists():
        return False, f"Not found: {src.name}"
    
    # Safety check
    safety_level, reason = get_safety_level(src)
    if safety_level == "critical":
        return False, f"Cannot rename critical system path: {reason}"
    
    if safety_level == "warning":
        if not get_user_warning_confirm(reason):
            return False, f"Cancelled: {src.name}"
    
    dst = src.parent / new_name
    
    if dry_run:
        return True, f"[DRY RUN] Would rename: {src.name} -> {new_name}"
    
    try:
        shutil.move(str(src), str(dst))
        # IMPORTANT: Save to history AFTER successful rename
        _save_history(src, dst, "rename")
        return True, f"✅ Renamed: {src.name} -> {new_name}"
    except Exception as e:
        return False, f"❌ Failed to rename: {e}"

def copy_item(source: str, destination: str, dry_run: bool = False) -> Tuple[bool, str]:
    """Copy file/folder to new location with safety checks"""
    src = Path(source).expanduser()
    dst = Path(destination).expanduser()
    
    if not src.exists():
        return False, f"Not found: {src.name}"
    
    # Safety check on source
    safety_level, reason = get_safety_level(src)
    if safety_level == "critical":
        return False, f"Cannot copy critical system path: {reason}"
    
    # If destination doesn't exist, create parent
    if dst.suffix and '.' in dst.name:  # Has extension, treat as file
        dst.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Treat as folder
        dst = dst / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
    
    if dry_run:
        return True, f"[DRY RUN] Would copy: {src} -> {dst}"
    
    try:
        if src.is_file():
            shutil.copy2(str(src), str(dst))
        else:
            shutil.copytree(str(src), str(dst))
        _save_history(src, dst, "copy")
        return True, f"✅ Copied: {src.name} -> {dst}"
    except Exception as e:
        return False, f"❌ Failed to copy: {e}"