# -*- coding: utf-8 -*-

from flask import Flask

from .models import db
from .views import module

__all__ = ('create_app',)


def _init_db(app):
    """Setup for Flask-SQLAlchemy."""
    db.app = app
    db.init_app(app)


def _init_jinja(app):
    """Setup for Jinja2."""
    pass


def _init_modules(app):
    """Setup for blueprints"""
    app.register_blueprint(module)


def create_app(name=None):
    """Create and initialize app."""
    if name is None:
        name = __name__

    app = Flask(name)
    app.config.from_object('config')

    _init_db(app)
    _init_jinja(app)
    _init_modules(app)

    return app
