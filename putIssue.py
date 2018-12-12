import os
import json
import requests


USUARI = 'IMIJCA'
REPOSITORI = 'Qvista'
PASSWORD = 'qVista123'

def reportarProblema(titol, descripcio=None, labels=None):
    '''Crea un "issue" a github'''

    # url per crear issues
    url = 'https://api.github.com/repos/%s/%s/issues' % (USUARI, REPOSITORI)

    # Creem una sessió
    session = requests.Session()
    session.auth = (USUARI, PASSWORD)

    # creem el problema
    problema = {"title": titol,
            "body": descripcio}

    # Afegim el problema
    r = session.post(url, json.dumps(problema))

    if r.status_code == 201:
        print ('Creat el problema {0:s}'.format(titol))
    else:
        print ('Error al crear el problema {0:s}'.format(titol))
        print ('Response:', r.content)
