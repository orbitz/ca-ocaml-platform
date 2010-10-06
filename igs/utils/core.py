##
# Really core tiny functions

class StringNotFoundError(Exception):
    pass


def getStrBetween(haystack, start, end):
    sidx = haystack.find(start)
    if sidx < 0:
        raise StringNotFoundError('start: %s not found in %s' % (start, haystack))
    
    sidx += len(start)

    eidx = haystack[sidx:].find(end)
    
    if eidx < 0:
        raise StringNotFoundError('end: %s not found in %s' % (end, haystack))
    
    eidx += sidx
    return haystack[sidx:eidx]

