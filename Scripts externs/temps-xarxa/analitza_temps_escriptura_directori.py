import os
import time
import sys
from pathlib import Path


def cronometra(path):
    t=time.time()
    for i in range(1000):
        with open(Path(path,f'{i}.txt'),'w') as f:
            f.write(str(i))
    return time.time()-t