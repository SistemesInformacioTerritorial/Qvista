# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QDir, Qt, QUrl
from qgis.PyQt.QtGui import QPalette
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from qgis.PyQt.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget,QDialog)

class QvVideo(QDialog):

    def __init__(self, fileName='', xSize=800, ySize=600, parent=None):
        super(QvVideo, self).__init__(parent)

        self.fileName = fileName
        self.resize(xSize, ySize)
        self.setWindowTitle('Reproducció Video')
        #ombra_ = QvConstants.afegeixOmbraWidget(self)
        # self.openButton = QPushButton("Obrir...")
        # self.openButton.clicked.connect(self.openFile)

        # self.playButton = QPushButton()
        # self.playButton.setEnabled(False)
        # self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        # self.playButton.clicked.connect(self.play)

        # self.positionSlider = QSlider(Qt.Horizontal)
        # self.positionSlider.setRange(0, 0)
        # self.positionSlider.sliderMoved.connect(self.setPosition)

        # controlLayout = QHBoxLayout()
        # controlLayout.setContentsMargins(0, 0, 0, 0)
        # controlLayout.addWidget(self.openButton)
        # controlLayout.addWidget(self.playButton)
        # controlLayout.addWidget(self.positionSlider)

        videoWidget = QVideoWidget()
        #ombra_ = QvConstants.afegeixOmbraWidget(videoWidget)

        # videoWidget.setAttribute(Qt.WA_TranslucentBackground, True)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(videoWidget)
        # self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        # self.mediaPlayer.positionChanged.connect(self.positionChanged)
        # self.mediaPlayer.durationChanged.connect(self.durationChanged)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)

        if self.fileName != '':
            self.setWindowFlag(Qt.SplashScreen, True)
            self.setWindowFlag(Qt.FramelessWindowHint, True)
            # self.setBackgroundColor(Qt.white)
            self.open()
        else:
            layout.addLayout(controlLayout)

        self.setLayout(layout)
        self.resize(xSize, ySize)

    def setBackgroundColor(self, color): #???
        pal = QPalette()
        pal.setColor(QPalette.Background, color)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

    def openFile(self):
        try:
            f, _ = QFileDialog.getOpenFileName(self, "Arxiu de video", QDir.homePath())
        except:
            f = ''
        if f != '':
            print("troba l'arxiu de video")
            self.fileName = f
            self.open()
            self.play()

    def open(self):
        if self.fileName != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.fileName)))
            # self.mediaPlayer.resize(xSize, ySize)
            self.setWindowTitle('Reproducció Video - ' + self.fileName)
            # self.playButton.setEnabled(True)

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.openButton.setEnabled(False)
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.openButton.setEnabled(True)

    # def positionChanged(self, position):
    #     self.positionSlider.setValue(position)

    # def durationChanged(self, duration):
    #     self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

if __name__ == '__main__':

    from qgis.core.contextmanagers import qgisapp

    with qgisapp(sysexit=False) as app:

        # player = QvVideo()
        # player = QvVideo('C:/Users/Public/Videos/Sample Videos/Wildlife.wmv')
        
        player = QvVideo('D:/qVista/Codi/imatges/Spinner_2.gif', 128, 128)
        # player_ = QvConstants.afegeixOmbraWidget(player)
        #player.setModal(True)
        #player.activateWindow()
        player.mediaPlayer.play()
        player.show()
