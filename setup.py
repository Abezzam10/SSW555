""" setup the package"""

import os
from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, 'README.md'), encoding='utf-8') as fp:
    long_description = fp.read()

setup(
    name='GEDCOM-AJRY',
    version='1.0.0',
    description='Course project of SSW555. Sprint_1 base line version.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/BenjiTheC/SSW555',
    author='Benjamin; Ray; John; Javer',
    author_email='ycai11@stevens.edu',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='Stevens_Institute_of_Technology SSW555 CS555',
    py_modules=['cli', 'gedcom_ajry'],
    install_requires=['Click', 'tabulate'],
    entry_points={
        'console_scripts': [
            'gedcom=cli:gedcom',
        ],
    },
)
