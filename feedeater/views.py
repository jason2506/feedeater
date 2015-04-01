# -*- coding: utf-8 -*-

from flask import Blueprint, url_for, request, abort, redirect, render_template

from .models import db, Item, Feed, Source
from .forms import FeedForm, SourceForm

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


def _source_endpoint(source_id):
    source_name = db.session.query(Source.name) \
        .filter_by(id=source_id) \
        .scalar()
    if source_name is None:
        abort(404)

    return (source_name, url_for('.show_feeds', source_id=source_id))


def _feed_endpoint(feed_id, source_id):
    feed_name = db.session.query(Feed.name) \
        .filter_by(id=feed_id, source_id=source_id) \
        .scalar()
    if feed_name is None:
        abort(404)

    return (feed_name, url_for('.show_items', source_id=source_id,
                               feed_id=feed_id))


@module.route('/')
def index():
    return redirect(url_for('.show_sources'))


@module.route('/sources')
def show_sources():
    page = request.args.get('page', default=1, type=int)
    pagination = Source.query.paginate(page, _PER_PAGE)
    return render_template('show_sources.html', pagination=pagination)


@module.route('/sources/new', methods=('GET', 'POST'))
@module.route('/sources/<int:source_id>/edit', methods=('GET', 'POST'))
def edit_source(source_id=None):
    source = Source() if source_id is None \
        else Source.query.get_or_404(source_id)

    form = SourceForm(request.form, obj=source)
    if form.validate_on_submit():
        form.populate_obj(source)
        source.save()
        return redirect(url_for('.show_sources'))

    return render_template('edit_source.html', form=form)


@module.route('/sources/<int:source_id>/delete')
def delete_source(source_id):
    Source.get(source_id).delete()
    db.session.commit()
    return redirect(url_for('.show_sources'))


@module.route('/sources/<int:source_id>/feeds')
def show_feeds(source_id):
    page = request.args.get('page', default=1, type=int)
    pagination = Feed.query.filter_by(source_id=source_id) \
        .paginate(page, _PER_PAGE)

    breadcrumb = (_source_endpoint(source_id),)
    return render_template(
        'show_feeds.html',
        source_id=source_id,
        pagination=pagination,
        breadcrumb=breadcrumb)


@module.route('/sources/<int:source_id>/feeds/new', methods=('GET', 'POST'))
@module.route('/sources/<int:source_id>/feeds/<int:feed_id>/edit',
              methods=('GET', 'POST'))
def edit_feed(source_id, feed_id=None):
    feed = Feed(source_id=source_id) if feed_id is None \
        else Feed.query.filter_by(id=feed_id, source_id=source_id).first_or_404()

    form = FeedForm(request.form, obj=feed)
    if form.validate_on_submit():
        form.populate_obj(feed)
        feed.save()
        return redirect(url_for('.show_feeds', source_id=source_id))

    breadcrumb = (_source_endpoint(source_id),)
    return render_template('edit_feed.html', form=form, breadcrumb=breadcrumb)


@module.route('/sources/<int:source_id>/feeds/<int:feed_id>/delete')
def delete_feed(source_id, feed_id):
    Feed.query.filter_by(id=feed_id, source_id=source_id).delete()
    db.session.commit()
    return redirect(url_for('.show_feeds', source_id=source_id))


@module.route('/sources/<int:source_id>/feeds/<int:feed_id>/items')
def show_items(source_id, feed_id):
    page = request.args.get('page', default=1, type=int)
    pagination = Item.query.filter_by(source_id=source_id, feed_id=feed_id) \
        .order_by(Item.crawled_at.desc()) \
        .paginate(page, _PER_PAGE)

    breadcrumb = (_source_endpoint(source_id),
                  _feed_endpoint(feed_id, source_id))
    return render_template(
        'show_items.html',
        pagination=pagination,
        breadcrumb=breadcrumb)
