#!/bin/bash
set -e
echo "Building project..."
pip3 install -r counseling_app/requirements.txt
python3 counseling_app/manage.py collectstatic --noinput --clear
