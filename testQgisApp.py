# -*- coding: utf-8 -*-

import os
from qgis.core import QgsApplication, QgsProviderRegistry

if __name__ == "__main__":

    # qgisPath = r"C:\OSGeo4W\apps\qgis-ltr"
    userPath = os.path.join(os.getenv('APPDATA'), r"QGIS\QGIS3\profiles\default")
    # QgsApplication.setPrefixPath(qgisPath, True)
    qgs = QgsApplication([], True, userPath)
    qgs.initQgis()
    print("providers: ", QgsProviderRegistry.instance().providerList())
    qgs.exitQgis()