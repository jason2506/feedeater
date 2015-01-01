# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from datetime import datetime
from itertools import imap

import celery
import urllib3
from lxml import etree
from dateutil.parser import parse

from worker import app, engine
from .models import Session, Item, Rule, Source, create_all, drop_all
from .selector import Selector

_http = urllib3.PoolManager()


class _DatabaseTask(celery.Task):

    abstract = True

    def after_return(self, *args, **kwargs):
        Session.remove()


def _extract_feed_item(node):
    guid_elem = node.find('./guid')
    pub_date_elem = node.find('./pubDate')
    url = node.find('./link').text
    item = Item(
        url=url,
        item_id=guid_elem.text if guid_elem is not None else url,
        title=node.find('./title').text,
        # description=node.find('./description').text
    )
    if pub_date_elem is not None:
        item.create_time = item.update_time = parse(pub_date_elem.text)
        item.last_crawl_time = datetime.now()

    return item


def _extract_items(url):
    response = _http.request('GET', url)
    root = etree.fromstring(response.data, etree.XMLParser())
    return imap(_extract_feed_item, root.iter('item'))


def _extract_item_content(source_id, sel):
    def extract_content(item):
        response = _http.request('GET', item.url)
        root = etree.fromstring(response.data, etree.HTMLParser())
        item.content = '\n'.join(sel(root))
        item.source_id = source_id
        return item
    return extract_content


@app.task
def init_db():
    create_all(engine)


@app.task
def drop_db():
    drop_all(engine)


@app.task(base=_DatabaseTask)
def crawl(source_id, url, sel):
    items = map(_extract_item_content(source_id, sel), _extract_items(url))
    Session.add_all(items)
    Session.commit()


@app.task(base=_DatabaseTask)
def crawl_all():
    sources = Session.query(Source).all()
    for source in sources:
        crawl(source.id, source.feed_url, Selector(source.rules))

    return sources
