def quick_sort(x):
    if len(x) <= 1:
        return x
    pivot = x[len(x)//2]
    left,right,equal = [],[],[]
    for a in x:
        if a < pivot:
            left.append(a)
        elif a > pivot:
            right.append(a)
        else:
            equal.append(a)
    return quick_sort(left) + equal + quick_sort(right)