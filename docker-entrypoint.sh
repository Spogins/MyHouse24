#!/bin/sh

if [ "$DATABASE" = 'postgres' ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi
python manage.py collectstatic --no-input --clear
python manage.py makemigrations
python manage.py migrate
python manage.py set_superadmin
python manage.py create_roles
python manage.py create_payment_details
python manage.py set_main_page
python manage.py set_info
python manage.py set_service_page
python manage.py set_contact_page



exec "$@"