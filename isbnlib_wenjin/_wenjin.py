# -*- coding: utf-8 -*-
'''Query the Wenjin service for metadata from The National Library of China. '''

import logging

import bs4

from isbnlib._msk import msk
from isbnlib._core import to_isbn10
from isbnlib.dev import stdmeta
from isbnlib.dev._exceptions import (DataNotFoundAtServiceError, RecordMappingError)
from isbnlib.dev.webquery import query as wquery

UA = 'isbnlib (gzip)'
SERVICE_SEARCH_URL = 'http://find.nlc.cn/search/doSearch?actualQuery=identifer:({isbn})'
LOGGER = logging.getLogger(__name__)


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

        records['title'] = item.select_one('div.book_name a').string.strip()
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
    return _mapper(isbn, data)
