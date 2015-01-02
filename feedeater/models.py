# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.orderinglist import ordering_list

Session = scoped_session(sessionmaker())
_ModelBase = declarative_base()


def bind_engine(engine):
    Session.configure(bind=engine)


def create_all(engine):
    _ModelBase.metadata.create_all(engine)


def drop_all(engine):
    _ModelBase.metadata.drop_all(engine)


class _ModelMixin(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)


class Rule(_ModelMixin, _ModelBase):

    type = sa.Column(sa.Enum('XPATH', 'CSS'), nullable=False)
    path = sa.Column(sa.String(32), nullable=False)
    position = sa.Column(sa.Integer, nullable=False)

    source_id = sa.Column(sa.Integer, sa.ForeignKey('source.id'), nullable=False)


class Item(_ModelMixin, _ModelBase):

    item_id = sa.Column(sa.String(256), nullable=False)
    url = sa.Column(sa.String(256), nullable=False)
    title = sa.Column(sa.String(32), nullable=False)
    content = sa.Column(sa.Text, nullable=False)
    updated_at = sa.Column(sa.DateTime, nullable=False)
    crawled_at = sa.Column(sa.DateTime, nullable=False)

    source_id = sa.Column(sa.Integer, sa.ForeignKey('source.id'), nullable=False)


class Feed(_ModelMixin, _ModelBase):

    name = sa.Column(sa.String(32), nullable=False)
    url = sa.Column(sa.String(256), nullable=False)

    source_id = sa.Column(sa.Integer, sa.ForeignKey('source.id'), nullable=False)


class Source(_ModelMixin, _ModelBase):

    name = sa.Column(sa.String(32), nullable=False)
    url = sa.Column(sa.String(256), nullable=False)

    feeds = relationship(Feed)
    items = relationship(Item)
    rules = relationship(Rule, cascade='all, delete-orphan',
                         order_by=Rule.position,
                         collection_class=ordering_list('position'))
