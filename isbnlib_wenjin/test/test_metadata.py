# -*- coding: utf-8 -*-
# flake8: noqa
# pylint: skip-file
"""nose tests for metadata."""

# ADAPT to your case!


from nose.tools import assert_equals
from isbnlib import meta
from .._wenjin import query


def test_query():
    """Test with 'low level' queries."""
    assert_equals(len(repr(query('9789727576807'))) > 100, True)
    assert_equals(len(repr(query('9789720049612'))) > 100, True)
    assert_equals(len(repr(query('9789727228133'))) > 100, True)


def test_query_missing():
    """Test with 'low level' queries (missing data)."""
    assert_equals(len(repr(query('9781849692341'))) <= 2, True)
    assert_equals(len(repr(query('9781849692343'))) <= 2, True)


def test_query_wrong():
    """Test with 'low level' queries (wrong data)."""
    assert_equals(len(repr(query('9780000000'))) <= 2, True)
