#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='160422733078@mjcollege.ac.in').exists() or User.objects.create_superuser('160422733078@mjcollege.ac.in', 'Admin@1234')" | python manage.py shell