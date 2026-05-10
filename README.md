# isbnlib-wenjin

An unofficial metadata extension for [isbnlib](https://github.com/xlcnd/isbnlib) that pulls book information from the [Wenjin search service](http://find.nlc.cn/) (文津搜索) of The National Library of China.

## Requirements

- Python 3.7+
- [isbnlib2](https://pypi.org/project/isbnlib2/) >= 3.11.0 (fork of isbnlib compatible with modern setuptools)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) >= 4.7.1

## Installation

#### Install from GitHub

```bash
pip install git+https://github.com/lewixliu/isbnlib-wenjin.git
```

#### Install for local development

```bash
git clone https://github.com/lewixliu/isbnlib-wenjin
cd isbnlib-wenjin
pip install -e .
```

## Usage

Once installed, a new metadata provider named `wenjin` is available in isbnlib:

```python
import isbnlib

meta = isbnlib.meta('9787111334620', service='wenjin')
print(meta)
# {
#   'ISBN-13': '9787111334620',
#   'Title': '三元合金相图手册',
#   'Authors': ['张启运', '庄鸿寿'],
#   'Publisher': '机械工业出版社',
#   'Year': '2011',
#   'Language': 'zh'
# }
```

## Running Tests

```bash
# Unit tests only (no network required)
pytest -m "not network" -v

# All tests including network integration tests
pytest -v

# With coverage report
pytest --cov=isbnlib_wenjin -m "not network"
```

## Known Limitations

- **Language field** is hardcoded to `zh` (Chinese). Detecting the actual language would require an additional request to the book detail page.
- **HTML scraping**: The parser depends on the current Wenjin HTML structure. If the site layout changes, the parser may need to be updated.
- **First result only**: When multiple results are returned for an ISBN, only the first result is used.

## License

(c) 2024 Lewix — Code available under [LGPL v3](LICENSE-LGPL.txt) license
