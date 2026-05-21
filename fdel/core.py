from pathlib import Path
import os
from difflib import get_close_matches

def cari_file(start_path, keyword, max_results=10):
    """Cari file yang namanya mirip keyword"""
    results = []
    start = Path(start_path).expanduser()
    
    if not start.exists():
        raise FileNotFoundError(f"{start_path} not found!")
    
    for file in start.rglob("*"):
        if file.is_file() and keyword.lower() in file.name.lower():
            results.append(file)
            if len(results) >= max_results:
                break
    
    if results:
        names = [f.name for f in results]
        mirip = get_close_matches(keyword, names, n=len(results), cutoff=0.3)
        results.sort(key=lambda x: mirip.index(x.name) if x.name in mirip else 999)
    
    return results

def cari_folder_kosong(start_path):
    """Cari semua folder kosong"""
    start = Path(start_path).expanduser()
    kosong = []
    
    for folder in start.rglob("*"):
        if folder.is_dir():
            try:
                # Cek isi folder (include hidden files)
                isi = list(folder.iterdir())
                if not isi:
                    kosong.append(folder)
            except PermissionError:
                continue
    
    return kosong

def cari_file_kosong(start_path):
    """Cari semua file yang ukurannya 0 byte"""
    start = Path(start_path).expanduser()
    kosong = []
    
    for file in start.rglob("*"):
        if file.is_file():
            try:
                if file.stat().st_size == 0:
                    kosong.append(file)
            except (PermissionError, OSError):
                continue
    
    return kosong

def hapus_file(file_path, dry_run=False):
    """Hapus file/folder dengan konfirmasi"""
    path = Path(file_path).expanduser()
    
    if not path.exists():
        return False, f"{path.name} not found!"
    
    if dry_run:
        return True, f"[DRY RUN] will delete {path.name}"
    
    try:
        if path.is_file():
            os.remove(path)
            return True, f"{path.name} deleted!"
        elif path.is_dir():
            path.rmdir()  # Cuma bisa hapus folder kosong
            return True, f"Folder {path.name} deleted!"
    except OSError as e:
        return False, f"fail to delete  {path.name}: {e}"
    except Exception as e:
        return False, f"Error: {e}"
