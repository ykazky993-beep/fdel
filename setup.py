from setuptools import setup, find_packages

setup(
    name="fdel",
    version="5.2.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "fdel = fdel.cli:main",
        ],
    },
    author="ykaz",
    description="find and delete file/folder with fuzzy matching",
    python_requires=">=3.6",
)
