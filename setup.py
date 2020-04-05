from setuptools import setup

VERSION = "0.0.1"

setup(
    name="gromax",
    version=VERSION,
    packages=["gromax"],
    description="Gromacs optimization tool",
    author="Kevin Boyd",
    author_email="kevin.boyd@uconn.edu",
    url="https://github.com/scal444/gromax",
    license="GPLv3",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Operating System  :: OS Independent',
        'Programming Language :: Python :: 3',
        'Typing :: Typed'
    ],

    entry_points={
        "console_scripts": [
            'gromax=gromax.main:gromax'
        ]
    }
)