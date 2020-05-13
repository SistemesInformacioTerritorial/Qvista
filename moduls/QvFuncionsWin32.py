# -*- coding: utf-8 -*-

# Funciones y constantes que sólo se usan cuando qVista corre en win32

import win32con
import win32api
import win32file
import ctypes

DPI = 96


# Función que ajusta la escala de pantalla
def setDPIScaling(val: int = 2) -> None:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(val)
    except Exception as e:
        print(str(e))


# Función que activa el atributo de read-only de un fichero, si no lo está ya
def setReadOnlyFile(path: str) -> None:
    try:
        attr = win32api.GetFileAttributes(path)
        if attr & win32con.FILE_ATTRIBUTE_READONLY:
            return
        else:
            win32api.SetFileAttributes(path, win32con.FILE_ATTRIBUTE_READONLY)
    except Exception as e:
        print(str(e))
        return


# Función que dice si un disco es fijo (local) o no
def isDriveFixed(drive: str) -> bool:
    try:
        return (win32file.GetDriveType(drive + ':') == win32file.DRIVE_FIXED)
    except Exception as e:
        print(str(e))
        return False


# Función que retorna el nombre de usuario
def getUserName(login: str) -> str:
    try:
        GetUserNameEx = ctypes.windll.secur32.GetUserNameExW
        NameDisplay = 3

        size = ctypes.pointer(ctypes.c_ulong(0))
        GetUserNameEx(NameDisplay, None, size)

        nameBuffer = ctypes.create_unicode_buffer(size.contents.value)
        GetUserNameEx(NameDisplay, nameBuffer, size)
        return nameBuffer.value
    except Exception as e:
        print(str(e))
        return login
