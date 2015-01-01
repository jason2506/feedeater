# -*- coding: utf-8 -*-

from celery import Celery
from sqlalchemy import engine_from_config

import configs
from feedeater import models

engine = engine_from_config(configs.SQLALCHEMY_ENGINE, prefix='')
models.bind_engine(engine)

app = Celery('feedeater')
app.config_from_object(configs)

if __name__ == '__main__':
    app.start()
