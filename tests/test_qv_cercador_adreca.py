from moduls.QVCercadorAdreca import comenca
def test_input_parentesis():
    comenca("balm (", 'carrer dels llebrencs  000102                                                  \x1e')
    comenca("balm \\", 'carrer dels llebrencs  000102                                                  \x1e')
