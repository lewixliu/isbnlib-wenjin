# -*- coding: utf-8 -*-
# flake8: noqa
# pylint: skip-file
"""pytest tests for isbnlib-wenjin."""

import pytest
from isbnlib.dev._exceptions import DataNotFoundAtServiceError
from .._wenjin import (
    query, parser_search, parser_detail,
    _mapper, _parse_language, _parse_authors_detail, _safe_msk,
)


# ============================================================
# HTML fixtures (no network required)
# ============================================================

# Chinese book: title as direct text in <a>
HTML_ONE_RESULT = """
<html><body>
<div class="search_information">
  <b id="totalCnt">1</b>
  <div class="article_list">
    <div class="article_item">
      <div class="book_name">
        <a href="javascript:void(0);" id="123456789"
           onclick="makeDetailUrl(this, '/search/showDocDetails?', '123456789', 'ucs01', '');"
           target="_blank">深入理解计算机系统</a>
      </div>
      <div class="book_right">
        <div class="book_type">著者：<span class="book_val">（美）布莱恩特（Bryant,R.E.）</span></div>
        <div class="book_type">出版年份：<span class="book_val">2016</span>
          <span class="book_she"><span class="book_val">机械工业出版社</span></span>
        </div>
      </div>
    </div>
  </div>
</div>
</body></html>
"""

# Foreign book: long title truncated in display, full title in <span title="...">
HTML_LONG_TITLE = """
<html><body>
<div class="search_information">
  <b id="totalCnt">1</b>
  <div class="article_list">
    <div class="article_item">
      <div class="book_name">
        <a href="javascript:void(0);" id="987654321"
           onclick="makeDetailUrl(this, '/search/showDocDetails?', '987654321', 'ucs09', '');"
           target="_blank">
          <span alt="Full Long Title Here" title="Full Long Title Here">Full Long Title ...</span>
        </a>
      </div>
      <div class="book_right">
        <div class="book_type">著者：<span class="book_val">Vickers</span></div>
        <div class="book_type">出版年份：<span class="book_val">2006</span>
          <span class="book_she"><span class="book_val">Routledge</span></span>
        </div>
      </div>
    </div>
  </div>
</div>
</body></html>
"""

HTML_ZERO_RESULTS = """
<html><body>
<div class="search_information">
  <b id="totalCnt">0</b>
  <div class="article_list"></div>
</div>
</body></html>
"""

HTML_NO_AUTHOR = """
<html><body>
<div class="search_information">
  <b id="totalCnt">1</b>
  <div class="article_list">
    <div class="article_item">
      <div class="book_name">
        <a href="javascript:void(0);" id="999"
           onclick="makeDetailUrl(this, '/search/showDocDetails?', '999', 'ucs01', '');"
           target="_blank">无著者书目</a>
      </div>
      <div class="book_right">
        <div class="book_type">出版年份：<span class="book_val">2020</span>
          <span class="book_she"><span class="book_val">测试出版社</span></span>
        </div>
      </div>
    </div>
  </div>
</div>
</body></html>
"""

HTML_DETAIL = """
<html><body>
<div class="book_item">
  <span class="book_val">语种\n：</span>
  <span class="book_type" style="word-break: break-all;">Chinese  汉语</span>
</div>
<div class="book_item">
  <span class="book_val">所有责任者\n：</span>
  <span class="book_type" style="word-break: break-all;">张三，李四著</span>
</div>
</body></html>
"""

HTML_DETAIL_ENGLISH = """
<html><body>
<div class="book_item">
  <span class="book_val">语种\n：</span>
  <span class="book_type" style="word-break: break-all;">English  英语</span>
</div>
<div class="book_item">
  <span class="book_val">所有责任者\n：</span>
  <span class="book_type" style="word-break: break-all;">John Smith著</span>
</div>
</body></html>
"""


# ============================================================
# Unit tests: _parse_language (no network)
# ============================================================

def test_parse_language_chinese():
    assert _parse_language('Chinese  汉语') == 'zh'

def test_parse_language_english():
    assert _parse_language('English  英语') == 'en'

def test_parse_language_japanese():
    assert _parse_language('Japanese  日语') == 'ja'

def test_parse_language_unknown_defaults_to_zh():
    assert _parse_language('Klingon  克林贡语') == 'zh'

def test_parse_language_empty():
    assert _parse_language('') == 'zh'


# ============================================================
# Unit tests: _safe_msk (no network)
# ============================================================

def test_safe_msk_valid_chinese():
    assert _safe_msk('9787302423287') == '978-7-302-42328-7'

def test_safe_msk_unregistered_prefix_returns_none():
    # 978-9-999... is not a registered publisher prefix; msk() returns ''
    assert _safe_msk('9789999999991') is None

def test_safe_msk_invalid_isbn10_returns_none():
    # '0000000000' is structurally invalid for msk
    assert _safe_msk('0000000000') is None

def test_safe_msk_none_input():
    assert _safe_msk(None) is None

def test_safe_msk_empty_input():
    assert _safe_msk('') is None


# ============================================================
# Unit tests: _parse_authors_detail (no network)
# ============================================================

def test_parse_authors_single():
    assert _parse_authors_detail('周志华著') == ['周志华']

def test_parse_authors_multiple_comma():
    assert _parse_authors_detail('张启运，庄鸿寿编') == ['张启运', '庄鸿寿']

def test_parse_authors_semicolon_groups():
    assert _parse_authors_detail('张三著；李四译') == ['张三', '李四']

def test_parse_authors_compound_suffix():
    assert _parse_authors_detail('黑马程序员编著') == ['黑马程序员']

def test_parse_authors_chief_editor():
    assert _parse_authors_detail('王五主编') == ['王五']


# ============================================================
# Unit tests: parser_search (no network)
# ============================================================

def test_parser_search_one_result():
    """Parses a Chinese book (title as direct text) correctly."""
    records = parser_search(HTML_ONE_RESULT)
    assert records['title'] == '深入理解计算机系统'
    assert records['year'] == '2016'
    assert records['publisher'] == '机械工业出版社'
    assert '布莱恩特' in records['authors'][0]
    assert records['doc_id'] == '123456789'
    assert records['data_source'] == 'ucs01'


def test_parser_search_long_title():
    """Uses span title attribute for long titles (foreign books)."""
    records = parser_search(HTML_LONG_TITLE)
    assert records['title'] == 'Full Long Title Here'
    assert records['doc_id'] == '987654321'
    assert records['data_source'] == 'ucs09'


def test_parser_search_zero_results():
    """Returns empty dict when total count is 0."""
    assert parser_search(HTML_ZERO_RESULTS) == {}


def test_parser_search_no_author():
    """Handles missing author field gracefully."""
    records = parser_search(HTML_NO_AUTHOR)
    assert records['title'] == '无著者书目'
    assert 'authors' not in records


def test_parser_search_empty_html():
    """Returns empty dict on malformed HTML without raising."""
    assert parser_search('<html></html>') == {}


def test_parser_search_blank():
    """Returns empty dict on blank input without raising."""
    assert parser_search('') == {}


# ============================================================
# Unit tests: parser_detail (no network)
# ============================================================

def test_parser_detail_chinese():
    """Parses language and authors from Chinese detail page."""
    records = parser_detail(HTML_DETAIL)
    assert records['language'] == 'zh'
    assert records['authors'] == ['张三', '李四']


def test_parser_detail_english():
    """Parses English language correctly."""
    records = parser_detail(HTML_DETAIL_ENGLISH)
    assert records['language'] == 'en'
    assert records['authors'] == ['John Smith']


def test_parser_detail_empty():
    """Returns empty dict on empty HTML without raising."""
    assert parser_detail('<html></html>') == {}


# ============================================================
# Unit tests: _mapper (no network)
# ============================================================

def test_mapper_valid_records():
    """Maps valid records to canonical metadata format."""
    records = {
        'title': '测试书名',
        'authors': ['张三'],
        'publisher': '测试出版社',
        'year': '2020',
        'language': 'zh',
    }
    result = _mapper('9787111334620', records)
    assert result['ISBN-13'] == '9787111334620'
    assert result['Title'] == '测试书名'
    assert result['Authors'] == ['张三']
    assert result['Publisher'] == '测试出版社'
    assert result['Year'] == '2020'
    assert result['Language'] == 'zh'


def test_mapper_empty_records():
    """Raises NotValidMetadataError when records have no title."""
    from isbnlib.dev._exceptions import NotValidMetadataError
    with pytest.raises(NotValidMetadataError):
        _mapper('9787111334620', {})


# ============================================================
# Integration tests (require network access)
#
# ISBN format coverage:
#   9787302423287  Chinese 978-7-*  → indexed as masked ISBN-13
#   9787111334620  Chinese 978-7-*  → multi-author via detail page
#   7115151695     Pre-978 Chinese  → indexed as bare ISBN-10
#   9780132662369  International   → indexed as bare ISBN-13
#   9780415976527  International   → long title with <span> wrapper
# ============================================================

@pytest.mark.network
def test_query_chinese_isbn13():
    """Chinese 978-7-* ISBN found via masked ISBN-13."""
    result = query('9787302423287')
    assert result['ISBN-13'] == '9787302423287'
    assert result['Title'] == '机器学习'
    assert result['Authors'] == ['周志华']
    assert result['Language'] == 'zh'


@pytest.mark.network
def test_query_chinese_multi_author():
    """Detail page provides complete multi-author list."""
    result = query('9787111334620')
    assert result['Authors'] == ['张启运', '庄鸿寿']
    assert result['Language'] == 'zh'


@pytest.mark.network
def test_query_pre978_bare_isbn10():
    """Old pre-978 Chinese ISBN found via bare ISBN-10."""
    result = query('9787115151698')  # same book as 7115151695
    assert result['ISBN-13'] == '9787115151698'
    assert result['Title']
    assert result['Language'] == 'en'


@pytest.mark.network
def test_query_international_bare_isbn13():
    """International ISBN found via bare ISBN-13."""
    result = query('9780132662369')
    assert result['ISBN-13'] == '9780132662369'
    assert result['Language'] == 'en'


@pytest.mark.network
def test_query_long_title_span_wrapper():
    """Foreign book with long title stored in <span title="..."> attribute."""
    result = query('9780415976527')
    assert result['ISBN-13'] == '9780415976527'
    assert '...' not in result['Title']
    assert result['Language'] == 'en'


@pytest.mark.network
def test_query_result_has_all_fields():
    """All canonical metadata fields are present."""
    result = query('9787302423287')
    for field in ('ISBN-13', 'Title', 'Authors', 'Publisher', 'Year', 'Language'):
        assert field in result


@pytest.mark.network
def test_query_not_found():
    """Raises DataNotFoundAtServiceError for a valid ISBN not in Wenjin."""
    # 9789999999991: valid check digit, unregistered prefix, confirmed 0 results
    with pytest.raises(DataNotFoundAtServiceError):
        query('9789999999991')
