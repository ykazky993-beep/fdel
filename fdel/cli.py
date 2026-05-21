#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from .core import cari_file, cari_folder_kosong, cari_file_kosong, hapus_file
from .explorer import explore_folder, cari_dan_hapus_dari_explore

def tampilkan_hasil(items, title="founded"):
    """Tampilkan daftar file/folder dengan nomor"""
    if not items:
        print(f"{title}: 0")
        return False
    
    print(f"\n📁 {title}: {len(items)}\n")
    for i, item in enumerate(items, 1):
        if item.is_file():
            size = item.stat().st_size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024*1024):.1f} MB"
            print(f"  {i}. {item.name} ({size_str})")
        else:
            print(f"  {i}. {item.name}/")
        print(f"     📂 {item.parent}")
    
    return True

def proses_hapus_interaktif(items, dry_run=False):
    """Handle hapus interaktif dengan pilihan nomor/nama"""
    if not items:
        return
    
    print("\n" + "="*50)
    
    while True:
        pilihan = input("\nPick item (number/name, type 'q' quit, 'a' delete all): ").strip()
        
        if pilihan.lower() == 'q':
            break
        
        if pilihan.lower() == 'a':
            print(f"\ndelete all {len(items)} item?")
            confirm = input("you sure? (yes/no): ").strip().lower()
            if confirm == 'yes':
                for item in items[:]:
                    success, msg = hapus_file(item, dry_run)
                    print(msg)
                    if success and not dry_run:
                        items.remove(item)
                print(f"\n✨ remaining {len(items)} item have not been processed")
            continue
        
        # Cek pilihan nomor
        if pilihan.isdigit():
            idx = int(pilihan) - 1
            if 0 <= idx < len(items):
                target = items[idx]
            else:
                print(f"number {pilihan} not found!")
                continue
        else:
            # Cari berdasarkan nama (case insensitive)
            cocok = [i for i in items if i.name.lower() == pilihan.lower()]
            if cocok:
                target = cocok[0]
            else:
                print(f"can't find '{pilihan}'")
                continue
        
        # Konfirmasi hapus
        tipe = "file" if target.is_file() else "folder"
        print(f"\ndelete {tipe}: {target.name}")
        confirm = input(f"Delete? (y/n): ").strip().lower()
        
        if confirm == 'y':
            success, msg = hapus_file(target, dry_run)
            print(msg)
            if success and not dry_run:
                items.remove(target)
                if not items:
                    print("\nall item processed!")
                    break
        elif confirm == 'n':
            print("cancel")
        else:
            print("type 'y' or 'n'")

def mode_explore(path, dry_run=False):
    """Mode explore: liat struktur project dan hapus pake keyword"""
    # Debug: print path yang diterima
    print(f"🔍 Debug: path was received = '{path}'")
    
    if not path:
        print("path can't be empty!")
        return
    
    # Expand user path (buat ~)
    try:
        expanded_path = Path(path).expanduser()
        print(f"Explore: {expanded_path}")
        
        # Cek apakah path ada
        if not expanded_path.exists():
            print(f"Path '{expanded_path}' not found!")
            return
        
        # Tampilkan struktur folder
        explore_folder(str(expanded_path))
        
        print("\n" + "="*50)
        
        # Minta keyword buat hapus
        keyword = input("\ndelete file/folder with what keyword?? (enter for skip): ").strip()
        
        if keyword:
            cari_dan_hapus_dari_explore(str(expanded_path), keyword, dry_run)
        else:
            print("cancel")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def mode_keyword_search(path, keyword, dry_run=False):
    """Mode cari berdasarkan keyword"""
    print(f"searching file with keyword '{keyword}' in {path}...")
    
    try:
        hasil = cari_file(path, keyword)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    
    if tampilkan_hasil(hasil, f"similiar file '{keyword}' founded"):
        proses_hapus_interaktif(hasil, dry_run)

def mode_empty_dirs(path, dry_run=False):
    """Mode cari folder kosong"""
    print(f"🔍 searching empty folder in {path}...")
    
    try:
        hasil = cari_folder_kosong(path)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    
    if tampilkan_hasil(hasil, "empty folder founded"):
        proses_hapus_interaktif(hasil, dry_run)

def mode_empty_files(path, dry_run=False):
    """Mode cari file kosong (0 byte)"""
    print(f"🔍 searching empty file (0 byte) in {path}...")
    
    try:
        hasil = cari_file_kosong(path)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    
    if tampilkan_hasil(hasil, "empty founded"):
        proses_hapus_interaktif(hasil, dry_run)

def main():
    # Manual parsing karena argparse ribet dengan mode
    if len(sys.argv) < 2:
        print("""
  fdel explore <path>
  fdel explore <path> --dry-run
  
  fdel <path> <keyword>
  fdel <path> <keyword> --dry-run
  
  fdel <path> --empty-dirs
  fdel <path> --empty-files

example:
  fdel explore ~/Projects
  fdel ~/Downloads file
  fdel ~/Downloads --empty-dirs
        """)
        return
    
    # Parse arguments manual
    args = sys.argv[1:]
    
    # Cek mode explore
    if args[0] == "explore":
        if len(args) < 2:
            print("need path! example: fdel explore ~/Projects")
            return
        
        path = args[1]
        dry_run = "--dry-run" in args
        
        mode_explore(path, dry_run)
        return
    
    # Mode normal
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    
    if "--empty-dirs" in args:
        if len(args) < 2:
            print("need path! example: fdel ~/Downloads --empty-dirs")
            return
        path = args[0]
        mode_empty_dirs(path, dry_run)
    
    elif "--empty-files" in args:
        if len(args) < 2:
            print("need path! example: fdel ~/Downloads --empty-files")
            return
        path = args[0]
        mode_empty_files(path, dry_run)
    
    else:
        # Cari keyword
        if len(args) < 2:
            print("need path and keyword! example: fdel ~/Downloads Gantz")
            return
        path = args[0]
        keyword = args[1]
        mode_keyword_search(path, keyword, dry_run)

if __name__ == "__main__":
    main()
