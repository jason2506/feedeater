# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from datetime import datetime
from itertools import imap, ifilter

import celery
import urllib3
from lxml import etree
from dateutil.parser import parse

from worker import app, engine
from .models import Session, Item, Rule, Feed, Source, create_all, drop_all
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
        item.updated_at = parse(pub_date_elem.text).replace(tzinfo=None)
        item.crawled_at = datetime.now()

    return item


def _extract_items(url):
    response = _http.request('GET', url)
    root = etree.fromstring(response.data, etree.XMLParser())
    return imap(_extract_feed_item, root.iter('item'))


def _extract_item_content(feed_id, sel):
    def extract_content(item):
        response = _http.request('GET', item.url)
        root = etree.fromstring(response.data, etree.HTMLParser())
        item.content = '\n'.join(sel(root))
        item.feed_id = feed_id
        return item
    return extract_content


def _item_updated(items):
    def predicate(item):
        if item.item_id not in items:
            result = True
        else:
            result = item.updated_at > items[item.item_id]

        items[item.item_id] = item.updated_at
        return result
    return predicate


@app.task
def init_db():
    create_all(engine)


@app.task
def drop_db():
    drop_all(engine)


@app.task(base=_DatabaseTask)
def crawl(feed_id, url, sel):
    records = Session.query(Item.item_id, Item.updated_at).filter(Item.feed_id == feed_id)
    old_items = {item_id: updated_at for item_id, updated_at in records}

    items = imap(_extract_item_content(feed_id, sel),
                 ifilter(_item_updated(old_items), _extract_items(url)))
    Session.add_all(items)
    Session.commit()


@app.task(base=_DatabaseTask)
def crawl_all():
    sources = Session.query(Source).all()
    for source in sources:
        sel = Selector(source.rules)
        for feed in source.feeds:
            crawl(feed.id, feed.url, sel)

    return sources
