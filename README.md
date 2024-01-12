# isbnlib-wenjin
An unofficial metadata extension for the isbnlib Python library that pulls information from the Wenjin service (http://find.nlc.cn/) from The National Library of China.

## Requirements
Requires the following Python modules:
* isbnlib (version >= 3.9.1)
* beautifulsoup4 (version >= 4.7.1)

These are all available from PyPI (https://pypi.org/).

## Installation

#### 1. Manually using setup.py

First, make sure that you have installed the required dependencies. Then you can clone the git repository and build the module using setup.py.
```shell
git clone https://github.com/lewixliu/isbnlib-wenjin
cd isbnlib-wenjin/
python setup.py check -s
python setup.py sdist bdist_wheel
```

## Usage
Once installed, a new metadata provider for isbnlib named 'wenjin' will be available.

```python
import isbnlib

isbnlib.meta(isbn='9787111334620', service='wenjin')
```

## License
(c) 2024 Lewix -- Code available under LGPL v3 license
