#!/bin/bash
echo "Building project..."
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 counseling_app/manage.py collectstatic --noinput --clear
