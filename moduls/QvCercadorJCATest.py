from qgis.core import QgsPointXY
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QObject, pyqtSignal
from qgis.PyQt.QtWidgets import QCompleter
import sys
import csv
import collections

class MainWindow(QMainWindow):

def __init__(self):
    QMainWindow.__init__(self)

def customEvent(self, event):
    

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

protected:
    void customEvent(QEvent * event);

private:
    Ui::MainWindow *ui;

private slots:
    void on_lineEdit_textChanged(QString );
};
mainwindow.cpp:

class CompleteEvent : public QEvent
{
public:
    CompleteEvent(QLineEdit *lineEdit) : QEvent(QEvent::User), m_lineEdit(lineEdit) { }

    void complete()
    {
        m_lineEdit->completer()->complete();
    }

private:
    QLineEdit *m_lineEdit;
};

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    QStringList wordList;
    wordList << "one" << "two" << "three" << "four";

    QLineEdit *lineEdit = new QLineEdit(this);
    lineEdit->setGeometry(20, 20, 200, 30);
    connect(lineEdit, SIGNAL(textChanged(QString)), SLOT(on_lineEdit_textChanged(QString )));

    QCompleter *completer = new QCompleter(wordList, this);
    completer->setCaseSensitivity(Qt::CaseInsensitive);
    completer->setCompletionMode(QCompleter::UnfilteredPopupCompletion);
    lineEdit->setCompleter(completer);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::customEvent(QEvent * event)
{
    QMainWindow::customEvent(event);
    if (event->type()==QEvent::User)
        ((CompleteEvent*)event)->complete();
}

void MainWindow::on_lineEdit_textChanged(QString text)
{
    if (text.length()==0)
        QApplication::postEvent(this, new CompleteEvent((QLineEdit*)sender()));
}
class QvCercadorJCA(QObject):

    __carrersCSV = 'moduls\DadesBCN\CARRERER.csv'
    __numerosCSV = 'moduls\DadesBCN\TAULA_DIRELE.csv'
    sHanTrobatCoordenades = pyqtSignal()

    def __init__(self, lineEditCarrer, lineEditNumero, origen = 'CSV'):
        super().__init__()
        self.origen = origen
        self.leCarrer = lineEditCarrer
        self.leNumero = lineEditNumero
        self.connectarLineEdits()

        self.dictCarrers = {}
        self.dictNumeros = collections.defaultdict(dict)

        self.iniAdreca()
        if self.llegirAdreces():
            self.completarCarrer()

    def iniAdreca(self):
        self.iniAdrecaCarrer()
        self.iniAdrecaNumero()

    def iniAdrecaCarrer(self):
        self.nomCarrer = ''
        self.codiCarrer = ''

    def iniAdrecaNumero(self):
        self.numeroCarrer = ''
        self.coordAdreca = None
        self.infoAdreca = None

    def connectarLineEdits(self):
        self.leCarrer.editingFinished.connect(self.trobatCarrer)
        self.leCarrer.returnPressed.connect(self.focusANumero)
        self.leCarrer.textChanged.connect(self.esborrarNumero)
        self.leNumero.editingFinished.connect(self.trobatNumero)

    def llegirAdreces(self):
        if self.origen == 'CSV':
            ok = self.llegirAdrecesCSV()
        elif self.origen == 'ORACLE':
            ok = self.llegirAdrecesOracle()
        else:
            ok = False
        return ok

    def llegirAdrecesOracle(self):
        #
        # TODO - Lectura datos de direcciones de Oracle
        #
        return False

    def llegirAdrecesCSV(self):
        try:
            with open(self.__carrersCSV, encoding='utf-8', newline='') as csvFile:
                reader = csv.DictReader(csvFile, delimiter=',')
                for row in reader:
                    self.dictCarrers[row['NOM_OFICIAL']] = row['CODI_VIA']

            with open(self.__numerosCSV, encoding='utf-8', newline='') as csvFile:
                reader = csv.DictReader(csvFile, delimiter=',')
                for row in reader:
                    self.dictNumeros[row['CODI_CARRER']][row['NUMPOST']] = row
            return True
        except:
            print('QCercadorAdreca.llegirAdrecesCSV(): ', sys.exc_info()[0], sys.exc_info()[1])
            return False

    def completarCarrer(self):
        completer = QCompleter(self.dictCarrers, self.leCarrer)
        completer.setFilterMode(QtCore.Qt.MatchContains)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.leCarrer.setCompleter(completer)   

    def completarNumero(self):
        self.dictNumerosFiltre = self.dictNumeros[self.codiCarrer]
        completer = QCompleter(self.dictNumerosFiltre, self.leNumero)
        completer.setFilterMode(QtCore.Qt.MatchStartsWith)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.leNumero.setCompleter(completer)  

    def trobatNumero(self):
        txt = self.leNumero.text()
        if txt != '': # and txt != self.numeroCarrer:
            self.iniAdrecaNumero()
            if self.nomCarrer != '' and txt in self.dictNumerosFiltre:
                self.numeroCarrer = txt
                self.infoAdreca = self.dictNumerosFiltre[self.numeroCarrer]
                self.coordAdreca = QgsPointXY(float(self.infoAdreca['ETRS89_COORD_X']), \
                                            float(self.infoAdreca['ETRS89_COORD_Y']))
                self.leNumero.clearFocus()
                self.sHanTrobatCoordenades.emit()

    def focusANumero(self):
        self.leNumero.setFocus()

    def esborrarNumero(self):
        self.leNumero.clear()
        self.leNumero.setCompleter(None)


from importaciones import *


def llegirAdrecesCSV():
    try:
        with open(carrersCSV, encoding='utf-8', newline='') as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            for row in reader:
                dictCarrers[row['NOM_OFICIAL']] = row['CODI_VIA']

        with open(numerosCSV, encoding='utf-8', newline='') as csvFile:
            reader = csv.DictReader(csvFile, delimiter=',')
            for row in reader:
                dictNumeros[row['CODI_CARRER']][row['NUMPOST']] = row
        return True
    except:
        print('QCercadorAdreca.llegirAdrecesCSV(): ', sys.exc_info()[0], sys.exc_info()[1])
        return False


carrersCSV = 'moduls\DadesBCN\CARRERER.csv'
numerosCSV = 'moduls\DadesBCN\TAULA_DIRELE.csv'
dictCarrers = {}
dictNumeros = collections.defaultdict(dict)
global carrerTrobat
carrerTrobat = False
global segueixo
segueixo = False
global longi
longi = 0
global completer

def trobatCarrer():
    global carrerTrobat
    global completer
    global segueixo

    segueixo = True
    le1.setText(completer.currentCompletion())
    global longi
    longi = len(completer.currentCompletion())
    txt = le1.text()
    # if txt != '' and txt != self.nomCarrer:
    #     self.iniAdreca()
    #     if txt in self.dictCarrers:
    #         self.nomCarrer = txt
    #         self.codiCarrer = self.dictCarrers[self.nomCarrer]
    #         self.completarNumero()
    # else:
    print("Trobat: "+txt, completer.currentIndex(), completer.currentRow())
    carrerTrobat = True

def textTipat():
    global longi
    global completer
    global carrerTrobat
    global segueixo

    print (completer.completionPrefix())

    if carrerTrobat:        
        completer = QCompleter(dictCarrers, le1)
        completer.setFilterMode(QtCore.Qt.MatchContains)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setWrapAround(True)
        completer.setWidget(le1)
        le1.setCompleter(completer) 
        carrerTrobat = False
    if segueixo:
        print(longi)
        posi = longi +1
        textTallat = le1.text()[posi:]
        print(textTallat)
        completer.setCompletionPrefix(textTallat)
        le1.completer().complete()

    print (completer.currentCompletion())
    


if __name__ == "__main__":
    projecteInicial='projectes/BCN11_nord.qgs'

    with qgisapp() as app:
        app.setStyle(QStyleFactory.create('fusion'))

        le1 = QLineEdit()
        llegirAdrecesCSV()

        completer = QCompleter(dictCarrers, le1)
        completer.setFilterMode(QtCore.Qt.MatchContains)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setWrapAround(True)
        completer.setWidget(le1)

        le1.setCompleter(completer) 
        le1.textChanged.connect(textTipat)
        le1.returnPressed.connect(trobatCarrer)
        le1.show()