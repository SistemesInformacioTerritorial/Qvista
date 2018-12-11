import time
startGlobal = time.time()
import os
"""
Consideraciones:
    El fichero carreres.csv es fichero plano codificado como utf8 que procede de una extración oracle
    Cada vez que se actualice carrerer, deberá ejecutarse este programa
    El fichero carrerer.csv.old (copia de seguridad de la ultima ejecucion) actua como semaforo. Si existe no se ejecuta el programa. 
    Se evita asi que al reprocesar accidentalmente el fichero de calles varias veces, se incremente con variantes repetidas
    Si a pesar de todo se reprocesara carrerer.csv, debera eliminarse las lineas duplicadas (ultraedit > archivo > ordenar > opciones avanzadas > Eliminar duplicados)
    

Objetivo:
    Para facilitar la busqueda de calles con acentos, añadimos sus variantes sin acentos, aproximando la busqueda a una simplificación fonetica

Operativa:
    El proceso se realiza en una carpeta auxiliar "../Dades/DadesBCN/carrerer_tra/" que debe tener privilegios de escritura: 
    Deberá copiarse el fichero carrerer.csv en esta carpeta.
    Se generarara un nuevo fichero carrerer.csv,ampliado con estas variantes y el antiguo se renamea a carreres.csv.old

"""

carrerer_utf8="../Dades/DadesBCN/carrerer_tra/CARRERER.csv"
carrerer_8859="../Dades/DadesBCN/carrerer_tra/CARRERER.txt"
carrerer_utf8_conVariantes="../Dades/DadesBCN/carrerer_tra/CARRERER.csv_tmp"
carrerer_8859_conVariantes= "../Dades/DadesBCN/carrerer_tra/CARRERER_2.txt"



def correctSubtitleEncoding(filename, newFilename, encoding_from, encoding_to='UTF-8'):
    with open(filename, 'r', encoding=encoding_from) as fr:
        with open(newFilename, 'w', encoding=encoding_to) as fw:
            for line in fr:
                fw.write(line[:-1]+"\n")  


# El carrerer lo pasamos a iso-8859-11
correctSubtitleEncoding(carrerer_utf8, carrerer_8859, encoding_from='UTF-8', encoding_to='iso-8859-1')

# completamos el carrerer con las variantes sin acentos
with open(carrerer_8859, 'r') as fr:
     with open(carrerer_8859_conVariantes, 'w') as fw:
        for line in fr:
            line_original=line

            a,b = 'Àáàãéèëíìïóòõúùü','Aaaaeeeiiiooouuu'
            trans = str.maketrans(a,b)
            line1=line.translate(trans)

            if  line1 != line_original:
                fw.write(line1)
                
            fw.write(line_original)

# El carrerer lo pasamos a utf8
correctSubtitleEncoding(carrerer_8859_conVariantes, carrerer_utf8_conVariantes, encoding_from='iso-8859-1', encoding_to='UTF-8')


# Elimino ficheros temporales
if os.path.isfile(carrerer_8859_conVariantes): 
    os.remove(carrerer_8859_conVariantes)

if os.path.isfile(carrerer_8859): 
    os.remove(carrerer_8859)

# renombro el csv viejo
try:
    if os.path.isfile(carrerer_utf8): 
        oldbase = os.path.splitext(carrerer_utf8)
        newname = carrerer_utf8.replace('.csv', '.csv.old')
        output = os.rename(carrerer_utf8, newname)

    # renombro csv nuevo 
    if os.path.isfile(carrerer_utf8_conVariantes): 
        oldbase = os.path.splitext(carrerer_utf8_conVariantes)
        newname = carrerer_utf8_conVariantes.replace('.csv_tmp', '.csv')
        output = os.rename(carrerer_utf8_conVariantes, newname)
except:

    if os.path.isfile(carrerer_utf8_conVariantes): 
        os.remove(carrerer_utf8_conVariantes)

endGlobal = time.time()
tempsTotal = endGlobal - startGlobal
print ('Total carrega: ', tempsTotal)




