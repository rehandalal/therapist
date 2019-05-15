def parse_version(string):
    bits = str(string).split(".")
    while len(bits) < 3:
        bits.append(0)
    return [int(b) for b in bits[0:3]]


def version_compare(a, b):
    a = parse_version(a)
    b = parse_version(b)

    if a[0] > b[0]:
        return 1
    elif a[0] < b[0]:
        return -1
    elif a[1] > b[1]:
        return 1
    elif a[1] < b[1]:
        return -1
    elif a[2] > b[2]:
        return 1
    elif a[2] < b[2]:
        return -1
    else:
        return 0
