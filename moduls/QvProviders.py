# -*- coding: utf-8 -*-

from qgis.core import (QgsApplication, QgsProcessingProvider, QgsRuntimeProfiler,
                       QgsProcessingModelAlgorithm, QgsXmlUtils)
from qgis.PyQt.QtWidgets import QMessageBox
import os

class QvProjectProvider:
    # Copiado de ProjectProvider.py

    MODEL_DEFS = {}

    @staticmethod
    def readProject(doc):
        # Se obtiene la informacion del DOM del qgs al abrirlo
        QvProjectProvider.MODEL_DEFS = {}
        project_models_nodes = doc.elementsByTagName('projectModels')
        if project_models_nodes:
            project_models_node = project_models_nodes.at(0)
            model_nodes = project_models_node.childNodes()
            for n in range(model_nodes.count()):
                model_element = model_nodes.at(n).toElement()
                definition = QgsXmlUtils.readVariant(model_element)
                algorithm = QgsProcessingModelAlgorithm()
                if algorithm.loadVariant(definition):
                    QvProjectProvider.MODEL_DEFS[algorithm.name()] = definition

    @staticmethod
    def loadAlgorithms():
        # Se cargan los algoritmos en el momento de utilizarlos
        provProject = QgsApplication.processingRegistry().providerById('project')
        if provProject is not None:
            provProject.model_definitions = QvProjectProvider.MODEL_DEFS
            provProject.refreshAlgorithms()
            provProject.loadAlgorithms()
        return provProject


class QvQvistaProvider(QgsProcessingProvider):

    MODELS_FOLDER = str(os.path.join(os.getcwd(), r"processos\models"))

    def __init__(self):
        """
        Default constructor.
        """
        QgsProcessingProvider.__init__(self)
        self.algs = []
        self.isLoading = False

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        pass

    def loadFromFolder(self, folder):
        if not os.path.exists(folder):
            return
        for path, subdirs, files in os.walk(folder):
            for descriptionFile in files:
                if descriptionFile.endswith('model3'):
                    fullpath = os.path.join(path, descriptionFile)
                    alg = QgsProcessingModelAlgorithm()
                    if alg.fromFile(fullpath):
                        if alg.name():
                            alg.setSourceFilePath(fullpath)
                            self.algs.append(alg)
                    else:
                        QMessageBox.warning(None, f"No s'ha pogut carregar model {descriptionFile}",
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
            self.loadFromFolder(QvQvistaProvider.MODELS_FOLDER)
            for a in self.algs:
                self.addAlgorithm(a)
            self.isLoading = False

    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'qvista'

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return self.tr('Models qVista')

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
        return self.tr('Models disponibles a qVista')
