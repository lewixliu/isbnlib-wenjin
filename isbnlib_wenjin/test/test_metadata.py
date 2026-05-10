# -*- coding: utf-8 -*-
# flake8: noqa
# pylint: skip-file
"""pytest tests for isbnlib-wenjin."""

import pytest
from isbnlib.dev._exceptions import DataNotFoundAtServiceError
from .._wenjin import query, parser_search, _mapper


# ============================================================
# HTML fixtures (no network required)
# ============================================================

HTML_ONE_RESULT = """
<html><body>
<div class="search_information">
  <b id="totalCnt">1</b>
  <div class="article_list">
    <div class="article_item">
      <div class="book_name"><a>深入理解计算机系统</a></div>
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
      <div class="book_name"><a>无著者书目</a></div>
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


# ============================================================
# Unit tests: parser_search (no network)
# ============================================================

def test_parser_search_one_result():
    """Parses a single result correctly."""
    records = parser_search(HTML_ONE_RESULT)
    assert records['title'] == '深入理解计算机系统'
    assert records['year'] == '2016'
    assert records['publisher'] == '机械工业出版社'
    assert '布莱恩特' in records['authors'][0]


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
# Unit tests: _mapper (no network)
# ============================================================

def test_mapper_valid_records():
    """Maps valid records to canonical metadata format."""
    records = {
        'title': '测试书名',
        'authors': ['张三'],
        'publisher': '测试出版社',
        'year': '2020',
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
# ============================================================

@pytest.mark.network
def test_query_known_chinese_isbn():
    """Queries a known Chinese ISBN that exists on Wenjin."""
    result = query('9787302423287')
    assert result['ISBN-13'] == '9787302423287'
    assert result['Title']
    assert isinstance(result['Authors'], list)
    assert result['Language'] == 'zh'


@pytest.mark.network
def test_query_result_has_all_fields():
    """All canonical metadata fields are present."""
    result = query('9787302423287')
    for field in ('ISBN-13', 'Title', 'Authors', 'Publisher', 'Year', 'Language'):
        assert field in result


@pytest.mark.network
def test_query_not_found():
    """Raises DataNotFoundAtServiceError for a valid ISBN not in Wenjin."""
    with pytest.raises(DataNotFoundAtServiceError):
        query('9787000000002')
