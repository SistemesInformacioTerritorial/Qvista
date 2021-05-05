"""
Mòdul d'interpretació de les indicacions de rutes d'OSRM
"""

class QVStepsOSRM:
    ok = False
    indication_image_path = "null"
    indication_string = "null"
    #json és l'input de l'usuari

    def __init__(self, json):
        pass
        #per tractar per exemple la maniobra cal fer
        #if "maneuver" in json:
            #if "modifier" in json["maneuver"]:
                #var = json["maneuver"]["modifier"]