import analitza_temps_lectura_directori
import analitza_temps_escriptura_directori
import time
from pathlib import Path
import csv
from datetime import datetime
try:
    import pythonping
    PING=True
except ModuleNotFoundError:
    print('Per tenir també els pings, instal·lar pythonping amb pip')
    PING=False

# rutes on farem l'escriptura de prova
paths = {
    'C':r"C:\temp\proves",
    'U':r"U:\QUOTA\Comu_imi\Becaris\proves-velocitat",
    'L':r"L:\DADES\SIT\PyQgis\Apl\qVista\Rendiment",
    'N':r"N:\SITEB\APL\PyQgis\qVista\Nueva carpeta\prova velocitat"
}

# ips dels directoris, per fer els pings
# no cal que siguin ips com a tal, amb que s'hi pugui fer ping és suficient
ips = {
    'U':'nas_imi',
    'L':'NAS_CORP.imi.bcn',
    'N':'NAS_CORP.imi.bcn'
}

temps = 5

dir = Path('C:/temp/qVista/cronometres/')
dir.mkdir(parents=True, exist_ok=True)
with open(Path(dir,'resultats.csv'),'w', newline='') as f:
    # headers = [(f'Lectura-{x}', f'Escriptura-{x}') for x in paths.keys()]
    headers = [f'{t}-{x}' for x in paths.keys() for t in ('Lectura','Escriptura','Ping')]
    csvFile = csv.DictWriter(f,['Moment', *headers])
    csvFile.writeheader()

    while True:
        d={'Moment':datetime.now()}
        for disc, path in paths.items():
            if PING and disc in ips:
                p = pythonping.ping(ips[disc]).rtt_avg
            else:
                p=None
            escriptura = analitza_temps_escriptura_directori.cronometra(path)
            lectura = analitza_temps_lectura_directori.cronometra(path)
            d[f'Lectura-{disc}']=lectura
            d[f'Escriptura-{disc}']=escriptura
            d[f'Ping-{disc}']=p if PING else ''
            print(f'Lectura {disc}:',lectura)
            print(f'Escriptura {disc}:',escriptura)
            print(f'Ping {disc}:', p)

        csvFile.writerow(d)
        f.flush()
        time.sleep(temps*60)