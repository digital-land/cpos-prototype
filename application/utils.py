from collections import Counter

def counter_to_tuples(counter):
    tuple_list = []
    for key in counter.keys():
        tuple_list.append( (key, counter[key]) )

    tuple_list.sort(key=lambda tup: tup[0])
    return tuple_list


def getStatuses(cpos):
    statuses = []
    for cpo in cpos:
        for s in cpo.statuses:
            statuses.append(s.status)

    return Counter(statuses)


def getYearCounts(cpos):
    years = []
    for cpo in cpos:
        years.append(cpo.start_date.year)

    return Counter(years)


def get_LA_counts(cpos):
    las = []
    for cpo in cpos:
        las.append(cpo.organisation)

    counts = Counter(las)
    return counts.most_common()
