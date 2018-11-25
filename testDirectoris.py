import os

contingutCarpetes = os.walk("C:\qvista\dades\CatalegProjectes")
for carpeta in contingutCarpetes:
        tema = carpeta[0][33:]
        projectes = []
        for fitxer in carpeta[2]:
            projectes.append(fitxer[0:-4])
        print (tema)
        print(set(projectes))