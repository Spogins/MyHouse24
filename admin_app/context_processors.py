from django.shortcuts import redirect

from account.models import Profile
from admin_app.models import Role


def role_pass(request):
   
    try:
        profile = Profile.objects.get(user_id=request.user.id)
        role = Role.objects.get(name=profile.role)
        context = {
            'statistic': role.statistic,
            'cash_box': role.cash_box,
            'invoice': role.invoice,
            'personal_account': role.personal_account,
            'apartment': role.apartment,
            'owner': role.owner,
            'house': role.house,
            'message': role.message,
            'application': role.application,
            'meter': role.meter,
            'site_management': role.site_management,
            'service': role.service,
            'tariff': role.tariff,
            'role': role.role,
            'users': role.users,
            'requisites': role.requisites
        }
        return context
    except:
        return {}
