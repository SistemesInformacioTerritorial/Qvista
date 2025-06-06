# -*- coding: utf-8 -*-

from qgis.PyQt.QtGui import QColor

ROTATION_FIELD = "Rotació"

VCAD_COLORS = []       # Tabla de 256 colores
VCAD_LINE_STYLES = []  # Tabla de 8 estilos de línea (en QGIS hay 5 predefinidos,
                       # aunque es posible usar un patrón de guiones personalizado)
VCAD_FILL_STYLES = []  # Tabla de 6 estilos de relleno
VCAD_SYMBOLS = {}      # Construcciones

VCAD_COLORS.append('255,255,255')  # Blanco 
VCAD_COLORS.append('0,0,0')        # Negro
VCAD_COLORS.append('255,0,0')      # Rojo
VCAD_COLORS.append('0,255,0')      # Verde
VCAD_COLORS.append('255,255,0')    # Amarillo
VCAD_COLORS.append('0,0,255')      # Azul
VCAD_COLORS.append('255,0,255')    # Magenta
VCAD_COLORS.append('0,255,255')    # Cian
VCAD_COLORS.append('233,233,233')  # Gris 10%
VCAD_COLORS.append('204,204,204')  # Gris 20%
VCAD_COLORS.append('178,178,178')  # Gris 30%
VCAD_COLORS.append('153,153,153')  # Gris 40%
VCAD_COLORS.append('127,127,127')  # Gris 50%
VCAD_COLORS.append('102,102,102')  # Gris 60%
VCAD_COLORS.append('77,77,77')     # Gris 70%
VCAD_COLORS.append('26,26,26')     # Gris 90%
VCAD_COLORS.append('245,0,0')
VCAD_COLORS.append('255,115,0')
VCAD_COLORS.append('255,168,0')
VCAD_COLORS.append('255,214,0')
VCAD_COLORS.append('245,245,0')
VCAD_COLORS.append('214,255,0')
VCAD_COLORS.append('168,255,0')
VCAD_COLORS.append('115,255,0')
VCAD_COLORS.append('0,245,0')
VCAD_COLORS.append('0,255,115')
VCAD_COLORS.append('0,255,168')
VCAD_COLORS.append('0,255,214')
VCAD_COLORS.append('0,245,245')
VCAD_COLORS.append('0,214,255')
VCAD_COLORS.append('0,168,255')
VCAD_COLORS.append('0,115,255')
VCAD_COLORS.append('0,0,245')
VCAD_COLORS.append('115,0,255')
VCAD_COLORS.append('168,0,255')
VCAD_COLORS.append('214,0,255')
VCAD_COLORS.append('245,0,245')
VCAD_COLORS.append('255,0,214')
VCAD_COLORS.append('255,0,168')
VCAD_COLORS.append('255,0,115')
VCAD_COLORS.append('230,0,0')
VCAD_COLORS.append('230,105,0')
VCAD_COLORS.append('230,153,0')
VCAD_COLORS.append('230,194,0')
VCAD_COLORS.append('230,230,0')
VCAD_COLORS.append('194,230,0')
VCAD_COLORS.append('153,230,0')
VCAD_COLORS.append('105,230,0')
VCAD_COLORS.append('0,230,0')
VCAD_COLORS.append('0,230,105')
VCAD_COLORS.append('0,230,153')
VCAD_COLORS.append('0,230,194')
VCAD_COLORS.append('0,230,230')
VCAD_COLORS.append('0,194,230')
VCAD_COLORS.append('0,153,230')
VCAD_COLORS.append('0,105,230')
VCAD_COLORS.append('0,0,230')
VCAD_COLORS.append('105,0,230')
VCAD_COLORS.append('153,0,230')
VCAD_COLORS.append('194,2,230')
VCAD_COLORS.append('230,0,230')
VCAD_COLORS.append('230,0,194')
VCAD_COLORS.append('230,0,153')
VCAD_COLORS.append('230,0,105')
VCAD_COLORS.append('205,0,0')
VCAD_COLORS.append('205,96,0')
VCAD_COLORS.append('205,137,0')
VCAD_COLORS.append('205,173,0')
VCAD_COLORS.append('205,205,0')
VCAD_COLORS.append('173,205,0')
VCAD_COLORS.append('137,205,0')
VCAD_COLORS.append('96,205,0')
VCAD_COLORS.append('0,205,0')
VCAD_COLORS.append('0,205,96')
VCAD_COLORS.append('0,205,137')
VCAD_COLORS.append('0,205,173')
VCAD_COLORS.append('0,205,205')
VCAD_COLORS.append('0,173,205')
VCAD_COLORS.append('0,137,205')
VCAD_COLORS.append('0,96,205')
VCAD_COLORS.append('0,0,205')
VCAD_COLORS.append('96,0,205')
VCAD_COLORS.append('137,0,205')
VCAD_COLORS.append('173,0,205')
VCAD_COLORS.append('205,0,205')
VCAD_COLORS.append('205,0,173')
VCAD_COLORS.append('205,0,137')
VCAD_COLORS.append('205,0,96')
VCAD_COLORS.append('168,0,0')
VCAD_COLORS.append('168,81,0')
VCAD_COLORS.append('168,115,0')
VCAD_COLORS.append('168,143,0')
VCAD_COLORS.append('168,168,0')
VCAD_COLORS.append('143,168,0')
VCAD_COLORS.append('115,168,0')
VCAD_COLORS.append('81,168,0')
VCAD_COLORS.append('0,168,0')
VCAD_COLORS.append('0,168,81')
VCAD_COLORS.append('0,168,115')
VCAD_COLORS.append('0,168,143')
VCAD_COLORS.append('0,168,168')
VCAD_COLORS.append('0,143,168')
VCAD_COLORS.append('0,115,168')
VCAD_COLORS.append('0,81,168')
VCAD_COLORS.append('0,0,168')
VCAD_COLORS.append('81,0,168')
VCAD_COLORS.append('115,0,168')
VCAD_COLORS.append('143,0,168')
VCAD_COLORS.append('168,0,168')
VCAD_COLORS.append('168,0,143')
VCAD_COLORS.append('168,0,115')
VCAD_COLORS.append('168,0,81')
VCAD_COLORS.append('126,0,0')
VCAD_COLORS.append('126,65,0')
VCAD_COLORS.append('126,89,0')
VCAD_COLORS.append('126,109,0')
VCAD_COLORS.append('126,126,0')
VCAD_COLORS.append('109,126,0')
VCAD_COLORS.append('89,126,0')
VCAD_COLORS.append('65,126,0')
VCAD_COLORS.append('0,126,0')
VCAD_COLORS.append('0,126,65')
VCAD_COLORS.append('0,126,89')
VCAD_COLORS.append('0,126,109')
VCAD_COLORS.append('0,126,126')
VCAD_COLORS.append('0,109,126')
VCAD_COLORS.append('0,89,126')
VCAD_COLORS.append('0,65,126')
VCAD_COLORS.append('0,0,126')
VCAD_COLORS.append('65,0,126')
VCAD_COLORS.append('89,0,126')
VCAD_COLORS.append('109,0,126')
VCAD_COLORS.append('126,0,126')
VCAD_COLORS.append('126,0,109')
VCAD_COLORS.append('126,0,89')
VCAD_COLORS.append('126,0,65')
VCAD_COLORS.append('255,168,168')
VCAD_COLORS.append('255,192,168')
VCAD_COLORS.append('255,214,168')
VCAD_COLORS.append('255,235,168')
VCAD_COLORS.append('255,255,168')
VCAD_COLORS.append('235,255,168')
VCAD_COLORS.append('214,255,168')
VCAD_COLORS.append('192,255,168')
VCAD_COLORS.append('168,255,168')
VCAD_COLORS.append('168,255,192')
VCAD_COLORS.append('168,255,214')
VCAD_COLORS.append('168,255,235')
VCAD_COLORS.append('168,255,255')
VCAD_COLORS.append('168,235,255')
VCAD_COLORS.append('168,214,255')
VCAD_COLORS.append('168,192,255')
VCAD_COLORS.append('168,168,255')
VCAD_COLORS.append('192,168,255')
VCAD_COLORS.append('214,168,255')
VCAD_COLORS.append('235,168,255')
VCAD_COLORS.append('255,168,255')
VCAD_COLORS.append('255,168,235')
VCAD_COLORS.append('255,168,214')
VCAD_COLORS.append('255,168,192')
VCAD_COLORS.append('230,153,153')
VCAD_COLORS.append('230,174,153')
VCAD_COLORS.append('230,190,153')
VCAD_COLORS.append('230,212,153')
VCAD_COLORS.append('230,230,153')
VCAD_COLORS.append('212,230,153')
VCAD_COLORS.append('194,230,153')
VCAD_COLORS.append('174,230,153')
VCAD_COLORS.append('153,230,153')
VCAD_COLORS.append('153,230,174')
VCAD_COLORS.append('153,230,194')
VCAD_COLORS.append('153,230,212')
VCAD_COLORS.append('153,230,230')
VCAD_COLORS.append('153,212,230')
VCAD_COLORS.append('153,194,230')
VCAD_COLORS.append('153,174,230')
VCAD_COLORS.append('153,153,230')
VCAD_COLORS.append('174,153,230')
VCAD_COLORS.append('194,153,230')
VCAD_COLORS.append('212,153,230')
VCAD_COLORS.append('230,153,230')
VCAD_COLORS.append('230,153,212')
VCAD_COLORS.append('230,153,194')
VCAD_COLORS.append('230,153,174')
VCAD_COLORS.append('205,137,137')
VCAD_COLORS.append('205,156,137')
VCAD_COLORS.append('205,173,137')
VCAD_COLORS.append('205,190,137')
VCAD_COLORS.append('205,205,137')
VCAD_COLORS.append('190,205,137')
VCAD_COLORS.append('173,205,137')
VCAD_COLORS.append('156,205,137')
VCAD_COLORS.append('137,205,137')
VCAD_COLORS.append('137,205,156')
VCAD_COLORS.append('137,205,173')
VCAD_COLORS.append('137,205,190')
VCAD_COLORS.append('137,205,205')
VCAD_COLORS.append('137,190,205')
VCAD_COLORS.append('137,173,205')
VCAD_COLORS.append('137,156,205')
VCAD_COLORS.append('137,137,205')
VCAD_COLORS.append('156,137,205')
VCAD_COLORS.append('173,137,205')
VCAD_COLORS.append('190,137,205')
VCAD_COLORS.append('205,137,205')
VCAD_COLORS.append('205,137,190')
VCAD_COLORS.append('205,137,173')
VCAD_COLORS.append('205,137,156')
VCAD_COLORS.append('168,115,115')
VCAD_COLORS.append('168,129,115')
VCAD_COLORS.append('168,143,115')
VCAD_COLORS.append('168,156,115')
VCAD_COLORS.append('168,168,115')
VCAD_COLORS.append('156,168,115')
VCAD_COLORS.append('143,168,115')
VCAD_COLORS.append('129,168,115')
VCAD_COLORS.append('115,168,115')
VCAD_COLORS.append('115,168,129')
VCAD_COLORS.append('115,168,143')
VCAD_COLORS.append('115,168,156')
VCAD_COLORS.append('115,168,168')
VCAD_COLORS.append('115,156,168')
VCAD_COLORS.append('115,143,168')
VCAD_COLORS.append('115,129,168')
VCAD_COLORS.append('115,115,168')
VCAD_COLORS.append('129,115,168')
VCAD_COLORS.append('143,115,168')
VCAD_COLORS.append('156,115,168')
VCAD_COLORS.append('168,115,168')
VCAD_COLORS.append('168,115,156')
VCAD_COLORS.append('168,115,143')
VCAD_COLORS.append('168,115,129')
VCAD_COLORS.append('126,89,89')
VCAD_COLORS.append('126,99,89')
VCAD_COLORS.append('126,109,89')
VCAD_COLORS.append('126,117,89')
VCAD_COLORS.append('126,126,89')
VCAD_COLORS.append('117,126,89')
VCAD_COLORS.append('109,126,89')
VCAD_COLORS.append('99,126,89')
VCAD_COLORS.append('89,126,89')
VCAD_COLORS.append('89,126,99')
VCAD_COLORS.append('89,126,109')
VCAD_COLORS.append('89,126,117')
VCAD_COLORS.append('89,126,126')
VCAD_COLORS.append('89,117,126')
VCAD_COLORS.append('89,109,126')
VCAD_COLORS.append('89,99,126')
VCAD_COLORS.append('89,89,126')
VCAD_COLORS.append('99,89,126')
VCAD_COLORS.append('109,89,126')
VCAD_COLORS.append('117,89,126')
VCAD_COLORS.append('126,89,126')
VCAD_COLORS.append('126,89,117')
VCAD_COLORS.append('126,89,109')
VCAD_COLORS.append('126,89,99')

VCAD_LINE_STYLES.append("solid")
VCAD_LINE_STYLES.append("dot")
VCAD_LINE_STYLES.append("dash")
VCAD_LINE_STYLES.append("dash")
VCAD_LINE_STYLES.append("dot")
VCAD_LINE_STYLES.append("dash")
VCAD_LINE_STYLES.append("dash dot dot")
VCAD_LINE_STYLES.append("dash dot")

VCAD_FILL_STYLES.append("solid")
VCAD_FILL_STYLES.append("horizontal")
VCAD_FILL_STYLES.append("vertical")
VCAD_FILL_STYLES.append("f_diagonal")
VCAD_FILL_STYLES.append("b_diagonal")
VCAD_FILL_STYLES.append("cross")
VCAD_FILL_STYLES.append("diagonal_x")

VCAD_SYMBOLS['Cap de Fletxa'] = {
    'angle': '-90', 'color': '0,0,160,255', 'horizontal_anchor_point': '1', 'joinstyle': 'bevel', 'name': 'filled_arrowhead', 'offset': '0,0', 
    'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'outline_color': '0,0,160,255', 
    'outline_style': 'no', 'outline_width': '0', 'outline_width_map_unit_scale': '3x:0,0,0,0,0,0', 'outline_width_unit': 'MM', 
    'scale_method': 'diameter', 'size': '4', 'size_map_unit_scale': '3x:0,0,0,0,0,0', 'size_unit': 'MM', 'vertical_anchor_point': '1'
}

if __name__ == "__main__":

    print(f"# Colors: {len(VCAD_COLORS)}")
    print(f"# Line styles: {len(VCAD_LINE_STYLES)}")
    print(f"# Symbols: {len(VCAD_SYMBOLS)}")