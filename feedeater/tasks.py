# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from datetime import datetime
from itertools import imap, chain

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


def _extract_item_content(feed_id, sel, item):
    response = _http.request('GET', item.url)
    root = etree.fromstring(response.data, etree.HTMLParser())
    item.content = '\n'.join(sel(root))
    item.feed_id = feed_id
    return item


def _is_item_updated(old_items, item):
    if item.item_id not in old_items:
        result = True
    else:
        result = item.updated_at > old_items[item.item_id]

    old_items[item.item_id] = item.updated_at
    return result


@app.task
def init_db():
    create_all(engine)


@app.task
def drop_db():
    drop_all(engine)


def _crawl(feed, sel):
    old_items = {item.item_id: item.updated_at for item in feed.items}
    return (_extract_item_content(feed.id, sel, item)
            for item in _extract_items(feed.url)
            if _is_item_updated(old_items, item))


@app.task(base=_DatabaseTask)
def crawl_from_feed(feed_id):
    feed = Session.query(Feed).get(feed_id)
    if feed is None:
        return

    sel = Selector(feed.rules)
    items = _crawl(feed, sel)
    Session.add_all(items)
    Session.commit()


@app.task(base=_DatabaseTask)
def crawl_from_source(source_id):
    feeds = Session.query(Feed).filter_by(source_id=source_id)
    rules = Session.query(Rule).filter_by(source_id=source_id).order_by('position')
    sel = Selector(rules)
    items = chain.from_iterable(_crawl(feed, sel) for feed in feeds)
    Session.add_all(items)
    Session.commit()


@app.task(base=_DatabaseTask)
def crawl_all():
    sources = Session.query(Source).all()
    for source in sources:
        sel = Selector(source.rules)
        items = chain.from_iterable(_crawl(feed, sel) for feed in source.feeds)
        Session.add_all(items)

    Session.commit()
