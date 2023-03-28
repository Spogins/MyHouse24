from django.shortcuts import redirect

from admin_app.models import Flat


def owner_flats(request):
    try:
        flats = Flat.objects.filter(owner_id=request.user.id)
        print(flats)
        return {'flats': flats}
    except:
        return {}

