import datetime as dt


def year(request):
    today_year = dt.datetime.now().year
    return {
        'year': today_year
    }