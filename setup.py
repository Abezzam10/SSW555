""" setup the package"""

import os
from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, 'README.md'), encoding='utf-8') as fp:
    long_description = fp.read()

setup(
    name='GEDCOM-Benji',
    version='0.0.0',
    description='Course project of SSW555.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    #url='not yet',
    author='Benjamin Cai',
    author_email='ycai11@stevens.edu',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='Stevens_Institute_of_Technology SSW555 CS555 James_Rowland his_courses_are_all_worth_to_choose!',
    py_modules=['cli', 'gedcom_benji'],
    install_requires=['Click', 'tabulate'],
    entry_points={
        'console_scripts': [
            'gedcom=cli:gedcom',
        ],
    },
)
