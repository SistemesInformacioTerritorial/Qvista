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

    posicio_conduccio = ''
    nom_via = ''
    nom_rotonda = ''
    tipus_maniobra = ''
    direccio_maniobra = ''
    exit_rotonda = ''
    destinacions = ''

    indication_image_path = '' 
    indication_string = ''
    indicacioDireccioManiobra = ''
    indicacioTipusManiobra = ''



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

        if "destinations" in self.json:
            self.destinacions = self.json['destinations']

        if "maneuver" in self.json:
            if "modifier" in self.json["maneuver"]:
                self.tipus_maniobra = self.json['maneuver']['type']
                self.direccio_maniobra = self.json['maneuver']['modifier']
            if "exit" in self.json["maneuver"]:
                self.exit_rotonda = self.json["maneuver"]["exit"]   
    
    def switch_direccio_maniobra(self):
        switcherDireccio = {
            '':'',
            'uturn': "i faci un gir de 180 graus, per ",
            'sharp right': "pronunciadament a la dreta per ",
            'right': "a la dreta per ",
            'slight right': "lleugerament a la dreta per ",
            'sharp left': "pronunciadament a l'esquerra per ",
            'left': "a l'esquerra per ",
            'slight left': "lleugerament a l'esquerra per ",
            'straight': "recte per "
        }
        if self.direccio_maniobra in switcherDireccio:
            self.indicacioDireccioManiobra = switcherDireccio[self.direccio_maniobra]
        else:
            print("ERROR: " + self.direccio_maniobra)

    def switch_tipus_maniobra(self):
        switcherTipus = {
            '':'',
            'turn': "Giri " + self.indicacioDireccioManiobra,
            'new name': "Continuï "+ self.indicacioDireccioManiobra,
            'depart': "Surti "+ self.indicacioDireccioManiobra,
            'arrive': "Arribada al destí ",
            'merge': "Incorpori's a la via "+self.indicacioDireccioManiobra,
            'ramp': "DEPRECATED "+ self.indicacioDireccioManiobra,
            'on ramp': "Prengui l'entrada que es troba " + self.indicacioDireccioManiobra,
            'off ramp': "Prengui la sortida que es troba " + self.indicacioDireccioManiobra,
            'fork': "En la bifurcació giri " + self.indicacioDireccioManiobra,
            'end of road': "Al final de la via segueixi " + self.indicacioDireccioManiobra,
            'use lane': "Continuï recte per " + self.indicacioDireccioManiobra,
            'continue': "Segueixi " + self.indicacioDireccioManiobra,
            'roundabout': "roundabout",
            'rotary': "rotary",
            'roundabout turn': "Entri a ",
            'exit roundabout': "Surti de la rotonda en la " + str(self.exit_rotonda) + "a sortida cap a ",
            'exit rotary': "Surti de la rotonda en la " + str(self.exit_rotonda) + "a sortida cap a ",
            'notification': "Giri a " + self.indicacioDireccioManiobra
        }
        if self.tipus_maniobra in switcherTipus:
            self.indication_string = switcherTipus[self.tipus_maniobra]
            if self.tipus_maniobra == 'turn' and self.direccio_maniobra == 'straight':
                self.indication_string = "Segueixi recte per "
            if switcherTipus[self.tipus_maniobra] == 'roundabout' or switcherTipus[self.tipus_maniobra] == 'rotary':
                if self.exit_rotonda != '':
                    self.indication_string = "Surti de la rotonda per la sortida número " + str(self.exit_rotonda)
                if self.exit_rotonda == 'undefined':
                    self.indication_string = "Arribada al destí "
                else:
                    self.indication_string = "Entri a la rotonda i segueixi " + self.indicacioDireccioManiobra
        else:
            print("ERROR: " + self.tipus_maniobra)
            self.ok = False

        if self.nom_rotonda == '':
            self.indication_string = self.indication_string + self.nom_via
        else:
            self.indication_string = self.indication_string + self.nom_rotonda

        if self.nom_via == '':
            self.indication_string = self.indication_string.replace("per", "")
            self.indication_string = self.indication_string.replace("cap a", "")
        elif self.destinacions != '':
            self.indication_string = self.indication_string + " i segueixi les indicacions del cartell " + self.destinacions

        # print(self.indication_string)

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
        'straight': "Imatges/imgsOSRM/recte.png" ,
        'exit roundabout': "Imatges/imgsOSRM/exitrotonda.png",
        'exit rotary': "Imatges/imgsOSRM/exitrotonda.png"
        }
        if 'modifier' in self.json['maneuver']:
            if self.direccio_maniobra in switcherPath:
                self.indication_image_path = switcherPath[self.direccio_maniobra]
            if self.tipus_maniobra in switcherPath:
                self.indication_image_path = switcherPath[self.tipus_maniobra]
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

