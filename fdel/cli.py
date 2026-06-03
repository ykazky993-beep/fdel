#!/usr/bin/env python3
"""
fdel - File Manager CLI Tool
Command-line interface with safety features
"""

from .version import __version__
import sys
from pathlib import Path
from typing import List

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
)
from .explorer import explore_folder, search_and_action
from .safety import SAFETY_CONFIG

def display_results(items: List[Path], title: str = "Found") -> bool:
    """Display list of items with numbers and safety indicators"""
    if not items:
        print(f"❌ {title}: 0")
        return False
    
    print(f"\n📁 {title}: {len(items)}\n")
    for i, item in enumerate(items, 1):
        safety_level, reason = get_safety_level(item)
        
        if safety_level == "critical":
            indicator = "🔴 [CRITICAL]"
        elif safety_level == "warning":
            indicator = "🟡 [WARNING]"
        else:
            indicator = "🟢 [SAFE]"
        
        if item.is_file():
            size = item.stat().st_size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024*1024):.1f} MB"
            print(f"  {i}. {indicator} {item.name} ({size_str})")
        else:
            print(f"  {i}. {indicator} {item.name}/")
        print(f"     📂 {item.parent}")
        if safety_level != "safe":
            print(f"     ⚠️  {reason}")
    
    return True

def interactive_action(items: List[Path], dry_run: bool = False) -> None:
    """Interactive menu for actions on items with safety warnings"""
    if not items:
        return
    
    print("\n" + "-" * 50)
    print("Legend: [SAFE] safe  [WARNING] sensitive  [CRITICAL] system")
    print("-" * 50)
    
    while True:
        choice = input("\nSelect item (number/name, 'q' quit, 'a' select all): ").strip()
        
        if choice.lower() == 'q':
            print("cancel")
            break
        
        if choice.lower() == 'a':
            critical_items = [i for i in items if get_safety_level(i)[0] == "critical"]
            if critical_items and SAFETY_CONFIG.get("batch_ops_skip_critical", True):
                print(f"\n[WARNING] {len(critical_items)} critical system item(s) selected.")
                print("Batch operations on system files are disabled for safety.")
                print("Please select critical items individually.")
                continue
            targets = items.copy()
        else:
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    targets = [items[idx]]
                else:
                    print(f"Number {choice} not found!")
                    continue
            else:
                matches = [i for i in items if i.name.lower() == choice.lower()]
                if matches:
                    targets = matches
                else:
                    print(f"No item named '{choice}'")
                    continue
        
        print(f"\nSelected ({len(targets)}):")
        has_critical = False
        for t in targets:
            safety_level, reason = get_safety_level(t)
            if safety_level == "critical":
                has_critical = True
                print(f"  [CRITICAL] {t.name} - {reason}")
            elif safety_level == "warning":
                print(f"  [WARNING] {t.name} - {reason}")
            else:
                print(f"  [SAFE] {t.name}")
        
        if has_critical:
            print("\n[CRITICAL] System files detected!")
            print("Modifying these can break your operating system.")
            proceed = input("\nType 'YES I UNDERSTAND THE RISK' to continue: ").strip()
            if proceed != "YES I UNDERSTAND THE RISK":
                print("Operation cancelled for safety")
                continue
        
        print("\nAvailable actions:")
        print("  1. Delete")
        print("  2. Move")
        print("  3. Rename")
        print("  4. Copy")
        print("  5. Zip (compress)")
        print("  6. Cancel")
        
        action = input("\nChoose action (1-6): ").strip()
        
        if action == '1':  # Delete
            confirm = input(f"\nConfirm delete {len(targets)} item(s)? (y/n): ").strip().lower()
            if confirm == 'y':
                for target in targets:
                    success, msg = delete_item(target, dry_run)
                    print(msg)
                    if success and not dry_run:
                        items.remove(target)
        
        elif action == '2':  # Move
            dest = input("Destination folder: ").strip()
            if dest:
                for target in targets:
                    success, msg = move_item(target, dest, dry_run)
                    print(msg)
                    if success and not dry_run:
                        items.remove(target)
        
        elif action == '3':  # Rename
            for target in targets:
                new_name = input(f"New name for '{target.name}': ").strip()
                if new_name:
                    success, msg = rename_item(target, new_name, dry_run)
                    print(msg)
                    if success and not dry_run:
                        items.remove(target)
        
        elif action == '4':  # Copy
            dest = input("Destination folder: ").strip()
            if dest:
                for target in targets:
                    success, msg = copy_item(target, dest, dry_run)
                    print(msg)
        
        elif action == '5':  # Zip (NEW)
            if len(targets) > 1:
                print(f"\nZipping {len(targets)} items...")
                # Create a zip with all selected items
                from .archive import create_zip
                import tempfile
                import shutil
                
                # Create temporary folder
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmp_path = Path(tmpdir) / "archive"
                    tmp_path.mkdir()
                    
                    # Copy all items to temp folder
                    for target in targets:
                        dest = tmp_path / target.name
                        if target.is_file():
                            shutil.copy2(target, dest)
                        else:
                            shutil.copytree(target, dest)
                    
                    # Zip the temp folder
                    zip_name = input("Zip name (without .zip): ").strip()
                    if not zip_name:
                        zip_name = "archive"
                    
                    zip_path = Path.cwd() / f"{zip_name}.zip"
                    success, msg = create_zip(str(tmp_path), str(zip_path), dry_run)
                    print(msg)
            else:
                # Single item zip
                from .archive import create_zip
                target = targets[0]
                zip_name = input(f"Zip name for '{target.name}' (Enter for '{target.name}.zip'): ").strip()
                if zip_name:
                    if not zip_name.endswith('.zip'):
                        zip_name += '.zip'
                    output = target.parent / zip_name
                else:
                    output = None
                
                success, msg = create_zip(str(target), str(output) if output else None, dry_run)
                print(msg)
        
        else:
            print("Cancelled")
        
        if not items:
            print("\nAll items processed!")
            break

def mode_explore(path: str, dry_run: bool = False) -> None:
    """Explore mode: view structure and search/act on items"""
    if not path:
        print("Path cannot be empty!")
        return
    
    try:
        expanded_path = Path(path).expanduser()
        
        # Safety check before exploring
        safety_level, reason = get_safety_level(expanded_path)
        if safety_level == "critical":
            print(f"\n CRITICAL: Cannot explore system directory!")
            print(f"   Path: {expanded_path}")
            print(f"   Reason: {reason}")
            print("\n   fdel is designed for user files only.")
            print("   System directories are protected.")
            return
        
        if safety_level == "warning":
            print(f"\n⚠️  WARNING: Exploring {expanded_path}")
            print(f"   Reason: {reason}")
            confirm = input("\nContinue anyway? (y/n): ").strip().lower()
            if confirm != "y":
                print("Exploration cancelled")
                return
        
        print(f"\nExploring: {expanded_path}")
        
        if not expanded_path.exists():
            print(f"❌ Path '{expanded_path}' not found!")
            return
        
        # Display folder structure
        explore_folder(str(expanded_path))
        
        print("\n" + "=" * 60)
        
        # Ask for keyword to search
        keyword = input("\n🔎 Search keyword (or press Enter to skip): ").strip()
        
        if keyword:
            results = search_and_action(str(expanded_path), keyword, dry_run)
            if results:
                interactive_action(results, dry_run)
        else:
            print("cancel")
            
    except KeyboardInterrupt:
        print("\n\nInterrupted. cancelled by user.")
    except Exception as e:
        print(f"❌ Error: {e}")

def mode_keyword_search(path: str, keyword: str, dry_run: bool = False) -> None:
    """Search by keyword mode"""
    print(f"🔍 Searching for files with keyword '{keyword}' in {path}...")
    
    try:
        results = search_files(path, keyword)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    except PermissionError as e:
        print(f"❌ {e}")
        return
    
    if display_results(results, f"Files matching '{keyword}' found"):
        interactive_action(results, dry_run)

def mode_empty_dirs(path: str, dry_run: bool = False) -> None:
    """Find and delete empty directories"""
    print(f"🔍 Searching for empty directories in {path}...")
    
    try:
        results = find_empty_dirs(path)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    except PermissionError as e:
        print(f"❌ {e}")
        return
    
    if display_results(results, "Empty directories found"):
        interactive_action(results, dry_run)

def mode_empty_files(path: str, dry_run: bool = False) -> None:
    """Find and delete empty files (0 bytes)"""
    print(f"🔍 Searching for empty files (0 bytes) in {path}...")
    
    try:
        results = find_empty_files(path)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    except PermissionError as e:
        print(f"❌ {e}")
        return
    
    if display_results(results, "Empty files found"):
        interactive_action(results, dry_run)

def mode_undo(dry_run: bool = False) -> None:
    """Undo last action"""
    success, msg = undo_last(dry_run)
    print(msg)

def show_help() -> None:
    """Display help menu"""
    print("""

USAGE:
  fdel -v/--version                # Show version
  fdel explore <path>              # Browse folder structure & act on items
  fdel <path> <keyword>            # Search files by keyword (fuzzy match)
  fdel <path> --empty-dirs         # Find all empty directories
  fdel <path> --empty-files        # Find all empty files (0 bytes)
  fdel stats <path>                # Show comprehensive folder statistics
  fdel find <path> <pattern>       # Find files by pattern
  fdel find <path> <extension>     # Find files by extension
  fdel zip <path> [output]         # Zip a file or folder
  fdel unzip <zipfile> [output]    # Unzip a zip file
  fdel --undo                      # Undo last action (move/rename/copy)
  fdel --help                      # Show this help
  fdel -E/--explain                # Show detailed usage and safety explanation

SAFETY OPTIONS:
  --dry-run                        # Preview actions without executing
  --force                          # Disable safety prompts (not recommended)

EXAMPLES:
  fdel explore ~/Projects          # Browse your Projects folder
  fdel ~/Downloads Gantz           # Search for files named like "Gantz"
  fdel ~/Downloads --empty-dirs    # Clean up empty folders
  fdel ~/Downloads --empty-files   # Clean up zero-byte files
  fdel --undo                      # Undo your last move/rename/copy
  fdel zip ~/text.txt text.zip     # Zip a file or folder
  fdel unzip text.zip text         # Unzip a zip file
  fdel stats ~/Projects            # Show comprehensive folder statistics
  fdel find ~/Projects .py         # Find all .py files in Projects
  fdel find ~/Documents "*.txt"    # Find all .txt files in Documents
SAFETY NOTES:
  🔴 CRITICAL (system files) → Requires typing confirmation
  🟡 WARNING (sensitive)     → Requires yes/no confirmation  
  🟢 SAFE (user files)       → Normal confirmation
""")

def mode_zip_operation(path: str, action: str, dest: str = None, dry_run: bool = False) -> None:
    """Zip or unzip files/folders"""
    from .archive import create_zip, extract_zip, list_zip_contents
    
    expanded_path = Path(path).expanduser()
    
    if not expanded_path.exists():
        print(f"Not found: {path}")
        return
    
    if action == "zip":
        if expanded_path.is_file():
            safety_level, reason = get_safety_level(expanded_path)
            if safety_level == "critical":
                print(f"[CRITICAL] Cannot zip system file: {reason}")
                return
            
            if safety_level == "warning":
                print(f"[WARNING] {reason}")
                confirm = input("Zip this file anyway? (y/n): ").strip().lower()
                if confirm != 'y':
                    print("Cancelled")
                    return
        
        output = dest if dest else None
        success, msg = create_zip(str(expanded_path), output, dry_run)
        print(msg)
        
        if success and not dry_run and output:
            print(f"Zip created at: {Path(output).expanduser()}")
    
    elif action == "unzip":
        if not expanded_path.suffix.lower() == '.zip':
            print(f"Not a zip file: {expanded_path.name}")
            return
        
        # Preview contents
        print(f"\nContents of {expanded_path.name}:")
        contents = list_zip_contents(str(expanded_path))
        if contents:
            for i, item in enumerate(contents[:10], 1):
                size_kb = item['size'] / 1024
                print(f"  {i}. {item['name']} ({size_kb:.1f} KB)")
            if len(contents) > 10:
                print(f"  ... and {len(contents) - 10} more files")
        
        output_dir = dest if dest else None
        success, msg = extract_zip(str(expanded_path), output_dir, dry_run)
        print(msg)

def mode_stats(path: str) -> None:
    """Show comprehensive statistics for a folder"""
    from .stats import get_folder_stats, print_stats
    
    expanded_path = Path(path).expanduser()
    
    if not expanded_path.exists():
        print(f"Not found: {path}")
        return
    
    # Safety check
    from .core import get_safety_level
    safety_level, reason = get_safety_level(expanded_path)
    if safety_level == "critical":
        print(f"[CRITICAL] Cannot analyze system directory: {reason}")
        return
    
    if safety_level == "warning":
        print(f"[WARNING] {reason}")
        confirm = input("Analyze this folder anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled")
            return
    
    print(f"\nScanning {expanded_path}...")
    
    try:
        stats = get_folder_stats(str(expanded_path))
        print_stats(stats, str(expanded_path))
    except Exception as e:
        print(f"Error: {e}")

def mode_find(path: str, query: str, dry_run: bool = False) -> None:
    """
    Find files by extension or pattern
    
    Examples:
        fdel find ~/Projects .py
        fdel find ~/Downloads .jpg
        fdel find ~/Documents "*.txt"
    """
    from .stats import find_by_extension, find_by_pattern
    from .core import get_safety_level
    
    expanded_path = Path(path).expanduser()
    
    if not expanded_path.exists():
        print(f"Not found: {path}")
        return
    
    # Safety check
    safety_level, reason = get_safety_level(expanded_path)
    if safety_level == "critical":
        print(f"[CRITICAL] Cannot search system directory: {reason}")
        return
    
    print(f"\nSearching for '{query}' in {expanded_path}...")
    
    # Determine if it's extension or pattern
    if query.startswith('.'):
        # Extension search
        results = find_by_extension(str(expanded_path), query)
        title = f"Files with extension '{query}'"
    else:
        # Pattern search (support wildcards)
        results = find_by_pattern(str(expanded_path), query)
        title = f"Files matching pattern '{query}'"
    
    if not results:
        print(f"No files found matching '{query}'")
        return
    
    # Display results
    print(f"\n📁 {title}: {len(results)} files\n")
    
    for i, file in enumerate(results[:50], 1):
        size = file.stat().st_size
        size_str = _format_size_short(size)
        safety_level, _ = get_safety_level(file)
        
        if safety_level == "critical":
            indicator = "[CRITICAL]"
        elif safety_level == "warning":
            indicator = "[WARNING]"
        else:
            indicator = "[SAFE]"
        
        print(f"  {i}. {indicator} {file.name} ({size_str})")
        print(f"     📂 {file.parent}")
    
    if len(results) > 50:
        print(f"\n  ... and {len(results) - 50} more files")
    
    # Offer actions
    if results:
        print(f"\nFound {len(results)} files.")
        action = input("Do you want to perform actions on these files? (y/n): ").strip().lower()
        if action == 'y':
            # Import interactive_action from your cli
            interactive_action(results, dry_run)

def _format_size_short(bytes_size: int) -> str:
    """Format size short"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024*1024):.1f} MB"
    else:
        return f"{bytes_size / (1024*1024*1024):.1f} GB"
    
def main() -> None:
    """Main CLI entry point"""
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    args = sys.argv[1:]
    
    # Help flag
    if "--help" in args or "-h" in args:
        show_help()
        return
    
    # Version flag
    if "--version" in args or "-v" in args:
        print(f"fdel version {__version__}")
        return
    
    #banner uh just for fun
    if "--banner" in args or "-b" in args:
        from .banner import banner
        print(banner)
        return
    
    # Check for stats mode
    if args[0] == "stats":
        if len(args) < 2:
            print("Usage: fdel stats <path>")
            print("Example: fdel stats ~/Projects")
            return
        
        path = args[1]
        mode_stats(path)
        return
    
    # Check for find mode
    if args[0] == "find":
        if len(args) < 3:
            print("Usage: fdel find <path> <extension|pattern>")
            print("Examples:")
            print("  fdel find ~/Projects .py")
            print("  fdel find ~/Downloads .jpg")
            print("  fdel find ~/Documents '*.txt'")
            return
        
        path = args[1]
        query = args[2]
        dry_run = "--dry-run" in args
        
        mode_find(path, query, dry_run)
        return
    
    # Check for zip/unzip mode
    if args[0] == "zip":
        if len(args) < 2:
            print("Usage: fdel zip <file/folder> [output] [--dry-run]")
            print("Example: fdel zip ~/Documents")
            print("Example: fdel zip ~/Documents ~/backup/myfiles.zip")
            return
        
        path = args[1]
        dest = args[2] if len(args) > 2 and not args[2].startswith('--') else None
        dry_run = "--dry-run" in args
        
        mode_zip_operation(path, "zip", dest, dry_run)
        return
    
    if args[0] == "unzip":
        if len(args) < 2:
            print("Usage: fdel unzip <zipfile> [output_dir] [--dry-run]")
            print("Example: fdel unzip ~/Downloads/archive.zip")
            print("Example: fdel unzip ~/Downloads/archive.zip ~/extracted")
            return
        
        path = args[1]
        dest = args[2] if len(args) > 2 and not args[2].startswith('--') else None
        dry_run = "--dry-run" in args
        
        mode_zip_operation(path, "unzip", dest, dry_run)
        return
    
    if "--explain" in args or "-E" in args:
        from .explain import explain
        explain.explain_version()
        return
    
    # Check for undo mode
    if "--undo" in args:
        dry_run = "--dry-run" in args
        mode_undo(dry_run)
        return
    
    # Check for force flag (disable safety)
    force_mode = "--force" in args
    if force_mode:
        print("⚠️  WARNING: Force mode enabled - safety prompts disabled!")
        print("   This can be dangerous. Proceed with caution.")
        from .safety import SAFETY_CONFIG
        SAFETY_CONFIG["enable_protection"] = False
        args = [a for a in args if a != "--force"]
    
    # Check for explore mode
    if args[0] == "explore":
        if len(args) < 2:
            print("❌ Provide path! Example: fdel explore ~/Projects")
            return
        
        path = args[1]
        dry_run = "--dry-run" in args
        
        mode_explore(path, dry_run)
        return
    
    # Normal mode
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    
    if "--empty-dirs" in args:
        if len(args) < 2:
            print("❌ Provide path! Example: fdel ~/Downloads --empty-dirs")
            return
        path = args[0]
        mode_empty_dirs(path, dry_run)
    
    elif "--empty-files" in args:
        if len(args) < 2:
            print("❌ Provide path! Example: fdel ~/Downloads --empty-files")
            return
        path = args[0]
        mode_empty_files(path, dry_run)
    
    else:
        if len(args) < 2:
            print("❌ Provide path and keyword! Example: fdel ~/Downloads Gantz")
            print("   Or use 'fdel --help' for more options")
            return
        path = args[0]
        keyword = args[1]
        mode_keyword_search(path, keyword, dry_run)

if __name__ == "__main__":
    main()