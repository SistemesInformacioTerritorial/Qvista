# -*- coding: utf-8 -*-

import qgis.core as qgCor
import qgis.gui as qgGui
import qgis.utils as qgUts
import qgis.PyQt.QtWidgets as qtWdg
import qgis.PyQt.QtGui as qtGui
import qgis.PyQt.QtCore as qtCor
import qgis.PyQt.QtSql as qtSql

class singleton:

    def __init__(self, cls):
        self._cls = cls

    def instance(self, *args, **kwargs):
        if hasattr(self, '_instance'):
            return self._instance
        else:
            self._instance = self._cls(*args, **kwargs)
            return self._instance

    def __call__(self, *args, **kwargs):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)


@singleton        
class QvDigitizeWidget(qgGui.QgsAdvancedDigitizingDockWidget):

    def __init__(self, canvas, keys="Ctrl+4"):
        self.canvas = canvas
        super().__init__(self.canvas)
        self.setWindowTitle("Digitalització avançada")
        self.shortcut = qtWdg.QShortcut(qtGui.QKeySequence(keys), self.canvas)
        self.shortcut.activated.connect(self.toggleUserVisible)


class QvDigitizeFeature(qgGui.QgsMapToolDigitizeFeature):

    @classmethod
    def new(cls, layer, canvas):
        try:
            if layer.type() == qgCor.QgsMapLayerType.VectorLayer:
                if not layer.isEditable():
                    if not layer.startEditing():
                        return
                dig = cls(layer, canvas)
                dig.setNew()
        except Exception as e:
            print('Error QvDigitizeFeature.new: ' + str(e))

    def __init__(self, layer, canvas):
        self.layer = layer
        self.canvas = canvas
        self.widget = QvDigitizeWidget.instance(self.canvas)
        super().__init__(self.canvas, self.widget)
        self.setLayer(self.layer)

    def setNew(self):
        self.digitizingCompleted.connect(self.newFeature)
        self.digitizingFinished.connect(self.end)
        self.canvas.setMapTool(self)
        self.canvas.activateWindow()
        self.canvas.setFocus()

    def newFeature(self, feature):
        print('New feature')
        if self.isActive():
            self.canvas.unsetMapTool(self)
        if self.layer.isEditable():
            self.layer.rollBack()
        # ok = self.layer.commitChanges()
        # self.layer.commitErrors()
        # self.layer.rollBack()

    def end(self):
        if self.layer.isEditable():
            self.layer.rollBack()
        # self.widget.clear()
        # self.widget.hide()
        print('End')

if __name__ == "__main__":

    from qgis.core.contextmanagers import qgisapp
    from moduls.QvApp import QvApp
    from moduls.QvCanvas import QvCanvas
    from moduls.QvAtributs import QvAtributs
    from moduls.QvLlegenda import QvLlegenda
    import configuracioQvista as cfg

    with qgisapp(sysexit=False) as app:

        QvApp().carregaIdioma(app, 'ca')

        canvas = QvCanvas()
        atributos = QvAtributs(canvas)
        leyenda = QvLlegenda(canvas, atributos)

        # inicial = cfg.projecteInicial
        inicial = 'd:/temp/TestDigitize.qgs'
        leyenda.readProject(inicial)

        leyenda.setWindowTitle('Llegenda')
        # leyenda.setGeometry(50, 50, 400, 600)
        leyenda.show()

        canvas.setWindowTitle('Canvas - ' + inicial)
        # canvas.setGeometry(400, 50, 900, 600)
        canvas.show()

        atributos.setWindowTitle('Atributs')
        # atributos.setGeometry(50, 500, 1050, 250)
        leyenda.obertaTaulaAtributs.connect(atributos.show)

        # Acciones de usuario para el menú

        def testDigitize():
            print('ini test digitize')
            QvDigitizeFeature.new(leyenda.currentLayer(), canvas)
            print('fin test digitize')

        def writeProject():
            print('write file')
            leyenda.project.write()

        def openProject():
            dialegObertura = qtWdg.QFileDialog()
            dialegObertura.setDirectoryUrl(qtCor.QUrl('D:/Temp/'))
            mapes = "Tots els mapes acceptats (*.qgs *.qgz);; " \
                    "Mapes Qgis (*.qgs);;Mapes Qgis comprimits (*.qgz)"
            nfile, _ = dialegObertura.getOpenFileName(None, "Obrir mapa Qgis",
                                                      "D:/Temp/", mapes)
            if nfile != '':
                print('read file ' + nfile)
                ok = leyenda.readProject(nfile)
                if ok:
                    canvas.setWindowTitle('Canvas - ' + nfile)
                else:
                    print(leyenda.project.error().summary())

        act = qtWdg.QAction()
        act.setText("Test Digitize")
        act.triggered.connect(testDigitize)
        leyenda.accions.afegirAccio('testDigitize', act)

        act = qtWdg.QAction()
        act.setText("Desa projecte")
        act.triggered.connect(writeProject)
        leyenda.accions.afegirAccio('writeProject', act)

        act = qtWdg.QAction()
        act.setText("Obre projecte")
        act.triggered.connect(openProject)
        leyenda.accions.afegirAccio('openProject', act)

        # Adaptación del menú

        def menuContexte(tipo):
            if tipo == 'none':
                leyenda.menuAccions.append('separator')
                leyenda.menuAccions.append('writeProject')
                leyenda.menuAccions.append('openProject')
            elif tipo == 'layer':
                leyenda.menuAccions.append('separator')
                leyenda.menuAccions.append('testDigitize')


        # Conexión de la señal con la función menuContexte para personalizar el menú

        leyenda.clicatMenuContexte.connect(menuContexte)


# /***************************************************************************
#     qgsmaptooladdfeature.cpp
#     ------------------------
#     begin                : April 2007
#     copyright            : (C) 2007 by Marco Hugentobler
#     email                : marco dot hugentobler at karto dot baug dot ethz dot ch
#  ***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

# #include "qgsmaptooladdfeature.h"
# #include "qgsadvanceddigitizingdockwidget.h"
# #include "qgsapplication.h"
# #include "qgsattributedialog.h"
# #include "qgsexception.h"
# #include "qgscurvepolygon.h"
# #include "qgsfields.h"
# #include "qgsgeometry.h"
# #include "qgslinestring.h"
# #include "qgsmultipoint.h"
# #include "qgsmapcanvas.h"
# #include "qgsmapmouseevent.h"
# #include "qgspolygon.h"
# #include "qgsproject.h"
# #include "qgsvectordataprovider.h"
# #include "qgsvectorlayer.h"
# #include "qgslogger.h"
# #include "qgsfeatureaction.h"
# #include "qgisapp.h"
# #include "qgsexpressioncontextutils.h"
# #include "qgsrubberband.h"

# #include <QSettings>

# QgsMapToolAddFeature::QgsMapToolAddFeature( QgsMapCanvas *canvas, CaptureMode mode )
#   : QgsMapToolDigitizeFeature( canvas, QgisApp::instance()->cadDockWidget(), mode )
#   , mCheckGeometryType( true )
# {
#   setLayer( canvas->currentLayer() );

#   mToolName = tr( "Add feature" );
#   connect( QgisApp::instance(), &QgisApp::newProject, this, &QgsMapToolAddFeature::stopCapturing );
#   connect( QgisApp::instance(), &QgisApp::projectRead, this, &QgsMapToolAddFeature::stopCapturing );
# }

# bool QgsMapToolAddFeature::addFeature( QgsVectorLayer *vlayer, const QgsFeature &f, bool showModal )
# {
#   QgsFeature feat( f );
#   QgsExpressionContextScope *scope = QgsExpressionContextUtils::mapToolCaptureScope( snappingMatches() );
#   QgsFeatureAction *action = new QgsFeatureAction( tr( "add feature" ), feat, vlayer, QString(), -1, this );
#   if ( QgsRubberBand *rb = takeRubberBand() )
#     connect( action, &QgsFeatureAction::addFeatureFinished, rb, &QgsRubberBand::deleteLater );
#   bool res = action->addFeature( QgsAttributeMap(), showModal, scope );
#   if ( showModal )
#     delete action;
#   return res;
# }

# void QgsMapToolAddFeature::digitized( const QgsFeature &f )
# {
#   QgsVectorLayer *vlayer = currentVectorLayer();
#   bool res = addFeature( vlayer, f, false );

#   if ( res )
#   {
#     //add points to other features to keep topology up-to-date
#     bool topologicalEditing = QgsProject::instance()->topologicalEditing();
#     QgsProject::AvoidIntersectionsMode avoidIntersectionsMode = QgsProject::instance()->avoidIntersectionsMode();
#     if ( topologicalEditing && avoidIntersectionsMode == QgsProject::AvoidIntersectionsMode::AvoidIntersectionsLayers &&
#          ( mode() == CaptureLine || mode() == CapturePolygon ) )
#     {

#       //use always topological editing for avoidIntersection.
#       //Otherwise, no way to guarantee the geometries don't have a small gap in between.
#       const QList<QgsVectorLayer *> intersectionLayers = QgsProject::instance()->avoidIntersectionsLayers();

#       if ( !intersectionLayers.isEmpty() ) //try to add topological points also to background layers
#       {
#         for ( QgsVectorLayer *vl : intersectionLayers )
#         {
#           //can only add topological points if background layer is editable...
#           if ( vl->geometryType() == QgsWkbTypes::PolygonGeometry && vl->isEditable() )
#           {
#             vl->addTopologicalPoints( f.geometry() );
#           }
#         }
#       }
#     }
#     if ( topologicalEditing )
#     {
#       QList<QgsPointLocator::Match> sm = snappingMatches();
#       for ( int i = 0; i < sm.size() ; ++i )
#       {
#         if ( sm.at( i ).layer() )
#         {
#           sm.at( i ).layer()->addTopologicalPoints( f.geometry().vertexAt( i ) );
#         }
#       }
#       vlayer->addTopologicalPoints( f.geometry() );
#     }
#   }
# }
