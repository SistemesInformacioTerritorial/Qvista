# -*- coding: utf-8 -*-

import qgis.core as qgCor

from moduls.QvApp import QvApp

class QvDigitizeContext:
    """Clase de manejo de algunas variables de proyecto y de capa de QGIS que influyen
    en el comportamiento de qVista.
    """
    
    @staticmethod
    def varClear(var):
        if var is not None:
            # Eliminar separadores y convertirlos en blancos
            for c in "\"'’,;":
                var = var.replace(c, " ")
            # Sustituir grupos de blancos por uno
            var = " ".join(var.split())
        return var

    @staticmethod
    def varList(var, type):
        try:
            return list(map(type, var.split(' ')))
        except:
            return None

    @staticmethod
    def selectAndScrollFeature(fid, layer, atributs):
        if atributs is not None:
            atributs.tabTaula(layer, True, fid)
        layer.selectByIds([fid])

    @staticmethod
    def testReadOnly(nom: str = 'qV_readOnly') -> bool:
        """Comprueba si un proyecto QGIS está en modo de sólo lectura para qVista.
        Esto es así si existe una variable de proyecto llamada 'qV_readOnly' con el valor True.

        Args:
            nom (str, optional): Nombre de variable. Defaults to 'qV_readOnly'.

        Returns:
            bool: True si el proyecto es de sólo lectura.
        """
        project = qgCor.QgsProject.instance()
        return qgCor.QgsExpressionContextUtils.projectScope(project).variable(nom) == 'True'

    @staticmethod
    def testUserEditable(layer: qgCor.QgsMapLayer, nom: str = 'qV_editable') -> bool:
        """Comprueba si una capa puede editarse desde qVista por un usuario determinado.
        Para que una capa pueda ser modificada, ha de ser de tipo vectorial. Además, es necesario definir en QGIS una
        variable de capa; esta puede contener una lista de los códigos de usuario que tienen permitida la edición,
        o bien un asterisco ('*') que significa que cualquier usuario puede modificarla, o bien un signo menos ('-') que
        indica que nadie puede modificarla. La variable solo actúa si está definida a nivel de capa.
        - La variable 'qV_editable' es para la edición total de la capa, gráfica y alfanumérica (altas, modificaciones y bajas)
        - La variable 'qV_editForm' es solo para la modificación de los atributos alfanuméricos de elementos ya existentes

        Args:
            layer (QgsMapLayer): Capa a testear.
            nom (str, optional): Nombre de variable. Defaults to 'qV_editable'.

        Returns:
            bool: True si el usuario de qVista puede modificar la capa.
        """
        def testVar(nom, scope):
            try:
                var = scope.variable(nom)
                var = QvDigitizeContext.varClear(var)
                if var is None or var == '': return None
                if var == '*': return True
                if var == '-': return False
                users = QvDigitizeContext.varList(var, str)
                if users is None: return False
                return any(QvApp().usuari in u.upper() for u in users)
            except Exception as e:
                print(str(e))
                return None

        ok = False
        try:
            if layer.type() != qgCor.QgsMapLayer.VectorLayer: return False
            scope = qgCor.QgsExpressionContextUtils.layerScope(layer)
            ok = testVar(nom, scope)
            if ok is None: ok = False
        except Exception as e:
            print(str(e))
        finally:
            return ok
