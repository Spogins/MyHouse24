from admin_app.management.commands import *
import subprocess

admin = 'python manage.py set_superadmin'
service = 'python manage.py set_service_page'
main = 'python manage.py set_main_page'
info = 'python manage.py set_info'
contact = 'python manage.py set_contact_page'
roles = 'python manage.py create_roles'
payment = 'python manage.py create_payment_details'

combined_command = admin + ' & ' + service + ' & ' + main + ' & ' + info + ' & ' + contact + ' & ' + roles + ' & ' + payment

subprocess.run(combined_command, shell=True)

