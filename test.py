import datetime

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


start = datetime.time(21, 0, 0)
print(start)
end = datetime.time(7, 0, 0)
now = datetime.datetime.now().time().replace(hour=22)
print(time_in_range(start, end, now))