from setuptools import find_packages, setup

setup(
    name="scene2table",
    version="1.0.0",
    author="CI&T Flow",
    description="Gerar tabela sintética de tracks e clips a partir de uma cena descrita em json.",
    packages=find_packages(where="src"),
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
            "scene2table=scene2table.cli:main",
        ],
    },
)
