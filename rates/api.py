import requests
from rates import db
from rates.model import Currancy_rates, Currancy, ratesSchema, Currancy_ratesSchema
from datetime import datetime
from datetime import timedelta
import json
import os

__api_key = "688a4ecad5e7d69ddf9f08b1"

def get_rate_history(currancy_code=None, date_from=None):

    rates = []

    if not Currancy_rates.query.filter(Currancy_rates.date == datetime.today().date()).first():
        get_external_rate()

    cur_id = Currancy.query.filter(Currancy.code == currancy_code).first()

    if cur_id or not currancy_code:

        rates = ratesSchema.dump(Currancy_rates.query. \
            filter(True if currancy_code is None else Currancy_rates.id_curr == cur_id.id). \
            filter(True if date_from is None else Currancy_rates.date >= datetime.strptime(date_from, '%Y-%m-%d').date()).\
            order_by(Currancy_rates.id_curr, Currancy_rates.date).all())
    else:
        if currancy_code:
            rate = get_external_rate(currancy_code)
            date = datetime(rate.date.year, rate.date.month, rate.date.day, 0, 0).strftime('%Y-%m-%d')
            rates = '{0}, {1}, {2}'.format(rate.rate, date, currancy_code)

    return rates

# заполнить справочник валют, которые нужно обновлять
def fillTableCurr():
        if not Currancy.query.filter(Currancy.code == 'UAH').first():
            cur = Currancy('UAH', 'Hryvnia', 'UKRAINE', 980)
            db.session.add(cur)
            db.session.commit()
        if not Currancy.query.filter(Currancy.code == 'RUR').first():
            cur = Currancy('RUR', 'Russian Ruble (befor 1998)', 'RUSSIAN FEDERATION (THE)', 810)
            db.session.add(cur)
            db.session.commit()
        if not Currancy.query.filter(Currancy.code == 'RUB').first():
            cur = Currancy('RUB', 'Russian Ruble', 'RUSSIAN FEDERATION (THE)', 643)
            db.session.add(cur)
            db.session.commit()
        if not Currancy.query.filter(Currancy.code == 'PLN').first():
            cur = Currancy('PLN', 'Zloty', 'POLAND', 985)
            db.session.add(cur)
            db.session.commit()
        if not Currancy.query.filter(Currancy.code == 'EUR').first():
            cur = Currancy('EUR', 'Euro', 'EUROPEAN UNION', 978)
            db.session.add(cur)
            db.session.commit()
        if not Currancy.query.filter(Currancy.code == 'CAD').first():
            cur = Currancy('CAD', 'Canadian Dollar', 'CANADA', 124)
            db.session.add(cur)
            db.session.commit()

# определить курс валют по внешней API
# Курсы для валют, которые сохранены в таблице Currancy, сохраняются
# в таблице Currancy_rates
# Т.к. кол-во бесплатных обращений к API ограничено, применяется кеш в предлах суток
def get_external_rate(code = None):

    # сформировать название файла с кешом
    cache_filename = get_filename_for_cache(date=datetime.now())

    # проверить кеш с курсом на дату
    conversion_rates = get_file_from_cache(cache_filename)

    ret_rate = []

    if len(conversion_rates) == 0:
        url = 'https://v6.exchangerate-api.com/v6/{0}/latest/USD'.format(__api_key)
        conversion_rates = get_rates_from_external_api( url, cache_filename)

    # все курсы на дату из внешнего API
    rates = conversion_rates.get('conversion_rates')

    # дата курса
    date = datetime.fromtimestamp(conversion_rates['time_last_update_unix'])

    # все валюты по справочнику Currancy, которые нужно обновлять
    currances = Currancy.query.all()

    if not code:
        # если валюту не передали обновляем курсы по всем из Currancy
        for curr in currances:
            if rates.__contains__(curr.code):
                # проверить наличтие курса на дату
                rate = Currancy_rates.query. \
                    filter(Currancy_rates.id_curr == curr.id). \
                    filter(Currancy_rates.date == date.date()).first()

                if not rate:
                    # еще нет курса на дату в справочнике курсов, значить добавить
                    rate = Currancy_rates(id_curr= curr.id, rate=rates.get(curr.code), date=date)
                    db.session.add(rate)
                else:
                    # уже есть курс на дату в справочнике курсов, значить обновить
                    rate.rate = rates.get(curr.code)

                db.session.commit()
    else:
        # найти переданный курс из списка, который вернул внешний API
        if rates.__contains__(code):
            cr = Currancy_rates(id_curr=None, rate=rates.get(code), date=date)
            ret_rate = cr

            curr = Currancy.query.filter(Currancy.code == code).first()
            if curr:
                # если валюту передали проверить, нужно ли ее обновлять
                ret_rate.id_curr = curr.id
                db.session.commit()
    return ret_rate

#заполнить таблицу курсов историей
def get_external_history_rate(days):

    # дата начала истории
    day_start = datetime.now().today() - timedelta(days=days)

    # дата окончания истории
    day_finish = datetime.now().today()-timedelta(days=1)

    # сформировать файл для кеша
    cache_filename = get_filename_for_cache_ft(date_from=day_start, date_to=day_finish)

    # open cache from file
    conversion_rates = get_file_from_cache(cache_filename)

    if len(conversion_rates) == 0:
        url = "https://api.apilayer.com/fixer/timeseries?start_date={0}&end_date={1}&base=USD&symbols=UAH,RUR,RUB,PLN,EUR,CAD"\
            .format(
            day_start.date(), day_finish.date())

        payload = {}
        headers = {
            "apikey": "u7QHuc8Pf6n5niDOLwLdoaVB9bcJlpvp"
        }

        # получить историю курсов по внешнему API
        response = requests.request("GET", url, headers=headers, data=payload)
        result = response.text
        conversion_rates = json.loads(result)

        # сохранить в кеш
        dump_to_json(cache_filename, conversion_rates)

    rates = conversion_rates.get('rates')

    # выгрузить все валюты, по которым нужно сохранить историю
    currances = Currancy.query.all()

    for date_str, rates in rates.items():
        for curr in currances:
            if rates.__contains__(curr.code):
                # если по валюте нужно сохранять курс в базу, делаем это
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                print(date, curr.code, rates[curr.code])

                # проверяем, есть ли уже такой курс в базе
                rate = Currancy_rates.query. \
                    filter(Currancy_rates.id_curr == curr.id). \
                    filter(Currancy_rates.date == date).first()

                if not rate:
                    # если курса нет, добавляем
                    rate = Currancy_rates(curr.id, rates.get(curr.code), date)
                    db.session.add(rate)
                else:
                    # если курс есть, обновляем
                    rate.rate = rates.get(curr.code)

                db.session.commit()

# Сохранение JSON <data> в файл <filename>
def dump_to_json(filename, data, **kwargs):
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('indent', 1)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, **kwargs)

# Загрузить и вернуть JSON <data> с файла <cache_filename>
def get_file_from_cache(cache_filename):
    conversion_rates = []
    if os.path.exists(cache_filename):
        with open(cache_filename, encoding='utf-8') as json_file:
            conversion_rates = json.load(json_file)
    return conversion_rates

# сформировать имя файла для кеша по дате
def get_filename_for_cache(date):
    return '{0}\\cache\\{1}.json'.format(os.getcwd(), date.date())

# сформировать имя файла для кеша по датам периода
def get_filename_for_cache_ft(date_from, date_to):
    return '{0}\\cache\\{1}_{2}.json'.format(os.getcwd(), date_from.date(), date_to.date())

# вернуть JSON с курсами, которые определили по внешенму API
def get_rates_from_external_api(url, cache_filename):

    # Making our request
    response = requests.get(url)

    # JSON object
    conversion_rates = response.json()

    # save cache into file
    dump_to_json(cache_filename, conversion_rates)

    return conversion_rates