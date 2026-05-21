from pathlib import Path
from .core import hapus_file

def explore_folder(path):
    """Tampilkan isi folder kayak tree view"""
    start = Path(path).expanduser()
    
    if not start.exists():
        raise FileNotFoundError(f"{path} not found!")
    
    print(f"\n📁 {start}\n")
    print("=" * 50)
    
    folders = []
    files = []
    empty_folders = []
    empty_files = []
    
    # Kumpulin semua isi
    for item in sorted(start.iterdir()):
        if item.is_dir():
            folders.append(item)
            # Cek folder kosong
            try:
                if not any(item.iterdir()):
                    empty_folders.append(item)
            except PermissionError:
                pass
        else:
            files.append(item)
            if item.stat().st_size == 0:
                empty_files.append(item)
    
    # Tampilin folder
    for folder in folders:
        is_empty = " [EMPTY]" if folder in empty_folders else ""
        print(f"📂 {folder.name}/{is_empty}")
        
        # Tampilin isi folder level 1 (opsional)
        try:
            for sub in sorted(folder.iterdir())[:3]:
                if sub.is_file():
                    size = sub.stat().st_size
                    size_str = f"{size} B" if size < 1024 else f"{size/1024:.1f} KB"
                    print(f"  ├── {sub.name} ({size_str})")
                else:
                    print(f"  ├── {sub.name}/")
            if len(list(folder.iterdir())) > 3:
                print(f"  └── ... and {len(list(folder.iterdir())) - 3} etc.")
        except PermissionError:
            print(f"  └── [cant access]")
    
    # Tampilin file
    for file in files:
        size = file.stat().st_size
        if size == 0:
            size_str = "0 B [EMPTY]"
        elif size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024*1024):.1f} MB"
        
        empty_flag = " [EMPTY]" if size == 0 else ""
        print(f"📄 {file.name} ({size_str}){empty_flag}")
    
    print("=" * 50)
    print(f"Total: {len(folders)} folder, {len(files)} file | "
          f"{len(empty_folders)} folder empty, {len(empty_files)} file empty")
    
    return {
        "path": start,
        "folders": folders,
        "files": files,
        "empty_folders": empty_folders,
        "empty_files": empty_files
    }

def cari_dan_hapus_dari_explore(project_path, keyword, dry_run=False):
    """Cari file/folder berdasarkan keyword di project"""
    start = Path(project_path).expanduser()
    
    if not start.exists():
        return []
    
    results = []
    
    # Cari di semua subfolder
    for item in start.rglob("*"):
        if keyword.lower() in item.name.lower():
            results.append(item)
    
    if not results:
        print(f"not found file/folder with keyword '{keyword}'")
        return []
    
    print(f"\n🔍 founded {len(results)} item with keyword '{keyword}':\n")
    for i, item in enumerate(results, 1):
        tipe = "📂" if item.is_dir() else "📄"
        if item.is_file():
            size = item.stat().st_size
            size_str = f"({size} B)" if size < 1024 else f"({size/1024:.1f} KB)"
            print(f"  {i}. {tipe} {item.name} {size_str}")
        else:
            print(f"  {i}. {tipe} {item.name}/")
        print(f"     📍 {item.parent}")
    
    print("\n" + "="*50)
    
    while True:
        pilihan = input("\npick item (number/name, 'q' quit, 'a' delete all): ").strip()
        
        if pilihan.lower() == 'q':
            break
        
        if pilihan.lower() == 'a':
            print(f"\ndelete all {len(results)} item?")
            confirm = input("You sure? (yes/no): ").strip().lower()
            if confirm == 'yes':
                for item in results[:]:
                    success, msg = hapus_file(item, dry_run)
                    print(msg)
                    if success and not dry_run:
                        results.remove(item)
                print(f"\n✨ Sisa {len(results)} item")
            continue
        
        # Pilih berdasarkan nomor
        if pilihan.isdigit():
            idx = int(pilihan) - 1
            if 0 <= idx < len(results):
                target = results[idx]
            else:
                print(f"number {pilihan} not found!")
                continue
        else:
            # Pilih berdasarkan nama
            cocok = [r for r in results if r.name.lower() == pilihan.lower()]
            if cocok:
                target = cocok[0]
            else:
                print(f"not found item named '{pilihan}'")
                continue
        
        tipe = "folder" if target.is_dir() else "file"
        print(f"\ndelete {tipe}: {target.name}")
        confirm = input(f"Delete? (y/n): ").strip().lower()
        
        if confirm == 'y':
            success, msg = hapus_file(target, dry_run)
            print(msg)
            if success and not dry_run:
                results.remove(target)
        elif confirm == 'n':
            print("cancel")
    
    return results
