# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.orderinglist import ordering_list

db = SQLAlchemy()


class _CRUDMixin(object):

    id = db.Column(db.Integer, primary_key=True, nullable=False)

    @classmethod
    def get(cls, id):
        if isinstance(id, (int, float)) or \
           (isinstance(id, basestring) and id.isdigit()):
            return cls.query.get(int(id))
        return None

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()


class Schedule(_CRUDMixin, db.Model):

    __tablename__ = 'schedule'

    weeks = db.Column(db.Integer, nullable=False)
    days = db.Column(db.Integer, nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    minutes = db.Column(db.Integer, nullable=False)
    seconds = db.Column(db.Integer, nullable=False)
    last_triggered_at = db.Column(db.DateTime, nullable=False)

    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'), nullable=False)


class Rule(_CRUDMixin, db.Model):

    __tablename__ = 'rule'

    type = db.Column(db.Enum('XPATH', 'CSS'), nullable=False)
    path = db.Column(db.String(32), nullable=False)
    position = db.Column(db.Integer, nullable=False)

    source_id = db.Column(db.Integer, db.ForeignKey('source.id'),
                          nullable=False)


class Item(_CRUDMixin, db.Model):

    __tablename__ = 'item'

    item_id = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    title = db.Column(db.String(32), nullable=False)
    content = db.Column(db.Text, nullable=False)
    last_updated_at = db.Column(db.DateTime, nullable=False)
    last_crawled_at = db.Column(db.DateTime, nullable=False)

    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'), nullable=False)


class Feed(_CRUDMixin, db.Model):

    __tablename__ = 'feed'

    name = db.Column(db.String(32), nullable=False)
    url = db.Column(db.String(256), nullable=False)

    source_id = db.Column(db.Integer, db.ForeignKey('source.id'),
                          nullable=False)

    items = db.relationship(Item)
    rules = db.relationship(
        Rule,
        primaryjoin=(db.remote(source_id) == db.foreign(Rule.source_id)),
        order_by=Rule.position,
        collection_class=ordering_list('position'))
    schedule = db.relationship(
        Schedule, uselist=False,
        cascade='all, delete-orphan')


class Source(_CRUDMixin, db.Model):

    __tablename__ = 'source'

    name = db.Column(db.String(32), nullable=False)
    url = db.Column(db.String(256), nullable=False)

    feeds = db.relationship(Feed)
    rules = db.relationship(
        Rule, cascade='all, delete-orphan',
        order_by=Rule.position,
        collection_class=ordering_list('position'))
