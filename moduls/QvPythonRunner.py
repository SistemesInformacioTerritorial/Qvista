# -*- coding: utf-8 -*-

from qgis.core import QgsPythonRunner


class QvPythonRunner(QgsPythonRunner):
    """Implementa la clase QgsPythonRunner para definir
       cómo se ejecuta Python en qVista
    """

    def __init__(self):
        """Constructor
        """
        super().__init__()

    def evalCommand(self, command):
        """Implementa el metodo eval en Python - No se ha probado

        Arguments:
            command (String) -- Expresión a evaluar

        Returns:
            Bool -- Ok o no
            String -- Resultado de la evaluación
        """
        try:
            exp = eval(command)
            return True, exp
        except:
            return False, None

    def runCommand(self, command, messageOnError=''):
        """Implementa el método exec en Python

        Arguments:
            command (String) -- Programa a ejecutar

        Keyword Arguments:
            messageOnError (String) -- No se usa (default: '')

        Returns:
            Bool -- Ok o no
        """
        try:
            exec(command, globals())
            return True
        except:
            return False
