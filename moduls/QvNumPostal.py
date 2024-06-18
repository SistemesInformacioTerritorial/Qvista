# -*- coding: utf-8 -*-

import re

from moduls import QvFuncions

#  https://regex101.com/

_EXP_NUM = r"[0-9]+\s*[a-z|A-Z]?"  # expresión regular de número postal con o sin letra
_EXP_PNT = r"[K|k|E|e|S|s][0-9]+"  # expresion regular de punto kilométrico, entrada y salida

def separaString(txt: str, s: re.Match) -> tuple[str, str]:
    str1 = txt[0:s.span()[0]].strip()
    str2 = txt[s.span()[0]:].strip().lstrip(',')
    return str1, str2

def incluirGuion(nums: str) -> str:
    s = re.search(_EXP_NUM + "$", nums)
    if s:
        num1, num2 = separaString(nums, s)
        return num1 + '-' + num2
    else:
        return nums

# El orden es importante:
_EXP_LST = [
    (_EXP_PNT + "$", None),                             # 1 punto especial (Km, E/S) al final
    (_EXP_NUM + r"\s*\-+\s*" + _EXP_NUM + "$", None),   # 2 nums. al final (con o sin letra) separados por un guión
    (_EXP_NUM + r"\s+" + _EXP_NUM + "$", incluirGuion), # 2 nums. al final (con o sin letra) separados por espacios con funcion de añadir guión
    (_EXP_NUM + "$", None),                             # 1 número al final (con o sin letra)
]

def separaDireccion(direccion: str) -> tuple[str, str]:
    # Si la dirección viene en un solo campo, la separa en dos partes: nombre y numeros postales
    # - El nombre irá separado de los numeros por coma o espacio
    # - Si hay dos números (cada uno con sus digitos y una posible letra), estarán separados por guión o espacio
    nombre = txt = direccion.strip()
    nums = ''
    s = None
    f = None
    for r in _EXP_LST:
        s = re.search(r[0], txt)
        if s:
            f = r[1]
            break
    if s:
        nombre, nums = separaString(txt, s)
        if nombre != '' and nombre[-1] == ',':  # Eliminar coma separadora del final si la hay
            nombre = nombre[:-1].strip()
        if f: nums = f(nums)                    # Llamar a función extra si procede
        nums = nums.replace(' ', '')            # Eliminar espacios
    if QvFuncions.debugging(): print('***', nombre, '|', nums)
    return nombre, nums


if __name__ == "__main__":
    
    str = "calle de numancia, 85 89a"
    while (str != ''):
        nom, num = separaDireccion(str)
        str = ''
        pass

    from qgis.PyQt.QtCore import QRegularExpression

    for r in _EXP_LST:
        exp = r[0]
        regexp = QRegularExpression(exp)
        print('Exp:', exp, '- Valid:', regexp.isValid())
