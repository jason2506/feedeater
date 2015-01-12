# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from flask import Blueprint, url_for, abort, redirect, render_template

from .models import Session, Item, Feed, Source

module = Blueprint('feedeater', __name__,
                   template_folder='templates',
                   static_folder='static')


@module.app_template_filter('datetime')
def _jinja2_filter_datetime(date, fmt=None):
    if fmt is None:
        fmt = '%Y-%m-%d %H:%M'

    return date.strftime(fmt)


@module.route('/')
def index():
    return redirect(url_for('.show_sources'))


@module.route('/sources')
def show_sources():
    sources = Session.query(Source).all()
    return render_template('show_sources.html', sources=sources)


@module.route('/sources/<int:source_id>/edit')
def edit_source(source_id):
    source = Session.query(Source).get(source_id)
    if source is None:
        abort(404)

    return render_template('edit_source.html', source=source)


@module.route('/sources/<int:source_id>/delete')
def delete_source(source_id):
    Session.query(Source).get(source_id).delete()
    return redirect(url_for('.show_sources'))


@module.route('/sources/<int:source_id>/feeds')
def show_feeds(source_id):
    source = Session.query(Source.name).filter_by(id=source_id).one()
    if source is None:
        abort(404)

    feeds = Session.query(Feed).filter_by(source_id=source_id)

    breadcrumb = (
        (source.name, url_for('.show_feeds', source_id=source_id)),
    )
    return render_template('show_feeds.html', feeds=feeds, breadcrumb=breadcrumb)


@module.route('/sources/<int:source_id>/feeds/<int:feed_id>/edit')
def edit_feed(source_id, feed_id):
    source = Session.query(Source.name).filter_by(id=source_id).one()
    if source is None:
        abort(404)

    feed = Session.query(Feed).filter_by(id=feed_id, source_id=source_id).one()
    if feed is None:
        abort(404)

    breadcrumb = (
        (source.name, url_for('.show_feeds', source_id=source_id)),
    )
    return render_template('edit_feed.html', feed=feed, breadcrumb=breadcrumb)


@module.route('/sources/<int:source_id>/feeds/<int:feed_id>/delete')
def delete_feed(source_id, feed_id):
    Session.query(Feed).filter_by(id=feed_id, source_id=source_id).delete()
    return redirect(url_for('.show_feeds', source_id=source_id))


@module.route('/sources/<int:source_id>/feeds/<int:feed_id>/items')
def show_items(source_id, feed_id):
    source = Session.query(Source.name).filter_by(id=source_id).one()
    if source is None:
        abort(404)

    feed = Session.query(Feed.name).filter_by(id=feed_id, source_id=source_id).one()
    if feed is None:
        abort(404)

    items = Session.query(Item).filter_by(feed_id=feed_id).order_by(Item.crawled_at.desc())

    breadcrumb = (
        (source.name, url_for('.show_feeds', source_id=source_id)),
        (feed.name, url_for('.show_items', source_id=source_id, feed_id=feed_id)),
    )
    return render_template('show_items.html', items=items, breadcrumb=breadcrumb)
