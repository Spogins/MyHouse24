from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import JsonResponse

from account.models import Owner
from admin_app.models import House, Flat, BankBook, Receipt


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def house_search(request, page):
    if is_ajax(request):
        house_list = House.objects.filter()

        name = request.GET.get('columns[1][search][value]')
        address = request.GET.get('columns[2][search][value]')

        if name:
            house_list = house_list.filter(name=name)

        if address:
            house_list = house_list.filter(address=address)

        _list = []
        ct = 0
        for x in house_list.values('name', 'address', 'id'):
            ct += 1
            x['ct'] = ct
            _list.append(x)

        paginate = Paginator(_list, request.GET.get('length'))
        page = paginate.page(page)
    return JsonResponse({'draw': request.GET.get('draw'), "recordsTotal": House.objects.filter().count(), "recordsFiltered": house_list.count(), 'data': list(page.object_list)})


def owner_search(request, page):
    if is_ajax(request):
        owner_list = Owner.objects.filter()
        print(owner_list)
        _list = []

        identify = request.GET.get('columns[0][search][value]')
        fullname = request.GET.get('columns[1][search][value]')
        phone = request.GET.get('columns[2][search][value]')
        email = request.GET.get('columns[3][search][value]')
        house = request.GET.get('columns[4][search][value]')
        flat = request.GET.get('columns[5][search][value]')
        date = request.GET.get('columns[6][search][value]')
        status = request.GET.get('columns[7][search][value]')
        debt = request.GET.get('columns[8][search][value]')

        for owner in owner_list:
            if identify != '' and identify not in str(owner.identify):
                continue

            if fullname != '' and fullname not in owner.fullname().lower():
                continue

            if phone != '' and phone not in str(owner.phone):
                continue

            if email != '' and email not in owner.user.email:
                continue

            if date != '' and date not in owner.user.date_joined.strftime("%d.%m.%Y"):
                continue

            if status != '' and status != owner.status:
                continue

            if debt != '' and not owner.has_debt():
                continue

            res = {
                'identify': owner.identify,
                'fullname': owner.fullname(),
                'phone': owner.phone,
                'email': owner.user.email,
                'house': [],
                'flat': [],
                'date': owner.user.date_joined.strftime("%d.%m.%Y"),
                'status': owner.status,
                'debt': owner.has_debt(),
                'id': owner.user_id
            }

            try:
                _flats = Flat.objects.filter(owner_id=owner.user_id)
                for _flat in _flats:
                    if house != '' and house != str(_flat.house.id):
                        continue
                    if flat != '' and flat not in str(_flat.number):
                        continue
                    res['house'].append(f'<a href="/admin_app/detail_house/{_flat.house.id}">{_flat.house.name}</a>')
                    res['flat'].append([f'<a href="/admin_app/detail_flat/{_flat.id}">№{_flat.number}</a>', f'<a href="/admin_app/detail_flat/{_flat.id}">"ЖК {_flat.house.name}"</a><br>'])
                if len(res['house']) == 0 or len(res['flat']) == 0:
                    continue
                _list.append(res)
            except ObjectDoesNotExist:
                if house != '':
                    continue

                if flat != '':
                    continue

                _list.append(res)

        paginate = Paginator(_list, request.GET.get('length'))
        page = paginate.page(page)
    return JsonResponse({'draw': request.GET.get('draw'), "recordsTotal": Owner.objects.filter().count(),
                         "recordsFiltered": len(_list), 'data': list(page.object_list)})


def bankbook_search(request, page):

    bankbook_list = BankBook.objects.filter()
    _list = []

    _id = request.GET.get('columns[0][search][value]')
    status = request.GET.get('columns[1][search][value]')
    flat = request.GET.get('columns[2][search][value]')
    house = request.GET.get('columns[3][search][value]')
    section = request.GET.get('columns[4][search][value]')
    owner = request.GET.get('columns[5][search][value]')
    balance = request.GET.get('columns[6][search][value]')

    for bankbook in bankbook_list:
        _flat = bankbook.flat.number if bankbook.flat else ''
        _house = bankbook.flat.house.name if bankbook.flat else ''
        _section = bankbook.flat.section.name if bankbook.flat else ''
        try:
            _owner = bankbook.flat.owner.fullname()
        except:
            _owner = ''

        if _id != '' and _id not in str(bankbook.id):
            continue

        if status != '' and status != bankbook.status:
            continue

        if flat != '' and flat != str(_flat):
            continue

        if house != '' and House.objects.get(id=house).name != str(_house):
            continue

        if section != '' and section != _section:
            continue

        if owner != '' and owner != _owner:
            continue

        if balance != '' and balance == 'Нет долга' and bankbook.balance() < 0:
            continue

        if balance != '' and balance == 'Есть долг' and bankbook.balance() >= 0:
            continue

        res = {
            'id': bankbook.id,
            'status': bankbook.status,
            'flat': _flat,
            'house': _house,
            'section': _section,
            'owner': _owner,
            'balance': bankbook.balance()
        }
        _list.append(res)

    paginate = Paginator(_list, request.GET.get('length'))
    page = paginate.page(page)
    return JsonResponse({'draw': request.GET.get('draw'), "recordsTotal": BankBook.objects.filter().count(),
                         "recordsFiltered": len(_list), 'data': list(page.object_list)})


