import time
import os
import sys
from datetime import datetime

temps = 1

if len(sys.argv)==2:
    try:
        temps = int(sys.argv[1])
    except:
        pass
os.chdir("../..")

while True:
    print('Comencem execució:',datetime.now())
    os.system(f'{sys.executable} qVista.py >nul 2>nul')
    print('Acabada execució')
    time.sleep(temps*60)