from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fdel",
    version="4.0.0",
    author="Ykazky993-beep",
    author_email="ykazky993@gmail.com",
    description="File Manager CLI Tool - Search, Delete, Move, Rename, Copy with Safety Layer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ykazky993-beep/fdel",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "fdel = fdel.cli:main",
        ],
    },
    install_requires=[
        # No external dependencies - pure Python!
    ],
    keywords="file-manager, cli, delete, move, rename, copy, search, safety, protection",
    project_urls={
        "Bug Reports": "https://github.com/ykazky993-beep/fdel/issues",
        "Source": "https://github.com/ykazky993-beep/fdel",
    },
)
