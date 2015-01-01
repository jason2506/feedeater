# Celery
BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'amqp://'
CELERY_IGNORE_RESULT = False
CELERY_TIMEZONE = 'Asia/Taipei'
CELERY_IMPORTS = (
    'feedeater.tasks',
)

# SQLAlchemy
SQLALCHEMY_ENGINE = {
    'url': 'sqlite:///tmp.db',
    'echo': True
}
