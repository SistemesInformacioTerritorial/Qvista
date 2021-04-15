# -*- coding: utf-8 -*-

import qgis.core as qgCor
import qgis.gui as qgGui
import qgis.utils as qgUts
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui
import qgis.PyQt.QtCore as qtCor

import requests
import pathlib
from zipfile import ZipFile

# Servicios Web FME: https://docs.safe.com/fme/html/FME_Server_Documentation/ReferenceManual/FME_Server_Web_Services.htm

DIR_TEMP = "D:/Temp"
FILE_TOKEN = "D:/qVista/Token.txt"

FMW_PARAMS = dict()
FMW_PARAMS['Layers qVista/ZonesAdmGpkg.fmw'] = {
    'name': 'ZonesAdm',
    'desc': 'Zones Administratives',
    'params': 'ORACLE_SPATIAL=QVISTA_CONS&TEMPLATE_GEOPACKAGE=$(FME_SHAREDRESOURCE_DATA)/qVista/ZonesAdmBase.gpkg',
    'group': 'Yes'
}

class QvFMEServer:

    def __init__(self, repository, workspace, server="http://pcias056.imi.bcn"):
        self.iniServer(server)
        self.iniJob(repository, workspace)

    def iniServer(self, server=None):
        if server is not None:
            self.server = server
            try: 
                with open(FILE_TOKEN, 'r') as f:
                    self.token = f.read()
            except:
                self.token = ''

    def iniJob(self, repository=None, workspace=None):
        if repository is not None:
            self.repository = repository
        if workspace is not None:
            self.workspace = workspace
        self.fmw = self.repository + '/' + self.workspace
        self.jobId = -1
        self.jobStatus = ''

    def fmwInfo(self, name):
        try:
            return FMW_PARAMS[self.fmw][name]
        except:
            return ''

    def header(self, accept=False, token=True):
        res = dict()
        res['Content-Type'] = 'application/json; charset=UTF-8'
        if accept:
            res['Accept'] = 'application/json'
        if token:
            res['Authorization'] = f"fmetoken token={self.token}"
        return res

    def infoServer(self):
        url = f"{self.server}/fmerest/v3/info"
        r = requests.get(url, headers=self.header())
        if  r.status_code == 200: # Ok
            resp = r.json()
            qtWdg.QMessageBox.information(None, 'FME Server', f"Versió: {resp['build']}")
        else:
            qtWdg.QMessageBox.critical(None, 'FME Server', f"Error: {r.status_code}")

    def jobServer(self):
        if self.jobId < 0:
            self.dataService()
        else:
            self.dataDownload()

    def msgService(self, r):
        try:
            resp = r.json()
            # Ejemplo: 'serviceResponse': {'statusInfo': {'message': 'Invalid service mode: kkasync', 'mode': 'kkasync', 'status': 'failure'}}
            return resp['serviceResponse']['statusInfo']['message']
        except:
            return None

    def dataService(self):
        self.iniJob()
        url = f"{self.server}/fmedatadownload/{self.fmw}" \
              f"/?opt_servicemode=async&opt_responseformat=json&{self.fmwInfo('params')}" 
        r = requests.get(url, headers=self.header())
        if r.status_code == 200: # OK
            resp = r.json()
            # Ejemplo: 'serviceResponse': {'jobID': 11966, 'statusInfo': {'mode': 'async', 'status': 'success'}}
            self.jobId = int(resp['serviceResponse']['jobID'])
            qtWdg.QMessageBox.information(None, 'Petició enviada', f"ID: {self.jobId}\nNom: {self.fmwInfo('desc')}")
        else:
            error = self.msgService(r)
            if error is None:
                msg = ''
            else:
                msg = f"\nMissatge: {error}"
            qtWdg.QMessageBox.warning(None, 'Atenció', f"Petició rebutjada\nEstat: {r.status_code}{msg}")

    # def submit(self):
    #     self.iniJob()
    #     url = f"{self.server}/fmerest/v3/transformations/submit/{self.fmw}"
    #     params = {
    #         "publishedParameters": [
    #             {
    #             "name": "ORACLE_SPATIAL",
    #             "value": "QVISTA_CONS"
    #             },
    #             {
    #             "name": "TEMPLATE_GEOPACKAGE",
    #             "value": "$(FME_SHAREDRESOURCE_DATA)/qVista/ZonesAdmBase.gpkg"
    #             },
    #             {
    #             "name": "OUTPUT_GEOPACKAGE",
    #             "value": "$(FME_SHAREDRESOURCE_DATA)/qVista/ZonesAdm.gpkg"
    #             }
    #         ]
    #     }
    #     r = requests.post(url, json=params, headers=self.header(accept=True))
    #     resp = r.json()
    #     if r.status_code == 202: # OK
    #         self.jobId = int(resp['id'])
    #         self.jobName = jobName
    #         qtWdg.QMessageBox.information(None, 'Petició enviada', f"ID: {self.jobId}, Nom: {self.jobName}")
    #     else:
    #         qtWdg.QMessageBox.warning(None, 'Atenció', f"Petició rebutjada\nEstat: {r.status_code}\nMissatge: {resp.get('message', '-')}")

    def dataDownload(self):
        url = f"{self.server}/fmerest/v3/transformations/jobs/id/{self.jobId}"
        r = requests.get(url, headers=self.header())
        if r.status_code == 200: # Ok
            resp = r.json()
            self.jobStatus = resp['status']
            if self.jobStatus =='SUCCESS':
                name = self.fmwInfo('name')
                dirZip = pathlib.Path(DIR_TEMP)
                fZip = pathlib.Path(dirZip, name).with_suffix('.zip')
                fGpkg = pathlib.Path(dirZip, name, name).with_suffix('.gpkg')
                urlZip = resp['result']['resultDatasetDownloadUrl']
                r = requests.get(urlZip, stream=True)
                if r.status_code == 200: # Ok
                    print('Tamaño fichero ' + urlZip + ':', r.headers['content-length'])
                    # Descarga Zip
                    with open(fZip, 'wb') as zip:
                        for chunk in r.iter_content(chunk_size=256):
                            zip.write(chunk)
                    # Extracción Zip
                    with ZipFile(fZip, 'r') as zip:
                        zip.printdir()
                        zip.extractall(path=dirZip)
                    # Visualización capas
                    gpkg = qgCor.QgsVectorLayer(str(fGpkg), name, "ogr")
                    layersGpkg = [x.split('!!::!!')[1] for x in gpkg.dataProvider().subLayers()]
                    if self.fmwInfo('group') == 'Yes':
                        grupo = qgCor.QgsProject.instance().layerTreeRoot().addGroup(self.fmwInfo('desc'))
                        for item in layersGpkg:
                            layer = qgCor.QgsVectorLayer(f"{fGpkg}|layername={item}", item, 'ogr')
                            qgCor.QgsProject.instance().addMapLayer(layer, False)
                            grupo.addLayer(layer)
                    else:
                        layers = [qgCor.QgsVectorLayer(f"{fGpkg}|layername={layer}", layer, 'ogr') for layer in layersGpkg]
                        qgCor.QgsProject.instance().addMapLayers(layers)
                    self.iniJob()
                else:
                    qtWdg.QMessageBox.warning(None, 'Atenció', f"Descàrrega rebutjada\nEstat: {r.status_code}")
            elif self.jobStatus in ('ABORTED', 'FME_FAILURE', 'JOB_FAILURE'):
                qtWdg.QMessageBox.warning(None, 'Petició fallida', f"ID: {self.jobId}\nNom: {self.fmwInfo('desc')}\nEstat: {self.jobStatus}")
                self.iniJob()
            else: 
                qtWdg.QMessageBox.information(None, 'Petició en procés', f"ID: {self.jobId}\nNom: {self.fmwInfo('desc')}\nEstat: {self.jobStatus}")

if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    from moduls.QvApp import QvApp
    from moduls.QvCanvas import QvCanvas
    from moduls.QvAtributs import QvAtributs
    from moduls.QvLlegenda import QvLlegenda
    import configuracioQvista as cfg

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')

        canvas = QvCanvas()
        atributos = QvAtributs(canvas)
        leyenda = QvLlegenda(canvas, atributos)

        inicial = cfg.projecteInicial
        leyenda.readProject(inicial)

        leyenda.setWindowTitle('Llegenda')
        leyenda.setGeometry(100, 50, 400, 600)
        leyenda.show()

        canvas.setWindowTitle('Canvas - ' + inicial)
        canvas.setGeometry(510, 50, 900, 600)
        canvas.show()

        atributos.setWindowTitle('Atributs')
        atributos.setGeometry(100, 700, 1310, 300)
        leyenda.obertaTaulaAtributs.connect(atributos.show)

        # Adaptación del menú

        fme = QvFMEServer("Layers qVista", "ZonesAdmGpkg.fmw")
        # fme.jobId = 11990

        act = qtWdg.QAction()
        act.setText("FME-SERVER - Informació")
        act.triggered.connect(fme.infoServer)
        leyenda.accions.afegirAccio('infoServer', act)

        act = qtWdg.QAction()
        act.setText("FME-SERVER - Petició " + fme.fmwInfo('desc'))
        act.triggered.connect(fme.jobServer)
        leyenda.accions.afegirAccio('jobServer', act)

        def menuContexte(tipo):
            if tipo == 'none':
                leyenda.menuAccions.append('separator')
                leyenda.menuAccions.append('infoServer')
                leyenda.menuAccions.append('jobServer')

        # Conexión de la señal con la función menuContexte para personalizar el menú

        leyenda.clicatMenuContexte.connect(menuContexte)
