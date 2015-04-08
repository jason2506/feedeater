# -*- coding: utf-8 -*-

from operator import attrgetter

from flask import Markup, url_for


def _attr_getter(name):
    escape = Markup.escape

    def getter(item):
        return escape(getattr(item, name))

    return getter


def create_field(attr):
    return _attr_getter(attr)


def create_link_field(attr, url_attr=None):
    text_getter = _attr_getter(attr)
    url_getter = text_getter if url_attr is None else _attr_getter(url_attr)

    def render(item):
        text, url = text_getter(item), url_getter(item)
        return '<a href="{}">{}</a>'.format(url, text)

    return render


def create_endpoint_link_field(attr, endpoint, url_kw_attr=None):
    text_getter = _attr_getter(attr)
    if url_kw_attr is None:
        url_kw_attr = {}

    def render(item):
        text = text_getter(item)
        kwargs = {k: getattr(item, v) for k, v in url_kw_attr.iteritems()}
        url = url_for(endpoint, **kwargs)
        return '<a href="{}">{}</a>'.format(url, text)

    return render


def create_datetime_field(attr, fmt=None):
    dt_getter = attrgetter(attr)
    if fmt is None:
        fmt = '%Y-%m-%d %H:%M'

    def render(item):
        dt = dt_getter(item)
        return dt.strftime(fmt)

    return render
