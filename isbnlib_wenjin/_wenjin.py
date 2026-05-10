# -*- coding: utf-8 -*-
'''Query the Wenjin service for metadata from The National Library of China. '''

import logging
import re

import bs4

from isbnlib._msk import msk
from isbnlib._core import to_isbn10
from isbnlib.dev import stdmeta
from isbnlib.dev._exceptions import (DataNotFoundAtServiceError, RecordMappingError)
from isbnlib.dev.webquery import query as wquery

UA = 'isbnlib (gzip)'
SERVICE_SEARCH_URL = 'http://find.nlc.cn/search/doSearch?actualQuery=identifer:({isbn})'
SERVICE_DOC_DETAILS_URL = 'http://find.nlc.cn/search/showDocDetails?docId={docId}&dataSource={ds}'
LOGGER = logging.getLogger(__name__)

# ISO 639-1 codes for languages commonly found in NLC
_LANG_MAP = {
    'Chinese': 'zh',
    'English': 'en',
    'Japanese': 'ja',
    'German': 'de',
    'French': 'fr',
    'Russian': 'ru',
    'Korean': 'ko',
    'Spanish': 'es',
    'Italian': 'it',
    'Arabic': 'ar',
    'Portuguese': 'pt',
}

# Chinese responsibility role suffixes (e.g. '周志华著', '张三，李四编')
_ROLE_SUFFIX_RE = re.compile(
    r'(?:总主编|副主编|责任编辑|主编|编著|编译|改写|整理|摄影|[著编译注评校订绘])+$'
)


def _parse_language(lang_str):
    """Convert Wenjin language string (e.g. 'Chinese  汉语') to ISO 639-1 code."""
    first_word = lang_str.split()[0] if lang_str else ''
    return _LANG_MAP.get(first_word, 'zh')


def _parse_authors_detail(authors_str):
    """Parse complete author list from 所有责任者 field.

    Strips Chinese role suffixes and splits on semicolons and commas.
    Examples:
      '周志华著'          -> ['周志华']
      '张启运，庄鸿寿编'  -> ['张启运', '庄鸿寿']
      '张三著；李四译'    -> ['张三', '李四']
    """
    authors = []
    for group in re.split(r'[;；]', authors_str):
        group = _ROLE_SUFFIX_RE.sub('', group.strip())
        authors.extend(p.strip() for p in re.split(r'[,，、]', group) if p.strip())
    return authors


def _get_detail_field(soup, label_text):
    """Extract a field value from the detail page by label text."""
    for span in soup.select('div.book_item span.book_val'):
        if label_text in span.get_text():
            sib = span.find_next_sibling('span')
            if sib:
                return sib.get_text(strip=True)
    return ''


def parser_search(data):
    '''Parse the search results page from the Wenjin service.'''
    records = {}
    soup = bs4.BeautifulSoup(data, features='html.parser')
    try:
        search_info = soup.find('div', class_='search_information')
        total_count = search_info.select_one('b#totalCnt').contents[0]
        LOGGER.info("Found {} results".format(total_count))

        if int(total_count) == 0:
            return records

        # Get the first item, use select() to get all results
        item = search_info.select_one('div.article_list div.article_item')

        a_tag = item.select_one('div.book_name a')
        records['title'] = a_tag.string.strip()

        # Extract docId and dataSource for the detail page request
        records['doc_id'] = a_tag.get('id', '')
        m = re.search(
            r"makeDetailUrl\([^,]+,\s*'[^']+',\s*'[^']+',\s*'([^']+)'",
            a_tag.get('onclick', ''),
        )
        records['data_source'] = m.group(1) if m else ''

        book_vals = item.select('div.book_right div.book_type')
        for val in book_vals:
            LOGGER.debug(val.contents)
            if '著者：' in val.contents[0].strip():
                records['authors'] = [val.find('span', class_='book_val').contents[0].strip()]
            if '出版年份：' in val.contents[0].strip():
                records['year'] = val.find('span', class_='book_val').contents[0].strip()
                records['publisher'] = val.select_one('span.book_she span.book_val').contents[0].strip()

        LOGGER.info(records)
    except (AttributeError, KeyError):
        LOGGER.debug('Error parsing Wenjin html. Did the layout change?')
        records = {}

    return records


def parser_detail(data):
    '''Parse the detail page from the Wenjin service for additional metadata.'''
    records = {}
    soup = bs4.BeautifulSoup(data, features='html.parser')
    try:
        lang_str = _get_detail_field(soup, '语种')
        if lang_str:
            records['language'] = _parse_language(lang_str)

        authors_str = _get_detail_field(soup, '所有责任者')
        if authors_str:
            records['authors'] = _parse_authors_detail(authors_str)
    except (AttributeError, KeyError):
        LOGGER.debug('Error parsing Wenjin detail html. Did the layout change?')

    return records


def _mapper(isbn, records):
    """Map canonical <- records."""
    try:
        canonical = {}
        canonical['ISBN-13'] = isbn
        canonical['Title'] = records.get('title', '')
        canonical['Authors'] = records.get('authors', '')
        canonical['Publisher'] = records.get('publisher', '')
        canonical['Year'] = records.get('year', '')
        canonical['Language'] = records.get('language', 'zh')
    except Exception:
        raise RecordMappingError(isbn)
    # call stdmeta for extra cleaning and validation
    return stdmeta(canonical)


def query(isbn):
    """Query the Wenjin service for metadata."""
    data = wquery(
        SERVICE_SEARCH_URL.format(isbn=msk(isbn)),
        user_agent=UA,
        parser=parser_search,
    )

    isbn10 = msk(to_isbn10(isbn))
    if not data and isbn10:
        # try to search with isbn10
        data = wquery(
            SERVICE_SEARCH_URL.format(isbn=isbn10),
            user_agent=UA,
            parser=parser_search,
        )

    if not data:
        raise DataNotFoundAtServiceError()

    # Fetch detail page for real language code and complete author list
    doc_id = data.pop('doc_id', None)
    data_source = data.pop('data_source', None)
    if doc_id and data_source:
        detail = wquery(
            SERVICE_DOC_DETAILS_URL.format(docId=doc_id, ds=data_source),
            user_agent=UA,
            parser=parser_detail,
        )
        if detail:
            data.update(detail)

    return _mapper(isbn, data)
