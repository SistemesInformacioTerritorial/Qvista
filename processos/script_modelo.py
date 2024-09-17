"""
Model exported as python.
Name : EmulacionPlugin
Group : Soroll
With QGIS : 32215
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Emulacionplugin(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterNumber('numpuntos', 'num puntos', type=QgsProcessingParameterNumber.Integer, defaultValue=100))
        self.addParameter(QgsProcessingParameterNumber('numpuntos (2)', 'Dist buff', type=QgsProcessingParameterNumber.Integer, defaultValue=100))
        self.addParameter(QgsProcessingParameterVectorLayer('zonasdeinteres', 'Capa puntual a Tratar', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Buffer', 'Buffer', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Buffer2', 'Buffer2', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('AgrupamientoDbscan', 'Agrupamiento DBSCAN', type=QgsProcessing.TypeVectorPoint, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('ExtraerPorAtributo', 'Extraer por atributo', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('SalidaFinal', 'salida final', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
        results = {}
        outputs = {}

        # Agrupamiento DBSCAN
        # hago agrupamientos
        alg_params = {
            'DBSCAN*': False,
            'EPS': parameters['numpuntos (2)'],
            'FIELD_NAME': 'CLUSTER_ID',
            'INPUT': parameters['zonasdeinteres'],
            'MIN_SIZE': parameters['numpuntos'],
            'SIZE_FIELD_NAME': 'CLUSTER_SIZE',
            'OUTPUT': parameters['AgrupamientoDbscan']
        }
        outputs['AgrupamientoDbscan'] = processing.run('native:dbscanclustering', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['AgrupamientoDbscan'] = outputs['AgrupamientoDbscan']['OUTPUT']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Extraer por atributo
        alg_params = {
            'FIELD': 'CLUSTER_ID',
            'INPUT': outputs['AgrupamientoDbscan']['OUTPUT'],
            'OPERATOR': 9,  # no es nulo
            'VALUE': '',
            'OUTPUT': parameters['ExtraerPorAtributo']
        }
        outputs['ExtraerPorAtributo'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['ExtraerPorAtributo'] = outputs['ExtraerPorAtributo']['OUTPUT']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': parameters['numpuntos (2)'],
            'END_CAP_STYLE': 0,  # Redondo
            'INPUT': outputs['ExtraerPorAtributo']['OUTPUT'],
            'JOIN_STYLE': 0,  # Redondo
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': parameters['Buffer']
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Buffer'] = outputs['Buffer']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Buffer2
        alg_params = {
            'DISSOLVE': True,
            'DISTANCE': 0,
            'END_CAP_STYLE': 0,  # Redondo
            'INPUT': outputs['Buffer']['OUTPUT'],
            'JOIN_STYLE': 0,  # Redondo
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': parameters['Buffer2']
        }
        outputs['Buffer2'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Buffer2'] = outputs['Buffer2']['OUTPUT']

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Multiparte a monoparte
        alg_params = {
            'INPUT': outputs['Buffer2']['OUTPUT'],
            'OUTPUT': parameters['SalidaFinal']
        }
        outputs['MultiparteAMonoparte'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['SalidaFinal'] = outputs['MultiparteAMonoparte']['OUTPUT']

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Seleccionar por expresión
        alg_params = {
            'EXPRESSION': 'fid',
            'INPUT': outputs['MultiparteAMonoparte']['OUTPUT'],
            'METHOD': 0,  # creando una nueva selección
        }
        outputs['SeleccionarPorExpresin'] = processing.run('qgis:selectbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'EmulacionPlugin'

    def displayName(self):
        return 'EmulacionPlugin'

    def group(self):
        return 'Soroll'

    def groupId(self):
        return 'Soroll'

    def createInstance(self):
        return Emulacionplugin()
