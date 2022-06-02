import analitza_temps_lectura_directori
import analitza_temps_escriptura_directori
import time
from pathlib import Path
import csv
from datetime import datetime

paths = {
    'C':r"C:\temp\proves",
    'U':r"U:\QUOTA\Comu_imi\Becaris\proves-velocitat"
}

temps = 5


with open('C:/temp/qVista/cronometres/resultats.csv','w', newline='') as f:
    # headers = [(f'Lectura-{x}', f'Escriptura-{x}') for x in paths.keys()]
    headers = [f'{t}-{x}' for x in paths.keys() for t in ('Lectura','Escriptura')]
    csvFile = csv.DictWriter(f,['Moment', *headers])
    csvFile.writeheader()

    while True:
        d={'Moment':datetime.now()}
        for disc, path in paths.items():
            escriptura = analitza_temps_escriptura_directori.cronometra(path)
            lectura = analitza_temps_lectura_directori.cronometra(path)
            d[f'Lectura-{disc}']=lectura
            d[f'Escriptura-{disc}']=escriptura
            print(f'Lectura {disc}:',lectura)
            print(f'Escriptura {disc}:',escriptura)

        csvFile.writerow(d)
        f.flush()
        time.sleep(temps*60)