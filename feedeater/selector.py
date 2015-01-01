# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from itertools import imap, chain

from cssselect import GenericTranslator
from lxml.etree import XPath

_CONTENT_TAGS = (
    'a', 'abbr', 'acronym', 'b', 'bdo', 'big', 'cite', 'code', 'dfn', 'em',
    'i', 'kbd', 'q', 'samp', 'small', 'span', 'strong', 'sub', 'sup', 'tt', 'var'
)


def _extract_text(node):
    text = ''
    for child in node.xpath('*|text()'):
        if isinstance(child, basestring):
            text += child
        elif child.tag in _CONTENT_TAGS:
            text += child.xpath('string()')
        else:
            text = text.strip()
            if text:
                yield text
            text = ''

    text = text.strip()
    if text:
        yield text


class Selector(object):

    def __init__(self, rules):
        css_to_xpath = GenericTranslator().css_to_xpath
        self._paths = tuple(XPath(css_to_xpath(rule.path) if rule.type == 'CSS' else rule.path)
                            for rule in rules)

    def __call__(self, node):
        nodes = (node,)
        for path in self._paths:
            nodes = chain.from_iterable(imap(path, nodes))

        return chain.from_iterable(imap(_extract_text, nodes))
