
#!/usr/bin/env python3
"""Quick test for history functionality"""

import sys
from pathlib import Path
import json

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import directly from core
from fdel.core import HISTORY_FILE, _save_history
from fdel.safety import SAFETY_CONFIG

SAFETY_CONFIG["enable_protection"] = False

# Clean history
if HISTORY_FILE.exists():
    HISTORY_FILE.unlink()
    print(f"Cleaned old history: {HISTORY_FILE}")

# Create test file
test_file = Path("/tmp/test_history.txt")
test_file.write_text("test content")
print(f"\nCreated: {test_file}")

# Test save history directly
print("\nTesting _save_history directly...")
_save_history(test_file, Path("/tmp/renamed.txt"), "rename")
print(f"History file exists: {HISTORY_FILE.exists()}")

if HISTORY_FILE.exists():
    with open(HISTORY_FILE) as f:
        print(f"History content: {json.load(f)}")
else:
    print("ERROR: History file still not created!")

# Now test rename via the actual function
print("\nTesting rename_item...")
from fdel.core import rename_item

# Clean history again
if HISTORY_FILE.exists():
    HISTORY_FILE.unlink()

test_file.write_text("test content again")
success, msg = rename_item(str(test_file), "renamed.txt")
print(f"Rename result: {msg}")

if HISTORY_FILE.exists():
    with open(HISTORY_FILE) as f:
        print(f"History after rename: {json.load(f)}")
else:
    print("ERROR: rename_item did not create history file!")

# Test undo
if HISTORY_FILE.exists():
    print("\nTesting undo_last...")
    from fdel.core import undo_last
    success, msg = undo_last()
    print(f"Undo result: {msg}")

# Cleanup
renamed = Path("/tmp/renamed.txt")
if renamed.exists():
    renamed.unlink()
if test_file.exists():
    test_file.unlink()
if HISTORY_FILE.exists():
    HISTORY_FILE.unlink()