# -*- coding: utf-8 -*-

from flask import Flask
from sqlalchemy import engine_from_config

import configs
from feedeater import views, models

engine = engine_from_config(configs.SQLALCHEMY_ENGINE, prefix='')
models.bind_engine(engine)

app = Flask(__name__, static_folder=None)
app.config.from_object(configs)
app.register_blueprint(views.module)

if __name__ == '__main__':
    app.run(host='192.168.224.131')
