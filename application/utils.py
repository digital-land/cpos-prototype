from collections import Counter, OrderedDict

import requests


def counter_to_tuples(counter):
    tuple_list = []
    for key in counter.keys():
        tuple_list.append( (key, counter[key]) )

    tuple_list.sort(key=lambda tup: tup[0])
    return tuple_list


def get_statuses(cpos):
    statuses = []
    for cpo in cpos:
        for s in cpo.statuses:
            statuses.append(s.status)

    return Counter(statuses)


def get_latest_statuses(cpos):
    statuses = []
    for cpo in cpos:
        statuses.append(cpo.latest_status().status)

    return Counter(statuses).most_common()


def get_year_counts(cpos):
    years = []
    for cpo in cpos:
        years.append(cpo.start_date.year)

    return Counter(years)


def get_year_type_counts(cpos):
    years = {}
    for cpo in cpos:
        if cpo.start_date.year in years.keys():
            years[cpo.start_date.year].append(cpo)
        else:
            # if new year add to obj
            years[cpo.start_date.year] = []
            years[cpo.start_date.year].append(cpo)

    # want dict in year order
    years_sorted = OrderedDict()
    for year in sorted(years.keys()):
        years_sorted[year] = {
            "total": len(years[year]),
            "types": get_cpo_type_counts(years[year])
        }

    return years_sorted


def get_LA_counts(cpos):
    las = []
    for cpo in cpos:
        las.append(cpo.organisation)

    counts = Counter(las)
    return counts.most_common()


def get_cpo_type_counts(cpos):
    typs = []
    for cpo in cpos:
        typs.append(cpo.compulsory_purchase_order_type)

    counts = Counter(typs)
    return counts.most_common()


def has_investigation_counts(cpos):
    inv = []
    for cpo in cpos:
        if len(cpo.investigations) > 0:
            inv.append(True)
        else:
            inv.append(False)

    return Counter(inv)


def get_average_durations(cpos):
    from statistics import mean
    days_to_completion = []
    days_for_inquiry = []
    for cpo in cpos:
        if cpo.days_to_completion() is not None:
            days_to_completion.append(cpo.days_to_completion())
        if cpo.days_for_inquiry() is not None:
            days_for_inquiry.append(cpo.days_for_inquiry())

    averages = {}
    if days_to_completion:
        averages['average_days_to_process'] = round(mean(days_to_completion))
    if days_for_inquiry:
        averages['average_days_pins_inquiry'] = round(mean(days_for_inquiry))

    averages['longest'] = max(days_to_completion) 
    averages['shortest'] = min(days_to_completion) 

    return averages


def get_search_result(url, headers):
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    # result_count = data['hits']['total']['value']
    cpo_ids = set([])
    for hit in data['hits']['hits']:
        filename = hit['_source']['file']['filename']
        cpo_id = '/'.join(filename.split('_')[:-1])
        cpo_ids.add(cpo_id)
    return {'result_count': len(cpo_ids), 'cpo_ids': cpo_ids}
