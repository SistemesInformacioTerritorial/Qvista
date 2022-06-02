import os
import time
import sys


def cronometra(path):
    t=time.time()
    for arxiu in os.scandir(path):
        if arxiu.name.endswith('.txt'):
            with open(arxiu,encoding='cp1252') as f:
                f.read()
    return time.time()-t