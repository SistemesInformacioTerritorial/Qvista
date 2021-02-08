# -*- coding: utf-8 -*-

from qgis.core import QgsExpressionContextUtils, QgsMapLayer, QgsProject

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
    def testReadOnly(project: QgsProject = QgsProject.instance(), nom: str = 'qV_readOnly') -> bool:
        """Comprueba si un proyecto QGIS está en modo de sólo lectura para qVista.
        Esto es así si existe una variable de proyecto llamada 'qV_readOnly' con el valor True.

        Args:
            project (QgsProject, optional): Instancia del proyecto. Defaults to QgsProject.instance().
            nom (str, optional): Nombre de variable. Defaults to 'qV_readOnly'.

        Returns:
            bool: True si el proyecto es de sólo lectura.
        """
        return QgsExpressionContextUtils.projectScope(project).variable(nom).upper() == 'TRUE'

    @staticmethod
    def testEditable(layer: QgsMapLayer, project: QgsProject = QgsProject.instance(), nom: str = 'qV_editable') -> bool:
        """Comprueba si una capa puede editarse desde qVista por un usuario determinado.
        Para que una capa pueda ser modificada, ha de ser vectorial y el proyecto que la incluye
        no puede estar en modo de sólo lectura. Además, tiene que haberse definido una variable
        de 'qV_editable'; esta puede contener una lista de los códigos de usuario que tienen permitida la edición,
        o bien un asterisco ('*') que significa que cualquier usuario puede modificarla, o bien un signo menos ('-') que
        indica que nadie puede modificarla. La variable puede estar definida a nivel de proyecto o de capa;
        tendrá preponderancia siempre la de capa a la de proyecto.

        Args:
            layer (QgsMapLayer): Capa a testear.
            nom (str, optional): Nombre de variable. Defaults to 'qV_editable'.

        Returns:
            bool: True si el usuario de qVista puede modificar la capa.
        """
        def testVar(nom, object, scope):
            try:
                var = scope(object).variable(nom)
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

        try:
            if layer.type() != QgsMapLayer.VectorLayer: return False
            if QvDigitizeContext.testReadOnly(): return False
            ok = testVar(nom, layer, QgsExpressionContextUtils.layerScope)
            if ok is None:
                ok = testVar(nom, project, QgsExpressionContextUtils.projectScope)
            if ok is None:
                return False
            else:
                return ok
        except Exception as e:
            print(str(e))
            return False



    
