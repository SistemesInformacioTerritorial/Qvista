"""
Model exported as python.
Name : Capa a Excel
Group : 
With QGIS : 34004
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingParameterMapLayer
import processing


class CapaAExcel(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile('arxiu_excel', 'Arxiu Excel', behavior=QgsProcessingParameterFile.File, fileFilter='Todos los archivos (*.*)', defaultValue='C:\\temp\\qVista\\dades\\output.xlsx'))
        self.addParameter(QgsProcessingParameterMapLayer('capa', 'Capa', defaultValue=None, types=[QgsProcessing.TypeVectorAnyGeometry,QgsProcessing.TypeVector]))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}

        # Exportar a hoja de cálculo
        alg_params = {
            'FORMATTED_VALUES': False,
            'LAYERS': parameters['capa'],
            'OUTPUT': parameters['arxiu_excel'],
            'OVERWRITE': True,
            'USE_ALIAS': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExportarAHojaDeClculo'] = processing.run('native:exporttospreadsheet', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Open file or URL
        alg_params = {
            'URL': outputs['ExportarAHojaDeClculo']['OUTPUT']
        }
        outputs['OpenFileOrUrl'] = processing.run('native:openurl', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'Capa a Excel'

    def displayName(self):
        return 'Capa a Excel'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return CapaAExcel()
