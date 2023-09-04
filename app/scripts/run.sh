#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate
# python manage.py test

# run uwsgi in :9000 as master with 4 workers
# enable multi- threading
# module to use in app.wsgi
uwsgi --socket :9000 --workers4 --master --enable-threads --module app.wsgi