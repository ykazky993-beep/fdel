from .version import __version__

class explain():
    @staticmethod
    def explain_version():
        print(f"fdel version {__version__}")
        print("""
fdel - File Manager CLI Tool                      MIT License by Ykazky993-beep
              
================================================================================

fdel is a command-line tool (CLI) for file and folder management with tree view.
It helps you inspect directories and manage files or folders from the terminal.

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
---------------------------------------------------------------------------------
full manual fdel usage and safety explanation:         
Explore
    When you explore a folder, fdel will show you a tree view of its contents.
    It will also indicate if any items are considered "critical" or "warning" based on their names or paths.
    You can then choose to delete, move, rename, or copy these items directly from the explorer.
    usage:
        fdel explore <path>
              
search (real usage is fdel <path> <keyword>)
    You can search for files by providing a keyword. fdel will perform a fuzzy match and show you all matching files.
    From the search results, you can also choose to act on any file (delete, move, rename, copy).
    usage:
        fdel <path> <keyword>
              
empty-dirs / empty-files
    These options help you find and clean up empty directories or zero-byte files.
    This is useful for decluttering your file system and freeing up space.
    usage:
        fdel <path> --empty-dirs    #Find empty directories
        fdel <path> --empty-files   #Find empty files
              
undo
    If you accidentally delete, move, rename, or copy something, you can use the undo command to revert the last action.
    This adds an extra layer of safety and peace of mind when managing your files.
    usage:
        fdel --undo
              
dry-run
    If you want to see what actions would be taken without actually executing them, you can use the --dry-run option.
    This is especially useful when performing batch operations or when you're unsure about the safety of certain items.
    usage:
        fdel <path> <keyword> --dry-run
        fdel explore <path> --dry-run
        etc.
               
force
    The --force option allows you to bypass all safety prompts and confirmations. 
    This is not recommended unless you are absolutely sure about the actions you're taking, as it can lead to accidental data loss or system damage.
    usage:
        fdel <path> <keyword> --force
        fdel explore <path> --force
        etc.
              
zip / unzip
    fdel also provides built-in support for zipping and unzipping files and folders.
    You can easily create zip archives or extract them without needing additional tools.
    usage:
        fdel zip <path> [output]         # Zip a file or folder
        fdel unzip <zipfile> [output]    # Unzip a zip file
              
stats
    The stats command provides a comprehensive overview of the contents of a folder, including counts of files and folders, size distribution, safety levels, and more.
    This is useful for quickly assessing the state of a directory and identifying potential issues.
    usage:
        fdel stats <path>
              
find (by pattern / by extension)
    The find command allows you to search for files based on specific patterns or extensions.
    This is more powerful than the basic keyword search and can help you locate files that match certain criteria.
    usage:
        fdel find <path> <pattern>       # Find files by pattern (e.g., "*.txt")
        fdel find <path> <extension>     # Find files by extension (e.g., ".py")
              
SAFETY LAYER
    fdel has a built-in safety layer to protect critical system files and sensitive data.
    It uses a combination of protected paths, folder names, and file patterns to determine the safety level of each item.
    Critical items require typing confirmation, while warning items require yes/no confirmation before any action can be taken.
                    
CRITICAL ITEMS
    These are items that are essential for the operating system or critical applications to function properly.
    Deleting or modifying these items can lead to system instability, data loss, or even an unbootable system.
    Examples include system directories like /bin, /etc, /usr, and important files like .git, node_modules, etc.
              
WARNING ITEMS
    These are items that may not be critical for the system but are still important or sensitive.
    Deleting or modifying these items can lead to loss of important data, project files, or cause issues with applications.
    Examples include version control folders (.git), package manager folders (node_modules), and system caches (__pycache__, .cache).
              
SAFE ITEMS
    These are regular user files and folders that do not match any critical or warning patterns.
    They can be safely managed with normal confirmations.
      
help
    this is litrally manual page for fdel, you can see simple usage by running "fdel --help"
              
note:
    Always double-check the items you're managing, especially if they are marked as critical or warning.
    Use the --dry-run option to preview actions when in doubt, and avoid using --force unless you're certain about the safety of your actions.
    and we have test units for testing the system to check if core or other system its bug, you also can contribute to the project by adding more test units or improving the existing ones.
    and if there's any bug or issue you can report it to the github repository of the project, and if you have any suggestion or idea for improving the project you also can share it in the
    github repository, we will be happy to hear from you and we will try to implement your suggestion or idea if it's good and useful for the project.
    usage test units:
        python3 run_tests.py        # Run all tests functions
        python3 test_history.py     # Test undo functionality
        python3 test_zip_extract.py # Test zip and unzip functionality
""")