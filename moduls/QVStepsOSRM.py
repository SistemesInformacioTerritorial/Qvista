"""
Mòdul d'interpretació de les indicacions de rutes d'OSRM. Funcionament:
step és una part del json de l'api d'OSRM. concretament un step individual, que conté interseccions, driving_side, geometry, distance, name, weight, maneuver i mode.
stepinfo = QVStepsOSRM(step)
if (stepinfo.ok):
    image_path = stepinfo.indication_image_path
    string = stepinfo.indication_string
"""
import pprint
import json
import os

class QVStepsOSRM:
    ok = True  # Si la indicació és prescindible 
    indication_image_path = "" 
    indication_string = ''
    posicio_conduccio = ''
    nom_via = ''
    nom_rotonda = ''
    tipus_maniobra = ''
    direccio_maniobra = ''
    exit_rotonda = ''

    def __init__(self, json):
        self.json = json
        self.processaJson()
        self.switch_direccio_maniobra()
        self.switch_tipus_maniobra()
        self.switch_path_imatge()

    def processaJson(self):

        if "driving_side" in self.json["intersections"]:
            self.posicio_conduccio = self.json['driving_side']

        if "name" in self.json: 
            self.nom_via = self.json['name']

        if "rotary_name" in self.json:
            self.nom_rotonda = self.json['rotary_name']

        if "maneuver" in self.json:
            if "modifier" in self.json["maneuver"]:
                self.tipus_maniobra = self.json['maneuver']['type']
                self.direccio_maniobra = self.json['maneuver']['modifier']
            if "exit" in self.json["maneuver"]:
                self.exit_rotonda = self.json["maneuver"]["exit"]   
    
    def switch_direccio_maniobra(self):
        switcherDireccio = {
            '':'?????????????????',
            'uturn': "faci un gir de 180 graus, per ",
            'sharp right': ", atenció, gir pronunciat a la dreta per ",
            'right': "dreta per ",
            'slight right': "lleugerament a la dreta per ",
            'sharp left': ", atenció, gir pronunciat a l'esquerra per ",
            'left': "esquerra per ",
            'slight left': "lleugerament a l'esquerra per ",
            'straight': "recte per "
        }
        if self.direccio_maniobra in switcherDireccio:
            self.direccio_maniobra = switcherDireccio[self.direccio_maniobra]
        else:
            print("ERROR: " + self.direccio_maniobra)
            raise

    def switch_tipus_maniobra(self):
        switcherTipus = {
            '':'?????????????????',
            'turn': "Giri cap a mà " + self.direccio_maniobra,
            'new name': "Continuï per "+ self.direccio_maniobra,
            'depart': "Surti per mà "+ self.direccio_maniobra,
            'arrive': "Arribada al destí "+ self.direccio_maniobra,
            'merge': "Incorpori's a la via "+self.direccio_maniobra,
            'ramp': "DEPRECATED "+ self.direccio_maniobra,
            'on ramp': "Prengui l'entrada en direccció " + self.direccio_maniobra,
            'off ramp': "Prengui la sortida en direccció " + self.direccio_maniobra,
            'fork': "Continuï per la bifurcació " + self.direccio_maniobra,
            'end of road': "Al final de la vía continuï en direcció " + self.direccio_maniobra,
            'use lane': "Continui recte per " + self.direccio_maniobra,
            'continue': "Mantingui's en la via " + self.direccio_maniobra,
            'roundabout': "roundabout",
            'rotary': "rotary",
            'roundabout turn': "Entri a la rotonda i giri a " + self.direccio_maniobra,
            'notification': "Giri a mà " + self.direccio_maniobra
        }
        if self.tipus_maniobra in switcherTipus:
            self.indication_string = switcherTipus[self.tipus_maniobra]
            if switcherTipus[self.tipus_maniobra] == 'roundabout' or switcherTipus[self.tipus_maniobra] == 'rotary':
                if self.exit_rotonda != '':
                    self.indication_string = "Surti de la rotonda per la sortida número " + str(self.exit_rotonda)
                if self.exit_rotonda == 'undefined':
                    self.indication_string = "Arribada al destí "
                else:
                    self.indication_string = "Entri a la rotonda i segueixi per mà " + self.direccio_maniobra
        else:
            print("ERROR: " + self.tipus_maniobra)
            self.ok = False

        if self.nom_rotonda == '':
            self.indication_string = self.indication_string + self.nom_via
        else:
            self.indication_string = self.indication_string + self.nom_rotonda

        print(self.indication_string)

    def switch_path_imatge(self):
        switcherPath = {
        '': "Imatges/imgsOSRM/default.png",
        'uturn': "Imatges/imgsOSRM/uturn.png",
        'sharp right': "Imatges/imgsOSRM/sharpdreta.png",
        'right': "Imatges/imgsOSRM/90dreta.png",
        'slight right': "Imatges/imgsOSRM/slightdreta",
        'sharp left': "Imatges/imgsOSRM/sharpesquerra.png",
        'left': "Imatges/imgsOSRM/90esquerra.png",
        'slight left': "Imatges/imgsOSRM/slightesquerra.png",
        'straight': "Imatges/imgsOSRM/recte.png" 
        }
        if 'modifier' in self.json['maneuver']:
            if self.json['maneuver']['modifier'] in switcherPath:
                self.indication_image_path = switcherPath[self.json['maneuver']['modifier']]
            # print(self.indication_image_path, json['maneuver']['modifier'])
        else:
            self.indication_image_path = switcherPath['straight']
        # else:
        #     print("ERROR: " + self.direccio_maniobra)
        #     raise

if __name__ == "__main__":
    
    testJsonPath = r"C:\Users\Patron\Desktop\teststep.json"                   
    with open(testJsonPath) as f:
        json = json.load(f)
    pp = pprint.PrettyPrinter(indent=3)
    # pp.pprint(myJson)

    traduccioSteps = QVStepsOSRM(json)



############################################################################
#  switch(direccio_maniobra){
#             case 'uturn':
#                 direccio_maniobra = "faci un gir de 180 graus, "
#             case 'sharp right':
#                 direccio_maniobra = ", atenció, gir pronunciat a la dreta"
#             case 'right':
#                 direccio_maniobra = "dreta "
#             case 'slight right':
#                 direccio_maniobra = "lleugerament a la dreta "
#             case 'sharp left':
#                 direccio_maniobra = ", atenció, gir pronunciat a l'esquerra"
#             case 'left':
#                 direccio_maniobra = "esquerra "
#             case 'slight left':
#                 direccio_maniobra = "lleugerament a l'esquerra "
#             case 'straight':
#                 direccio_maniobra = "recte "
#             default:
#                 indication_string = tipus_maniobra
#                 raise

#         switch(tipus_maniobra){
#             case 'turn':
#                 indication_string = "Giri cap a mà "
#             case 'new name':
#                 indication_string = "Continuï per "
#             case 'depart':
#                 indication_string = "Surti de "
#             case 'arrive':
#                 indication_string = "Arribada al destí "
#             case 'merge':
#                 indication_string = "Incorporis a la via "
#             case 'ramp':
#                 indication_string = "DEPRECATED "
#             case 'on ramp':
#                 indication_string = "Prengui l'entrada de l'autopista en direccció " + direccio_maniobra
#             case 'off ramp':
#                 indication_string = "Prengui la sortida de l'autopista en direccció " + direccio_maniobra
#             case 'fork':
#                 indication_string = "Continuï per la bifurcació " + 
#             case 'end of road':
#                 indication_string = "Al final de la vía continuï en direcció " + direccio_maniobra
#             case 'use lane':
#                 indication_string = "Continui recte per "
#             case 'continue':
#                 indication_string = "Mantinguis en la via "
#             case 'roundabout':
#                 if exit_rotonda != '':
#                     indication_string = "Surti de la rotonda per la sortida número " + str(exit)
#                 if exit_rotonda == 'undefined':
#                     indication_string = "Arribada al destí "
#                 else
#                     indication_string = "Entri a la rotonda i segueixi per mà " + direccio_maniobra
#             case 'rotatory':
#                 if exit_rotonda != '':
#                     indication_string = "Surti de la rotonda per la sortida número " + str(exit)
#                 if exit_rotonda == 'undefined':
#                     indication_string = "Arribada al destí "
#                 else
#                     indication_string = "Entri a la rotonda i segueixi per mà " + direccio_maniobra
#             case 'roundabout turn':
#                 indication_string = "Entri a la rotonda i giri a " + direccio_maniobra
#             case 'notification':
#                 indication_string = "Giri a mà " + direccio_maniobra
#             default: 
#                 indication_string = tipus_maniobra
#                 raise
#         }
#         if rotary_name == '':
#             indication_string = indication_string + nom_via
#         else:
#             indication_string = indication_string + nom_rotonda