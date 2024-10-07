#!/usr/bin/env python

# /home/tomash/poks/prog/python/GUI/.venv/bin/python

import sys
#from PySide2 import QtGui,QtCore,QtQuick
#from PySide2.QtWidgets import QApplication,QWidget,QLabel
from PySide2.QtWidgets import *
from PySide2 import QtCore

#QML_FILE = "01.qml"
#class MainWindow(QtQuick.QQuickView):
# 
#    def __init__(self, parent=None):
#        super(MainWindow, self).__init__(parent)
#        self.setTitle("QML Example @ PySide2")
##        self.setSource(QtCore.QUrl.fromLocalFile(QML_FILE))
#        self.setResizeMode(QtQuick.QQuickView.SizeRootObjectToView)

class MainWindow(QWidget):
    def __init__(self, app):
        super(MainWindow, self).__init__()
        self.app = app
        self.prepareGUI()
        
    def prepareGUI(self):
        self.setWindowTitle('Test1')
        self.resize(640,480)
        label = QLabel("HelloW", self).move(280,220)
        button = QPushButton("Butt", self)
        button.setToolTip("Close app")
#        button.clicked.connect(QtCore.QCoreApplication.instance().quit)
#        button.clicked.connect(self.app.quit)
        button.clicked.connect(self.close)
        
    def run(self):
        self.show()
        sys.exit(self.app.exec_())

    def close(self):
        self.app.quit()
    

def main():
    app = QApplication(sys.argv)
    MainWindow(app).run()
    

if __name__ == '__main__':
    main()
