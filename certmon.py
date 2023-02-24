from app import app
import logging

if __name__ == '__main__':
    app.run(host="0.0.0.0")
else:
    gunicorn_logger = logging.getLogger('gunicorn.debug')
    app.logger.addHandler(gunicorn_logger)