# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms_alchemy import model_form_factory

from . import models


class _ModelForm(model_form_factory(Form)):

    get_session = models.Session


class FeedForm(_ModelForm):

    class Meta:
        model = models.Feed


class SourceForm(_ModelForm):

    class Meta:
        model = models.Source
