# -*- coding: utf-8 -*-
'''Query the Wenjin service for metadata from The National Library of China. '''


import logging

import bs4

from isbnlib._msk import msk
from isbnlib._core import to_isbn10
from isbnlib.dev import stdmeta
from isbnlib.dev._bouth23 import u
from isbnlib.dev._exceptions import (DataWrongShapeError, ISBNNotConsistentError,
                              DataNotFoundAtServiceError, NoDataForSelectorError,
                              RecordMappingError)
from isbnlib.dev.webquery import query as wquery

UA = 'isbnlib (gzip)'
SERVICE_SEARCH_URL = 'http://find.nlc.cn/search/doSearch?actualQuery=identifer:({isbn})'
SERVICE_DOC_DETAILS_URL = 'http://find.nlc.cn/search/showDocDetails?docId={docID}&dataSource={ds}'
LOGGER = logging.getLogger(__name__)

def parser_search(data):
    '''Parse the response from the Wenjin service. The input data is the result webpage in html from the search.'''
    records = {}

    soup = bs4.BeautifulSoup(data, features='html.parser')
    
    #logging.basicConfig(level=logging.DEBUG)

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
    except (AttributeError, KeyError) as ex:
        LOGGER.debug('Error parsing WorldCat html. Did the layout change?')
        records = {}

    return records


def _mapper(isbn, records):
    """Map canonical <- records."""
    # canonical:
    # -> ISBN-13, Title, Authors, Publisher, Year, Language
    try:
        # mapping: canonical <- records
        canonical = {}
        canonical['ISBN-13'] = u(isbn)
        canonical['Title'] = records.get('title', u(''))
        canonical['Authors'] = records.get('authors', u(''))
        canonical['Publisher'] = records.get('publisher', u(''))
        canonical['Year'] = records.get('year', u(''))
        canonical['Language'] = records.get('language', u('zh'))
        # TODO: Hardcoded to zh for now. Need to use SERVICE_DOC_DETAILS_URL to get doc details
    except:
        raise RecordMappingError(isbn)
    # call stdmeta for extra cleanning and validation
    return stdmeta(canonical)

def query(isbn):
    """Query the Wenjin service for metadata."""

    data = wquery(SERVICE_SEARCH_URL.format(
                    isbn=msk(isbn)
                    #isbn='11103.78'
                ),
                user_agent=UA,
                parser=parser_search)

    isbn10 = msk(to_isbn10(isbn))
    if not data and isbn10:
        # try to search with isbn10
        data = wquery(SERVICE_SEARCH_URL.format(
                isbn=isbn10
            ),
            user_agent=UA,
            parser=parser_search)

    if not data:
        raise DataNotFoundAtServiceError()
    return _mapper(isbn, data)
