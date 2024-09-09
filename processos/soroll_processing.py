# -*- coding: utf-8 -*-

import os
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject, QgsVectorLayer
#  from qgis.core import *

try:
    from .processing import *    # qVista
except:
    from qgis import processing  # QGIS

def perform_dbscan_clustering(input_path, min_size, eps,  area_id):
    """
    Performs DBSCAN clustering on the specified layer.
    
    Parameters:
    - layer_name: Name of the layer to cluster.
    - npun: Minimum cluster size input.
    - dis: Epsilon distance input.
    - buf: Buffer distance input.
    - area_id: ID of the area for output file naming.
    """
    # from qgis.core import QgsProject
    # Definir las rutas de entrada y salida
    
    path_pro = QgsProject.instance().absolutePath() + '/'
    cluster_output_path = path_pro + f'agrupamientos{area_id}.gpkg'

    # Ejecutar el proceso de clustering DBSCAN
    processing.run("native:dbscanclustering", {
        'INPUT': input_path,
        'MIN_SIZE': min_size,
        'EPS': eps,
        'DBSCAN*': False,
        'FIELD_NAME': 'CLUSTER_ID',
        'SIZE_FIELD_NAME': 'CLUSTER_SIZE',
        'OUTPUT': cluster_output_path
    })
    
    return cluster_output_path


def create_buffer(area_id, output_layer_name, geometry_output_path, buffer_distance):
    """
    Creates a buffer layer around the specified geometry.
    
    Parameters:
    - area_id: ID of the area.
    - output_layer_name: Name of the output layer.
    - geometry_output_path: Path to the input geometry.
    - buffer_distance: Distance for the buffer.
    """
    path_pro = QgsProject.instance().absolutePath() + '/'
    buffer_output_path = path_pro + f'buf{area_id}.gpkg'
    
    processing.run("native:buffer", {
        'INPUT': geometry_output_path + f'|layername={output_layer_name}',
        'DISTANCE': buffer_distance,
        'SEGMENTS': 5,
        'END_CAP_STYLE': 0,
        'JOIN_STYLE': 0,
        'MITER_LIMIT': 2,
        'DISSOLVE': False,
        'OUTPUT': buffer_output_path
    })
    
    return buffer_output_path

def create_minimum_bounding_geometry(cluster_output_path, area_id, output_layer_name):
    """
    Creates the minimum bounding geometry for a given set of features.
    
    Parameters:
    - cluster_output_path: Path to the cluster output.
    - area_id: ID of the area.
    - output_layer_name: Name of the output layer.
    """
    path_pro = QgsProject.instance().absolutePath() + '/'
    geometry_output_path = path_pro + f'{output_layer_name}.gpkg'
    
    processing.run("qgis:minimumboundinggeometry", {
        'INPUT': cluster_output_path,
        'FIELD': 'CLUSTER_ID',
        'TYPE': 3,
        'OUTPUT': geometry_output_path
    })
    
    return geometry_output_path

# *******************************************************************************

def delete_fic(file):
    pass

def borra_capa_bien(nom_capa):
    """funcion para borrar capas y su gpkg"""

    try:
        a_borrar= nom_capa
        project = QgsProject.instance()
        
        path_salida = QgsProject.instance().absolutePath() + '/'  

        fic_salida  =  "{}{}.gpkg".format(path_salida,nom_capa) #'D:/QField\\export.gpkg'
        


        # obtener layer desde su nombre
        if QgsProject.instance().mapLayersByName(a_borrar):
            capas = QgsProject.instance().mapLayersByName(a_borrar)
            layer_a_borrar = capas[0]
            layer_a_borrar.dataProvider().reloadData()
        
        try:
            rsc = QgsProject.instance().removeMapLayer(layer_a_borrar.id())
            if QgsProject.instance().mapLayersByName(a_borrar):
                print(f"No se pudo eliminar la capa '{a_borrar}'.")
            else:
                print(f"La capa '{a_borrar}' fue eliminada exitosamente.")
            
        except:
            print("error eliminacion capa")
    except:
        print("error al borrar capa gpkg, o no existe ")


    try:
        if os.path.exists(fic_salida):
            os.remove(fic_salida)
    except:
        print("error al borrar fichero gpkg")   

def activarFeaturesCount(capa_activa):
    """Fuerza que se muestren el numero de features de la capa"""
    
    arbol_capas = QgsProject.instance().layerTreeRoot()
    nodo_capa = arbol_capas.findLayer(capa_activa.id())

    if nodo_capa is not None:
        nodo_capa.setCustomProperty("showFeatureCount", True)        

def Areas(area_id, layer_name, npun, dis, buf):
    """ Generalized function to process areas """
    try:
        path_pro = QgsProject.instance().absolutePath() + '/'  
        buffer_layer_name = f"{area_id} - {layer_name}_buf"
        output_layer_name = f"{area_id} - {layer_name}"
        cluster_layer_name = f"agrupamientos{area_id}"


        borra_capa_bien(buffer_layer_name)
        borra_capa_bien(output_layer_name)
        borra_capa_bien(cluster_layer_name)
        
        name_file = path_pro + f"agrupamientos{area_id}.gpkg "
        delete_fic(name_file)
        name_file = path_pro + f"buf{area_id}.gpkg "
        delete_fic(name_file)

        min_size = npun.text()
        eps = dis.text()
        buffer_distance = buf.text()

        input_path = f'D:/soroll/Pla Endreca/GlobalSoroll.gpkg|layername={layer_name}'

        # cluster_output_path = path_pro + f'agrupamientos{area_id}.gpkg'
        # processing.run("native:dbscanclustering", {
        #     'INPUT': input_path,
        #     'MIN_SIZE': min_size,
        #     'EPS': eps,
        #     'DBSCAN*': False,
        #     'FIELD_NAME': 'CLUSTER_ID',
        #     'SIZE_FIELD_NAME': 'CLUSTER_SIZE',
        #     'OUTPUT': cluster_output_path
        # })


        cluster_output_path = perform_dbscan_clustering(
            input_path,
            min_size,
            eps,
            area_id
        )


        # Usar la función del módulo para crear geometría mínima de contorno
        geometry_output_path = create_minimum_bounding_geometry(cluster_output_path, 
                                                                    area_id, 
                                                                    output_layer_name)

        alias = output_layer_name
        # layer = self.iface.addVectorLayer(geometry_output_path, alias, 'ogr')
        layer = QgsVectorLayer(geometry_output_path, alias, 'ogr')
        
        layer.startEditing()
        primer_elemento = next(layer.getFeatures())
        layer.deleteFeature(primer_elemento.id())
        layer.commitChanges()
        activarFeaturesCount(layer)

        # Usar la función del módulo para crear un buffer
        buffer_output_path = create_buffer(area_id, 
                                                output_layer_name, 
                                                geometry_output_path, 
                                                buffer_distance)

        buffer_alias = buffer_layer_name
        # buffer_layer = self.iface.addVectorLayer(buffer_output_path, buffer_alias, 'ogr')
        buffer_layer = QgsVectorLayer(buffer_output_path, buffer_alias, 'ogr')

        activarFeaturesCount(buffer_layer)
        borra_capa_bien(output_layer_name)
    except Exception as e:
        print(str(e))
        return None

# ******************************************************************************************

def prueba():
    print("modulo soroll_processing")

def proceso_test(txt):
    print(txt)
    params = {
        'INPUT':'D:/qVista/EndrecaSoroll/sorollIris.gpkg|layername=sorollIris',
        'MIN_SIZE':5,
        'EPS':1,
        'DBSCAN*':False,
        'FIELD_NAME':'CLUSTER_ID',
        'SIZE_FIELD_NAME':'CLUSTER_SIZE',
        'OUTPUT':'TEMPORARY_OUTPUT'
    }
    # if txt == "paso 2":
    #     params = {
    #         'INPUT':'D:/qVista/EndrecaSoroll/kksorollIris.gpkg|layername=sorollIris',
    #         'MIN_SIZE':5,
    #         'EPS':1,
    #         'DBSCAN*':False,
    #         'FIELD_NAME':'CLUSTER_ID',
    #         'SIZE_FIELD_NAME':'CLUSTER_SIZE',
    #         'OUTPUT':'TEMPORARY_OUTPUT'
    #     }
    res = processing.run("native:dbscanclustering", params)
    if res is not None:
        salida = res['OUTPUT']
        QgsProject.instance().addMapLayer(salida)
    # if txt == "paso 3":
    #     m = 3 / 0
    return res

def soroll_processing():
    try:
        res = proceso_test("paso 1")
        res = proceso_test("paso 2")
        res = proceso_test("paso 3")
        return res
    except Exception as e:
        print(str(e))
        return None

# ***************************************************************************************************

from .soroll_dialog import sorollDialog

def soroll_dialog_():

    dlg = None

    try:

        dlg = sorollDialog()

        dlg.setWindowFlags(Qt.WindowStaysOnTopHint)

        dlg.areas1.clicked.connect(lambda: Areas(
            area_id=1,
            layer_name="Mycellium",
            npun=dlg.npun1,
            dis=dlg.dis1,
            buf=dlg.buf1
        ))

        min_size1 = dlg.npun1.text()
        eps1 = dlg.dis1.text()
        buf1 = dlg.buf1.text()
        
        dlg.areas2.clicked.connect(lambda: Areas(
            area_id=2,
            layer_name="IrisSoroll",
            npun=dlg.npun2,
            dis=dlg.dis2,
            buf=dlg.buf2
        ))        

        min_size2 = dlg.npun2.text()
        eps2 = dlg.dis2.text()
        buf2 = dlg.buf2.text()

        dlg.areas3.clicked.connect(lambda: Areas(
            area_id=3,
            layer_name="DenunciesAlcoholCarrer",
            npun=dlg.npun3,
            dis=dlg.dis3,
            buf=dlg.buf3
        ))
        min_size3 = dlg.npun3.text()
        eps3 = dlg.dis3.text()
        buf3 = dlg.buf3.text()

        dlg.areas4.clicked.connect(lambda: Areas(
            area_id=4,
            layer_name="DenunciesSorollCarrer",
            npun=dlg.npun4,
            dis=dlg.dis4,
            buf=dlg.buf4
        )) 

        min_size4 = dlg.npun4.text()
        eps4 = dlg.dis4.text()  
        buf4 = dlg.buf4.text() 
        
        dlg.show()
        return dlg

    except Exception as e:
        print(str(e))
        if dlg is not None: dlg.hide()
        return None
