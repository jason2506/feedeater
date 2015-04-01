# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms_alchemy import model_form_factory

from .models import db, Feed, Source


class _ModelForm(model_form_factory(Form)):

    get_session = db.create_scoped_session


class FeedForm(_ModelForm):

    class Meta:
        model = Feed


class SourceForm(_ModelForm):

    class Meta:
        model = Source
