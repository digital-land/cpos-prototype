from collections import Counter


def getStatuses(cpos):
    statuses = []
    for cpo in cpos:
        for s in cpo.statuses:
            statuses.append(s.status)

    return Counter(statuses)
