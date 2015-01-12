# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from flask import Blueprint, url_for, request, abort, redirect, render_template
from sqlalchemy.sql.expression import func

from .models import Session, Item, Feed, Source
from .pagination import Pagination

module = Blueprint('feedeater', __name__,
                   template_folder='templates',
                   static_folder='static')

_PER_PAGE = 10


@module.app_template_filter('datetime')
def _jinja2_filter_datetime(date, fmt=None):
    if fmt is None:
        fmt = '%Y-%m-%d %H:%M'

    return date.strftime(fmt)


@module.app_template_global('url_for_page')
def _jinja2_url_for_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


@module.route('/')
def index():
    return redirect(url_for('.show_sources'))


@module.route('/sources')
def show_sources():
    page = request.args.get('page', default=1, type=int)
    count = Session.query(func.count(Source.id)).scalar()
    sources = Session.query(Source).slice(_PER_PAGE * (page - 1), _PER_PAGE * page)
    pagination = Pagination(page, _PER_PAGE, count)
    return render_template('show_sources.html', sources=sources, pagination=pagination)


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
    source_name = Session.query(Source.name).filter_by(id=source_id).scalar()
    if source_name is None:
        abort(404)

    page = request.args.get('page', default=1, type=int)
    count = Session.query(func.count(Feed.id)).filter_by(source_id=source_id).scalar()
    feeds = Session.query(Feed).filter_by(source_id=source_id).slice(_PER_PAGE * (page - 1), _PER_PAGE * page)
    pagination = Pagination(page, _PER_PAGE, count)

    breadcrumb = (
        (source_name, url_for('.show_feeds', source_id=source_id)),
    )
    return render_template('show_feeds.html', feeds=feeds, pagination=pagination, breadcrumb=breadcrumb)


@module.route('/sources/<int:source_id>/feeds/<int:feed_id>/edit')
def edit_feed(source_id, feed_id):
    source_name = Session.query(Source.name).filter_by(id=source_id).scalar()
    if source_name is None:
        abort(404)

    feed = Session.query(Feed).filter_by(id=feed_id, source_id=source_id).one()
    if feed is None:
        abort(404)

    breadcrumb = (
        (source_name, url_for('.show_feeds', source_id=source_id)),
    )
    return render_template('edit_feed.html', feed=feed, breadcrumb=breadcrumb)


@module.route('/sources/<int:source_id>/feeds/<int:feed_id>/delete')
def delete_feed(source_id, feed_id):
    Session.query(Feed).filter_by(id=feed_id, source_id=source_id).delete()
    return redirect(url_for('.show_feeds', source_id=source_id))


@module.route('/sources/<int:source_id>/feeds/<int:feed_id>/items')
def show_items(source_id, feed_id):
    source_name = Session.query(Source.name).filter_by(id=source_id).scalar()
    if source_name is None:
        abort(404)

    feed_name = Session.query(Feed.name).filter_by(id=feed_id, source_id=source_id).scalar()
    if feed_name is None:
        abort(404)

    page = request.args.get('page', default=1, type=int)
    count = Session.query(func.count(Item.id)).filter_by(feed_id=feed_id).scalar()
    items = Session.query(Item).filter_by(feed_id=feed_id).order_by(Item.crawled_at.desc()).slice(_PER_PAGE * (page - 1), _PER_PAGE * page)
    pagination = Pagination(page, _PER_PAGE, count)

    breadcrumb = (
        (source_name, url_for('.show_feeds', source_id=source_id)),
        (feed_name, url_for('.show_items', source_id=source_id, feed_id=feed_id)),
    )
    return render_template('show_items.html', items=items, pagination=pagination, breadcrumb=breadcrumb)
