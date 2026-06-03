"""
Explorer mode - Tree view and search functionality
"""

from pathlib import Path
from typing import List, Dict, Any
from .core import get_safety_level

def explore_folder(path: str) -> Dict[str, Any]:
    """Display folder contents like tree view"""
    start = Path(path).expanduser()
    
    if not start.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    
    print(f"\n📁 {start}\n")
    print("=" * 60)
    
    folders = []
    files = []
    empty_folders = []
    empty_files = []
    
    # Collect all items
    for item in sorted(start.iterdir()):
        if item.is_dir():
            folders.append(item)
            try:
                if not any(item.iterdir()):
                    empty_folders.append(item)
            except PermissionError:
                pass
        else:
            files.append(item)
            if item.stat().st_size == 0:
                empty_files.append(item)
    
    # Display folders
    for folder in folders:
        safety_level, reason = get_safety_level(folder)
        
        if safety_level == "critical":
            icon = "🔴"
        elif safety_level == "warning":
            icon = "🟡"
        else:
            icon = "📂"
        
        empty_flag = " [EMPTY]" if folder in empty_folders else ""
        warning_flag = f" [{safety_level.upper()}]" if safety_level != "safe" else ""
        
        print(f"{icon} {folder.name}/{empty_flag}{warning_flag}")
        
        # Show first 3 items inside folder
        try:
            items = sorted(folder.iterdir())
            for i, sub in enumerate(items[:3]):
                if sub.is_file():
                    size = sub.stat().st_size
                    size_str = f"{size} B" if size < 1024 else f"{size/1024:.1f} KB"
                    print(f"  ├── {sub.name} ({size_str})")
                else:
                    print(f"  ├── {sub.name}/")
            if len(items) > 3:
                print(f"  └── ... and {len(items) - 3} more")
        except PermissionError:
            print(f"  └── [permission denied]")
    
    # Display files
    for file in files:
        safety_level, reason = get_safety_level(file)
        
        if safety_level == "critical":
            icon = "🔴"
        elif safety_level == "warning":
            icon = "🟡"
        else:
            icon = "📄"
        
        size = file.stat().st_size
        if size == 0:
            size_str = "0 B [EMPTY]"
        elif size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024*1024):.1f} MB"
        
        warning_flag = f" [{safety_level.upper()}]" if safety_level != "safe" else ""
        print(f"{icon} {file.name} ({size_str}){warning_flag}")
        if safety_level != "safe":
            print(f"     ⚠️  {reason}")
    
    print("=" * 60)
    print(f"   Total: {len(folders)} folder(s), {len(files)} file(s)")
    print(f"   🟢 Safe: {len([f for f in folders+files if get_safety_level(f)[0] == 'safe'])}")
    print(f"   🟡 Warning: {len([f for f in folders+files if get_safety_level(f)[0] == 'warning'])}")
    print(f"   🔴 Critical: {len([f for f in folders+files if get_safety_level(f)[0] == 'critical'])}")
    print(f"   📂 Empty folders: {len(empty_folders)}")
    print(f"   📄 Empty files: {len(empty_files)}")
    
    return {
        "path": start,
        "folders": folders,
        "files": files,
        "empty_folders": empty_folders,
        "empty_files": empty_files
    }

def search_and_action(project_path: str, keyword: str, dry_run: bool = False) -> List[Path]:
    """Search items by keyword and return list for action"""
    start = Path(project_path).expanduser()
    
    if not start.exists():
        return []
    
    results = []
    
    # Search in all subfolders
    for item in start.rglob("*"):
        if keyword.lower() in item.name.lower():
            results.append(item)
    
    if not results:
        print(f"No items found with keyword '{keyword}'")
        return []
    
    print(f"\n🔍 Found {len(results)} item(s) with keyword '{keyword}':\n")
    for i, item in enumerate(results, 1):
        safety_level, reason = get_safety_level(item)
        
        if safety_level == "critical":
            indicator = "🔴"
        elif safety_level == "warning":
            indicator = "🟡"
        else:
            indicator = "🟢"
        
        item_type = "📂" if item.is_dir() else "📄"
        if item.is_file():
            size = item.stat().st_size
            size_str = f"({size} B)" if size < 1024 else f"({size/1024:.1f} KB)"
            print(f"  {i}. {indicator} {item_type} {item.name} {size_str}")
        else:
            print(f"  {i}. {indicator} {item_type} {item.name}/")
        print(f"     📍 {item.parent}")
        if safety_level != "safe":
            print(f"     ⚠️  {reason}")
    
    return results