# fdel
fuzzy deleted, auto tree file

# How To Use
>git clone https://github.com/ykazky993-beep/fdel.git
>cd fdel
>pip install .

# How To Use >fdel
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

>fdel explore <path>

its will explored your path

>fdel <path> <keyword>

its will searching file is similiar with the keyword

>fdel <path> <keyword> --dry-run
>fdel explore <path>

its will dry run (doesn't delete your file) if you confirm delete
