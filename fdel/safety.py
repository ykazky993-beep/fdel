"""
Safety configuration for fdel
Protects system files and sensitive data
"""

from pathlib import Path
import os

# ============ SAFETY CONFIGURATION ============

SAFETY_CONFIG = {
    "enable_protection": True,
    "require_typing_for_critical": True,
    "batch_ops_skip_critical": True,
    "warn_for_home_directory": True,
    "max_history_size": 50,
}

# Critical system paths (cannot be modified)
PROTECTED_PATHS = [
    Path("/bin"),
    Path("/boot"),
    Path("/dev"),
    Path("/etc"),
    Path("/lib"),
    Path("/lib64"),
    Path("/proc"),
    Path("/sbin"),
    Path("/sys"),
    Path("/usr"),
    Path("/var"),
    Path("/System"),  # macOS
    Path("/Library"),  # macOS
    Path("/Applications"),  # macOS
    Path("/Windows"),  # Windows
    Path("/Program Files"),  # Windows
    Path("/Program Files (x86)"),  # Windows
    Path("/System32"),  # Windows
]

# Protected folder names (case insensitive)
PROTECTED_FOLDERS = [
    # Linux system
    "systemd", "kernel", "boot", "efi", "grub",
    "initrd", "modules", "firmware", "udev", "dbus",
    "pam.d", "security", "selinux", "apparmor",
    "firewalld", "NetworkManager", "docker", "containerd",
    # Version control
    ".git", ".svn", ".hg", ".github",
    # Package managers
    "node_modules", "vendor", "site-packages",
    # System caches
    "__pycache__", ".cache", ".npm", ".pip",
]

# Protected file patterns (fnmatch)
PROTECTED_FILE_PATTERNS = [
    # System libraries
    "*.so", "*.so.*", "*.dll", "*.sys", "*.ko", "*.o",
    # System binaries
    "*.exe", "*.msi", "*.deb", "*.rpm", "*.dmg",
    # Configuration files
    "*.conf", "*.cfg", "*.ini", "*.config",
    # Log files
    "*.log", "*.pid", "*.sock",
    # Version control
    ".gitignore", ".gitattributes", ".gitmodules",
]

# Sensitive keywords in filenames
DANGEROUS_KEYWORDS = [
    # Security
    "passwd", "shadow", "sudoers", "fstab", "crypttab",
    "hosts", "hostname", "resolv.conf",
    # SSH & SSL
    "ssh", "ssl", "certificate", "cert", "key", "pem", "crt", "priv",
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
    # Credentials
    "token", "secret", "credential", "password", "apikey", "api_key",
    "private", "secret", ".env", "env",
    # Database
    "database", "db.sqlite", "mysql", "postgres", "redis",
]

# Safe extensions (user files)
SAFE_EXTENSIONS = [
    ".txt", ".md", ".rst", ".org",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",
    ".mp3", ".mp4", ".wav", ".flac", ".ogg",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
    ".py", ".js", ".html", ".css", ".json", ".yaml", ".yml", ".xml",
    ".c", ".cpp", ".h", ".java", ".go", ".rs", ".swift",
]

def is_safe_extension(filename: str) -> bool:
    """Check if file has a safe extension"""
    from fnmatch import fnmatch
    for pattern in SAFE_EXTENSIONS:
        if filename.lower().endswith(pattern):
            return True
    return False

def get_user_critical_confirm() -> bool:
    """Get confirmation for critical operations"""
    print("\n" + "=" * 70)
    print("🔴CRITICAL PROTECTION TRIGGERED!")
    print("=" * 70)
    print("\n⚠️  THIS OPERATION AFFECTS CRITICAL SYSTEM FILES!")
    print("   Modifying these files can:")
    print("   • Break your operating system")
    print("   • Cause data loss")
    print("   • Make your system unbootable")
    print("\n   Only proceed if you ABSOLUTELY know what you're doing.")
    print("=" * 70)
    
    confirm = input("\n(⚠️WARNING HIGH RISK!) type 'y' to continue: ").strip()
    return confirm == "y"

def get_user_warning_confirm(reason: str) -> bool:
    """Get confirmation for warning level operations"""
    print("\n" + "=" * 50)
    print(f"⚠️  WARNING: {reason}")
    print("=" * 50)
    confirm = input("\nContinue anyway? (y/n): ").strip().lower()
    return confirm == "y"