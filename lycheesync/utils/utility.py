import time
import random


def getUniqTimeBasedId():
    # Compute Photo ID
    id = str(int(time.time()))
    # not precise enough
    length = len(id)
    if length < 14:
        missing_char = 14 - length
        r = random.random()
        r = str(r)
        # last missing_char char
        filler = r[-missing_char:]
        id = id + filler
    return id
