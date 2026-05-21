# fdel
fuzzy deleted, auto tree file

# How To Use
>git clone https://github.com/ykazky993-beep/fdel.git
>cd fdel
>pip install .

# How To Use fdel
>fdel explore {path}

its will explore folder/file in that path

>fdel explore {path} --dry-run

its will explore folder/file in that path but can't delete file/folder

>fdel {path} {keyword}

its will searching path is similiar with keyword

>fdel {path} {keyword} --dry-run

its will searching path is similiar with keyword but can't delete file/folder

>fdel {path} --empty-dirs

its will searching directory/folder its empty

>fdel {path} --empty-files

its will searching file its empty

example:
>fdel explore ~/Projects

>fdel ~/Downloads file

>fdel ~/Downloads --empty-dirs
