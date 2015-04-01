#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.script import Manager, prompt_bool

from feedeater import create_app
from feedeater.models import db

manager = Manager(create_app)


@manager.command
def initdb():
    '''Creates all database tables.'''
    db.create_all()


@manager.command
def dropdb():
    '''Drops all database tables.'''
    if prompt_bool('Are you sure to drop your databse?'):
        db.drop_all()


if __name__ == '__main__':
    manager.run()
