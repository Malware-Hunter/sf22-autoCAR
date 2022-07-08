def rules_difference(list_a, list_b):
    a = set(map(tuple, list_a))
    b = set(map(tuple, list_b))
    list_d = a - b
    return list_d

def rules_intersection(list_a, list_b):
    a = set(map(tuple, list_a))
    b = set(map(tuple, list_b))
    list_i = a & b
    return list_i
