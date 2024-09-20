# -*- coding: utf-8 -*-

from processos.soroll.soroll_processing import Areas

def soroll2_processing():
    from PyQt5.QtWidgets import QLineEdit
    try:
        area_id = "1"
        layer_name = "Mycellium"
        npun = QLineEdit("100")
        dis = QLineEdit("60")
        buf = QLineEdit("60")
        res = Areas(area_id, layer_name, npun, dis, buf)
        return res
    except Exception as e:
        print(str(e))
        return None
