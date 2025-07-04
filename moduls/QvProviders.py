# -*- coding: utf-8 -*-

from qgis.core import (QgsProcessingProvider, QgsRuntimeProfiler,
                       QgsProcessingModelAlgorithm)
from qgis.PyQt.QtWidgets import QMessageBox
import os

class QvModelProvider(QgsProcessingProvider):
    
    def __init__(self, name='models', extension='.model3', groups=None):
        """
        Default constructor.
        """
        QgsProcessingProvider.__init__(self)
        self.algs = []
        self.isLoading = False
        self.qvId = 'qv' + name.lower()
        self.qvName = name.lower().title()
        self.qvFolder = str(os.path.join(os.getcwd(), "processing", name.lower()))
        self.qvExtension = extension
        self.qvGroups = groups

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        pass

    def groupsFilter(self, alg):
        if self.qvGroups is None: return True
        algGroup = alg.group().strip().lower()
        if type(self.qvGroups) is str:
            return algGroup == self.qvGroups 
        if type(self.qvGroups) is list:
            if len(self.qvGroups) == 0: return True
            return algGroup in self.qvGroups
        return False

    def loadFromFolder(self):
        if not os.path.exists(self.qvFolder):
            return
        for path, subdirs, files in os.walk(self.qvFolder):
            for descriptionFile in files:
                if descriptionFile.endswith(self.qvExtension):
                    fullpath = os.path.join(path, descriptionFile)
                    alg = QgsProcessingModelAlgorithm()
                    if alg.fromFile(fullpath):
                        if alg.name() and self.groupsFilter(alg):
                            alg.setSourceFilePath(fullpath)
                            self.algs.append(alg)
                    else:
                        QMessageBox.warning(None, f"No s'ha pogut carregar {descriptionFile}",
                                            'Processos qVista')
                        # QgsMessageLog.logMessage(self.tr('Could not load model {0}',
                        #                          'ModelerAlgorithmProvider').format(descriptionFile),
                        #                          self.tr('Processing'), Qgis.Critical)

    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """
        with QgsRuntimeProfiler.profile('Load model algorithms'):
            if self.isLoading:
                return
            self.isLoading = True
            self.algs = []
            self.loadFromFolder()
            for a in self.algs:
                self.addAlgorithm(a)
            self.isLoading = False

    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return self.qvId

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return self.tr(self.qvName + ' qVista')

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QgsProcessingProvider.icon(self)

    def longName(self):
        """
        Returns the a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return self.tr(self.qvName + ' disponibles a qVista')

