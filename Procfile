release: python counseling_app/manage.py migrate --noinput
web: gunicorn --bind 0.0.0.0:$PORT --chdir counseling_app counseling_app.wsgi:application
