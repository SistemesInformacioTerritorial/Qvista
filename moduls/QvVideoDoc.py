from PyQt5.QtWidgets import (QApplication, QMainWindow, QDockWidget, QTreeWidget,
                             QTreeWidgetItem, QTextBrowser, QVBoxLayout, QWidget,
                             QPushButton, QLabel, QLineEdit)
from PyQt5.QtCore import Qt, QUrl
import webbrowser
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

import json
import sys

class QvVideoDoc(QWidget):
    def __init__(self, parent=None):
        super(QvVideoDoc, self).__init__(parent=parent)

        try:
            from pathlib import Path
            with open('Documentacio/Vídeos/videos.json', 'r') as f:
                self.video_data = json.load(f)
        except FileNotFoundError:
            print("L'arxiu videos.json no s'ha trobat.")
            self.video_data = {}
        except json.JSONDecodeError as e:
            print(f"Error en decodificar l'arxiu JSON: {repr(e)}")
            self.video_data = {}

        self.setupUi()

    
    def setupUi(self):
        self.layout = QVBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self.on_item_clicked)

        self.text_browser = QTextBrowser()

        self.view_button = QPushButton("Visualitzar Vídeo")
        self.view_button.clicked.connect(self.view_video)
        self.view_button.setEnabled(False)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Cercar...")
        self.search_box.textChanged.connect(self.filter_tree)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.hide()
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._on_image_loaded)


        self.layout.addWidget(self.search_box)
        self.layout.addWidget(self.tree)
        self.layout.addWidget(self.text_browser)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.view_button)

        self.setLayout(self.layout)
        self.current_video_info = None

        # Deixem que s'estiri només l'arbre
        self.layout.setStretchFactor(self.search_box, 0)
        self.layout.setStretchFactor(self.tree, 1)
        self.layout.setStretchFactor(self.text_browser, 0)
        self.layout.setStretchFactor(self.view_button, 0)

        self.fill_tree()

    def fill_tree(self):
        self.tree.clear()
        for group, videos in self.video_data.items():
            group_item = QTreeWidgetItem([group])
            for video in videos.keys():
                video_item = QTreeWidgetItem([video])
                group_item.addChild(video_item)
            self.tree.addTopLevelItem(group_item)
        self.tree.expandAll()

    def filter_tree(self):
        query = self.search_box.text().lower().split()
        self.tree.clear()

        for group, videos in self.video_data.items():
            group_item = QTreeWidgetItem([group])
            
            for video_name, video_info in videos.items():
                # Comprovem que totes les paraules de la consulta apareguin en algun dels camps
                if all(any(word in video_info[field].lower() for field in ["titol", "descripcio", "tags"]) for word in query):
                    video_item = QTreeWidgetItem([video_name])
                    group_item.addChild(video_item)

            if not group_item.childCount() == 0:
                self.tree.addTopLevelItem(group_item)
        
        self.tree.expandAll()


    def on_item_clicked(self, item, column):
        if item.parent() is None:
            return

        group = item.parent().text(0)
        video = item.text(0)
        
        video_info = self.video_data.get(group, {}).get(video, {})
        self.text_browser.clear()
        self.text_browser.append(f"Titol: {video_info.get('titol', '')}")
        self.text_browser.append(f"Descripcio: {video_info.get('descripcio', '')}")
        self.text_browser.append(f"Tags: {video_info.get('tags', '')}")

        thumbnail_url = video_info.get('thumbnail', None)
        if thumbnail_url:
            self._load_image(thumbnail_url)
        else:
            self.image_label.hide()

        self.current_video_info = video_info
        self.view_button.setEnabled(True)

        self.adjust_text_browser_height()

    def adjust_text_browser_height(self):
        document_height = self.text_browser.document().size().height()
        self.text_browser.setMinimumHeight(document_height + 10)
        self.text_browser.setMaximumHeight(document_height + 10)

    def _load_image(self, url):
        self.network_manager.get(QNetworkRequest(QUrl(url)))

    def _on_image_loaded(self, reply):
        data = reply.readAll()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        width = max(250, self.width())
        height = pixmap.height()*width//pixmap.width()
        scaled_pixmap = pixmap.scaled(width, 200, Qt.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.show()


    def view_video(self):
        if self.current_video_info is None:
            return

        url = self.current_video_info.get("url", "")
        if url:
            webbrowser.open(url)


if __name__=='__main__':
    app = QApplication([])
    window = QMainWindow()

    dock = QDockWidget("Informació dels Vídeos", window)
    dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

    tree = QvVideoDoc()
    dock.setWidget(tree)
    window.addDockWidget(Qt.LeftDockWidgetArea, dock)

    window.show()

    sys.exit(app.exec_())
