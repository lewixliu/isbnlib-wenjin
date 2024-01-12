# -*- coding: utf-8 -*-

"""isbnlib-wenjin -- an isbnlib plugin for the Wenjin service."""

from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='isbnlib-wenjin',
    version='0.0.1',
    author='Lewix',
    author_email='lewix@ustc.edu',
    url='https://github.com/lewixliu/isbnlib-wenjin',
    download_url='',
    packages=['isbnlib_wenjin/'],
    entry_points={
        'isbnlib.metadata': ['wenjin=isbnlib_wenjin:query']
    },
    install_requires=['isbnlib>=3.9.1', 'beautifulsoup4>=4.7.1'],
    license='LGPL v3',
    description='An unofficial isbnlib plugin for the Wenjin service (http://find.nlc.cn/) from the National Library of China.',
    keywords='ISBN, isbnlib, wenjin, nlc',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'Topic :: Text Processing :: General',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
