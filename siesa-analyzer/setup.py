from setuptools import find_packages, setup

setup(
    name="siesa-analyzer",
    version="1.0.0",
    author="CI&T Flow",
    description="Gerador de documentações.",
    # Include both packages under src/ and top-level modules in src/
    packages=find_packages(where="src"),
    py_modules=[
        # list standalone modules located directly in src/
        # ensure cli.py is installed for console_scripts entry point
        "cli",
    ],
    package_dir={"": "src"},
    install_requires=open("requirements.txt").read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "siesa-analyzer=cli:main",
        ],
    },
)
