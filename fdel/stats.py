"""
Statistics and find functionality
"""

from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import os

from .core import get_safety_level

def get_folder_stats(path: str) -> Dict:
    """
    Get comprehensive statistics for a folder
    
    Returns:
        {
            'total_files': int,
            'total_folders': int,
            'total_size_bytes': int,
            'total_size_human': str,
            'extensions': Dict[str, int],
            'largest_files': List[Tuple],
            'oldest_files': List[Tuple],
            'newest_files': List[Tuple],
            'empty_folders': int,
            'empty_files': int,
            'hidden_files': int,
            'by_safety': {'safe': int, 'warning': int, 'critical': int}
        }
    """
    start = Path(path).expanduser()
    
    if not start.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    
    stats = {
        'total_files': 0,
        'total_folders': 0,
        'total_size_bytes': 0,
        'extensions': {},
        'largest_files': [],
        'oldest_files': [],
        'newest_files': [],
        'empty_folders': 0,
        'empty_files': 0,
        'hidden_files': 0,
        'by_safety': {'safe': 0, 'warning': 0, 'critical': 0}
    }
    
    all_files = []
    
    for item in start.rglob("*"):
        try:
            if item.is_file():
                stats['total_files'] += 1
                size = item.stat().st_size
                stats['total_size_bytes'] += size
                mtime = item.stat().st_mtime
                
                # Track by safety
                safety_level, _ = get_safety_level(item)
                stats['by_safety'][safety_level] = stats['by_safety'].get(safety_level, 0) + 1
                
                # Track empty files
                if size == 0:
                    stats['empty_files'] += 1
                
                # Track hidden files (Unix: starts with ., Windows: hidden attribute)
                if item.name.startswith('.'):
                    stats['hidden_files'] += 1
                
                # Track extensions
                ext = item.suffix.lower() if item.suffix else '(no extension)'
                stats['extensions'][ext] = stats['extensions'].get(ext, 0) + 1
                
                # Store for sorting
                all_files.append((item, size, mtime))
                
            elif item.is_dir():
                stats['total_folders'] += 1
                
                # Check empty folder
                try:
                    if not any(item.iterdir()):
                        stats['empty_folders'] += 1
                except PermissionError:
                    pass
                    
        except (PermissionError, OSError):
            continue
    
    # Sort and get largest files (top 10)
    all_files.sort(key=lambda x: x[1], reverse=True)
    stats['largest_files'] = [(str(f), size, _format_size(size)) for f, size, _ in all_files[:10]]
    
    # Sort and get oldest files (top 10)
    all_files.sort(key=lambda x: x[2])
    stats['oldest_files'] = [(str(f), size, datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')) 
                              for f, size, mtime in all_files[:10]]
    
    # Sort and get newest files (top 10)
    all_files.sort(key=lambda x: x[2], reverse=True)
    stats['newest_files'] = [(str(f), size, datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')) 
                              for f, size, mtime in all_files[:10]]
    
    # Human readable size
    stats['total_size_human'] = _format_size(stats['total_size_bytes'])
    
    return stats

def _format_size(bytes_size: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"

def print_stats(stats: Dict, path: str) -> None:
    """Pretty print statistics"""
    print(f"\n📊 STATISTICS FOR: {path}")
    print("=" * 60)
    
    # Basic counts
    print(f"\n📁 BASIC COUNTS:")
    print(f"   Total folders: {stats['total_folders']:,}")
    print(f"   Total files: {stats['total_files']:,}")
    print(f"   Total size: {stats['total_size_human']} ({stats['total_size_bytes']:,} bytes)")
    
    # Empty items
    print(f"\n🧹 EMPTY ITEMS:")
    print(f"   Empty folders: {stats['empty_folders']:,}")
    print(f"   Empty files (0 bytes): {stats['empty_files']:,}")
    print(f"   Hidden files: {stats['hidden_files']:,}")
    
    # Safety distribution
    print(f"\n🛡️  SAFETY DISTRIBUTION:")
    for level in ['safe', 'warning', 'critical']:
        count = stats['by_safety'].get(level, 0)
        if level == 'safe':
            emoji = "🟢"
        elif level == 'warning':
            emoji = "🟡"
        else:
            emoji = "🔴"
        print(f"   {emoji} {level.upper()}: {count:,} files")
    
    # Top extensions
    if stats['extensions']:
        print(f"\n📄 TOP FILE EXTENSIONS:")
        sorted_ext = sorted(stats['extensions'].items(), key=lambda x: x[1], reverse=True)[:10]
        for ext, count in sorted_ext:
            print(f"   {ext}: {count:,} files")
    
    # Largest files
    if stats['largest_files']:
        print(f"\n💾 LARGEST FILES (top 10):")
        for i, (filepath, size, size_human) in enumerate(stats['largest_files'], 1):
            name = Path(filepath).name
            print(f"   {i}. {name} ({size_human})")
    
    # Oldest files
    if stats['oldest_files']:
        print(f"\n📅 OLDEST FILES (top 10):")
        for i, (filepath, size, date) in enumerate(stats['oldest_files'], 1):
            name = Path(filepath).name
            print(f"   {i}. {name} ({date})")
    
    # Newest files
    if stats['newest_files']:
        print(f"\n🕒 NEWEST FILES (top 10):")
        for i, (filepath, size, date) in enumerate(stats['newest_files'], 1):
            name = Path(filepath).name
            print(f"   {i}. {name} ({date})")
    
    print("\n" + "=" * 60)

def find_by_extension(path: str, extension: str, dry_run: bool = False) -> List[Path]:
    """
    Find all files with specific extension
    
    Examples:
        find_by_extension("~/Projects", ".py")
        find_by_extension("~/Downloads", ".jpg")
    """
    start = Path(path).expanduser()
    
    if not start.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    
    # Normalize extension
    if not extension.startswith('.'):
        extension = '.' + extension
    
    results = []
    
    for file in start.rglob("*"):
        if file.is_file() and file.suffix.lower() == extension.lower():
            results.append(file)
    
    return results

def find_by_pattern(path: str, pattern: str, case_sensitive: bool = False) -> List[Path]:
    """
    Find files matching pattern (wildcards supported)
    
    Examples:
        find_by_pattern("~/Downloads", "*.jpg")
        find_by_pattern("~/Projects", "test_*.py")
    """
    import fnmatch
    start = Path(path).expanduser()
    
    if not start.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    
    results = []
    
    for file in start.rglob("*"):
        if file.is_file():
            name = file.name if case_sensitive else file.name.lower()
            pattern_match = pattern if case_sensitive else pattern.lower()
            if fnmatch.fnmatch(name, pattern_match):
                results.append(file)
    
    return results