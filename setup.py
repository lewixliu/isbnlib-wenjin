# -*- coding: utf-8 -*-

"""isbnlib-wenjin -- an isbnlib plugin for the Wenjin service."""

from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='isbnlib-wenjin',
    version='0.1.0',
    author='Lewix',
    author_email='lewix@ustc.edu',
    url='https://github.com/lewixliu/isbnlib-wenjin',
    download_url='',
    packages=['isbnlib_wenjin/', 'isbnlib_wenjin/test/'],
    entry_points={
        'isbnlib.metadata': ['wenjin=isbnlib_wenjin:query'],
    },
    install_requires=['isbnlib2>=3.11.0', 'beautifulsoup4>=4.7.1'],
    license='LGPL v3',
    description='An unofficial isbnlib plugin for the Wenjin service (http://find.nlc.cn/) from the National Library of China.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='ISBN, isbnlib, wenjin, nlc',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
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
