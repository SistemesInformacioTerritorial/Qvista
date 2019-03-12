# -*- coding: utf-8 -*-

from qgis.PyQt.QtGui import QCursor, QIcon
from qgis.PyQt.QtWidgets import QMenu, QAction
from qgis.PyQt.QtWidgets import QMessageBox, QWhatsThis
# import images_rc
# import recursos

class QvAccions:
    def __init__(self):
        super().__init__()

        # Conjunto de acciones predefinidas
        self.accions = {}
        self.iniAccions()

    def accio(self, nom):
        if nom in self.accions:
            return self.accions[nom]
        else:
            return None

    def afegirAccio(self, nom, act):
        self.accions[nom] = act

    def _about(self):
        QMessageBox().information(None, 'Quant a', 'qVista - Versió 0.1')

    def iniAccions(self):
        act = QAction()
        act.setText('Quant a')
        act.triggered.connect(self._about)
        self.afegirAccio('about', act)

    def menuAccions(self, llistaAccions, accions = None, menuExtra = None):
        if QWhatsThis.inWhatsThisMode():
            return None
        if accions == None:
            accions = self.accions
        else:
            accions.update(self.accions)
        menu = QMenu()
        for nom in llistaAccions:
            if nom == 'separator':
                menu.addSeparator()
            elif nom in accions:
                menu.addAction(accions[nom])
        if menuExtra is not None:
            menu.addSeparator()
            menu.addMenu(menuExtra)

#     QList<QgsMapLayerAction *> mapLayerActions = QgsGui::mapLayerActionRegistry()->mapLayerActions( mLayer, QgsMapLayerAction::SingleFeature );
 
#    if ( !mapLayerActions.isEmpty() )
#    {
#      //add a separator between user defined and standard actions
#      addSeparator();
 
#      for ( int i = 0; i < mapLayerActions.size(); ++i )
#      {
#        QgsMapLayerAction *qaction = mapLayerActions.at( i );
 
#        if ( qaction->isEnabledOnlyWhenEditable() && ( mMode == QgsAttributeEditorContext::AddFeatureMode || mMode == QgsAttributeEditorContext::IdentifyMode ) )
#          continue;
 
#        QAction *qAction = new QAction( qaction->icon(), qaction->text(), this );
#        qAction->setData( QVariant::fromValue<ActionData>( ActionData( qaction, mFeatureId, mLayer ) ) );
#        addAction( qAction );
#        connect( qAction, &QAction::triggered, this, &QgsActionMenu::triggerAction );
#      }
#    }
 
        return menu

